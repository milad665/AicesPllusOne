import os
import tempfile
import asyncio
import git
from git import Repo
from pathlib import Path
import shutil
from typing import Dict, List, Optional
from datetime import datetime
import logging
from .models import RepositoryConfig, SyncStatus
from .database import DatabaseManager

logger = logging.getLogger(__name__)


class GitManager:
    """Manages git repository operations"""
    
    def __init__(self, repos_dir: str = "repositories", db_manager: DatabaseManager = None):
        self.repos_dir = Path(repos_dir)
        self.repos_dir.mkdir(exist_ok=True)
        self.db_manager = db_manager
        self._ssh_keys_dir = Path(tempfile.gettempdir()) / "git_ssh_keys"
        self._ssh_keys_dir.mkdir(exist_ok=True)
    
    def _setup_ssh_key(self, repo_config: RepositoryConfig) -> str:
        """Setup SSH key for repository access"""
        key_file = self._ssh_keys_dir / f"key_{repo_config.id}"
        
        # Ensure the SSH key has proper line endings and format
        ssh_key = repo_config.ssh_private_key.strip()
        
        # Check if key looks valid
        if not ssh_key.startswith("-----BEGIN"):
            raise ValueError("SSH private key must start with -----BEGIN")
        
        if not ssh_key.endswith("-----"):
            raise ValueError("SSH private key must end with -----")
        
        # Ensure proper line endings
        lines = ssh_key.split('\n')
        properly_formatted_lines = []
        
        for line in lines:
            line = line.strip()
            if line:  # Skip empty lines
                properly_formatted_lines.append(line)
        
        # Reconstruct the key with proper formatting
        formatted_key = '\n'.join(properly_formatted_lines) + '\n'
        
        with open(key_file, 'w') as f:
            f.write(formatted_key)
        os.chmod(key_file, 0o600)
        
        # Validate the key format using ssh-keygen
        try:
            import subprocess
            result = subprocess.run(['ssh-keygen', '-l', '-f', str(key_file)], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"SSH key validation failed: {result.stderr}")
                raise ValueError(f"Invalid SSH key format: {result.stderr}")
            else:
                logger.info(f"SSH key validated successfully: {result.stdout.strip()}")
        except FileNotFoundError:
            logger.warning("ssh-keygen not found, skipping key validation")
        except Exception as e:
            logger.warning(f"Could not validate SSH key: {e}")
        
        logger.debug(f"Created SSH key file: {key_file}")
        return str(key_file)
    
    def _get_repo_path(self, repo_config: RepositoryConfig) -> Path:
        """Get local path for repository"""
        return self.repos_dir / repo_config.name
    
    async def clone_or_pull_repository(self, repo_config: RepositoryConfig) -> SyncStatus:
        """Clone or pull a repository"""
        status = SyncStatus(repository_id=repo_config.id, status="in_progress")
        ssh_key_file = None
        
        try:
            repo_path = self._get_repo_path(repo_config)
            ssh_key_file = self._setup_ssh_key(repo_config)
            
            # Setup SSH command with better options
            ssh_cmd = f'ssh -i {ssh_key_file} -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR'
            
            logger.info(f"Attempting to sync repository {repo_config.name} from {repo_config.url}")
            logger.debug(f"Using SSH command: {ssh_cmd}")
            
            if repo_path.exists():
                # Repository exists, pull latest changes
                logger.info(f"Repository {repo_config.name} exists, pulling latest changes...")
                repo = Repo(repo_path)
                origin = repo.remotes.origin
                
                # Configure SSH for git
                with repo.git.custom_environment(GIT_SSH_COMMAND=ssh_cmd):
                    origin.pull(repo_config.default_branch)
                
                current_commit = repo.head.commit.hexsha
                status.current_commit = current_commit
                logger.info(f"Successfully pulled repository {repo_config.name}, commit: {current_commit[:7]}")
            else:
                # Clone repository
                logger.info(f"Cloning repository {repo_config.name}...")
                env = {'GIT_SSH_COMMAND': ssh_cmd}
                logger.debug(f"Cloning from {repo_config.url} to {repo_path}")
                
                repo = Repo.clone_from(
                    repo_config.url,
                    repo_path,
                    branch=repo_config.default_branch,
                    env=env
                )
                current_commit = repo.head.commit.hexsha
                status.current_commit = current_commit
                logger.info(f"Successfully cloned repository {repo_config.name}, commit: {current_commit[:7]}")
            
            status.status = "success"
            status.last_sync = datetime.now()
            
        except Exception as e:
            status.status = "error"
            status.error_message = str(e)
            status.last_sync = datetime.now()
            logger.error(f"Error syncing repository {repo_config.name}: {e}")
        
        finally:
            # Clean up SSH key file
            if ssh_key_file and os.path.exists(ssh_key_file):
                try:
                    os.remove(ssh_key_file)
                    logger.debug(f"Cleaned up SSH key file: {ssh_key_file}")
                except Exception as e:
                    logger.warning(f"Failed to clean up SSH key file {ssh_key_file}: {e}")
        
        # Update status in database
        if self.db_manager:
            await self.db_manager.update_sync_status(status)
        
        return status
    
    async def sync_all_repositories(self) -> List[SyncStatus]:
        """Sync all configured repositories"""
        if not self.db_manager:
            return []
        
        repositories = await self.db_manager.get_repositories()
        results = []
        
        for repo_config in repositories:
            try:
                status = await self.clone_or_pull_repository(repo_config)
                results.append(status)
            except Exception as e:
                logger.error(f"Failed to sync repository {repo_config.name}: {e}")
                status = SyncStatus(
                    repository_id=repo_config.id,
                    status="error",
                    error_message=str(e),
                    last_sync=datetime.now()
                )
                results.append(status)
        
        return results
    
    def get_local_repositories(self) -> List[Path]:
        """Get list of local repository paths"""
        return [p for p in self.repos_dir.iterdir() if p.is_dir() and (p / '.git').exists()]
    
    def cleanup_repository(self, repo_name: str):
        """Remove local repository directory"""
        repo_path = self.repos_dir / repo_name
        if repo_path.exists():
            shutil.rmtree(repo_path)
            logger.info(f"Cleaned up repository {repo_name}")


class RepositorySyncScheduler:
    """Schedules periodic repository synchronization"""
    
    def __init__(self, git_manager: GitManager, interval_minutes: int = 5):
        self.git_manager = git_manager
        self.interval_minutes = interval_minutes
        self._running = False
        self._task = None
    
    async def start(self):
        """Start the synchronization scheduler"""
        if self._running:
            return
        
        self._running = True
        self._task = asyncio.create_task(self._sync_loop())
        logger.info(f"Started repository sync scheduler (interval: {self.interval_minutes} minutes)")
    
    async def stop(self):
        """Stop the synchronization scheduler"""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Stopped repository sync scheduler")
    
    async def _sync_loop(self):
        """Main synchronization loop"""
        while self._running:
            try:
                logger.info("Starting scheduled repository synchronization")
                results = await self.git_manager.sync_all_repositories()
                
                success_count = sum(1 for r in results if r.status == "success")
                error_count = sum(1 for r in results if r.status == "error")
                
                logger.info(f"Sync completed: {success_count} successful, {error_count} errors")
                
            except Exception as e:
                logger.error(f"Error in sync loop: {e}")
            
            # Wait for next interval
            await asyncio.sleep(self.interval_minutes * 60)
