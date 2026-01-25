from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import List, Dict, Optional
import asyncio
import logging
import json
import os
from pathlib import Path
from datetime import datetime

from .models import RepositoryConfig, ProjectInfo, EntryPoint, SyncStatus
from .database import DatabaseManager
from .git_manager import GitManager, RepositorySyncScheduler
from .tree_sitter_analyzer import TreeSitterAnalyzer
from .config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize components
app = FastAPI(
    title="Git Repository Manager",
    description="Manages git repositories and extracts project metadata using Tree-sitter",
    version="1.0.0"
)

db_manager = DatabaseManager(Config.DATABASE_PATH)
git_manager = GitManager(repos_dir=Config.REPOSITORIES_DIR, db_manager=db_manager)
analyzer = TreeSitterAnalyzer()
scheduler = RepositorySyncScheduler(git_manager, interval_minutes=Config.SYNC_INTERVAL_MINUTES)

# Store for project metadata cache
projects_cache: Dict[str, ProjectInfo] = {}
entry_points_cache: Dict[str, List[EntryPoint]] = {}
last_analysis_time: Optional[datetime] = None


@app.on_event("startup")
async def startup_event():
    """Initialize the application"""
    await db_manager.initialize()
    await scheduler.start()
    
    # Load Repositories from Environment Variables if provided
    try:
        env_repos = json.loads(Config.GIT_REPOSITORIES)
        if env_repos:
            logger.info(f"Found {len(env_repos)} repositories in environment variables")
            
            # Resolve Global SSH Key
            global_private_key = Config.GIT_SSH_KEY
            if not global_private_key and Config.GIT_SSH_KEY_PATH and os.path.exists(Config.GIT_SSH_KEY_PATH):
                with open(Config.GIT_SSH_KEY_PATH, 'r') as f:
                    global_private_key = f.read()
            
            global_public_key = Config.GIT_SSH_PUBLIC_KEY
            
            # Upsert Repositories
            existing_repos = await db_manager.get_repositories()
            existing_names = {r.name for r in existing_repos}
            
            for repo_data in env_repos:
                name = repo_data.get("name")
                url = repo_data.get("url")
                
                if not name or not url:
                    logger.warning(f"Skipping invalid repo config: {repo_data}")
                    continue
                    
                if name in existing_names:
                    logger.info(f"Repository {name} already exists in DB, skipping.")
                    continue
                
                # Determine SSH Key (Per-repo overrides or Global)
                # Assuming JSON might have 'ssh_key' field, else global
                private_key = repo_data.get("ssh_private_key", global_private_key)
                public_key = repo_data.get("ssh_public_key", global_public_key)
                
                if not private_key:
                    logger.warning(f"No SSH key found for {name} (global or local), using empty string (might fail if auth needed)")
                    private_key = ""
                    public_key = ""

                new_repo = RepositoryConfig(
                    name=name,
                    url=url,
                    ssh_private_key=private_key,
                    ssh_public_key=public_key,
                    default_branch=repo_data.get("default_branch", "main")
                )
                
                await db_manager.add_repository(new_repo)
                logger.info(f"Added repository {name} from environment")
                
            # Trigger initial Sync
            asyncio.create_task(git_manager.sync_all_repositories())
            asyncio.create_task(analyze_repositories())
            
    except json.JSONDecodeError:
        logger.error("Failed to parse GIT_REPOSITORIES environment variable. Must be valid JSON.")
    except Exception as e:
        logger.error(f"Error loading environment repositories: {e}")

    logger.info("Application started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown"""
    await scheduler.stop()
    logger.info("Application shutdown complete")


async def analyze_repositories():
    """Analyze all repositories and update cache"""
    global projects_cache, entry_points_cache, last_analysis_time
    
    try:
        projects_cache.clear()
        entry_points_cache.clear()
        
        repositories = await db_manager.get_repositories()
        
        for repo_config in repositories:
            repo_path = git_manager._get_repo_path(repo_config)
            
            if not repo_path.exists():
                continue
            
            # Analyze the repository
            project_info = analyzer.analyze_project(repo_path, repo_config.name)
            entry_points = analyzer.extract_entry_points(repo_path)
            
            # Update entry points count
            project_info.entry_points_count = len(entry_points)
            
            # Cache the results
            projects_cache[project_info.id] = project_info
            entry_points_cache[project_info.id] = entry_points
        
        last_analysis_time = datetime.now()
        logger.info(f"Analyzed {len(projects_cache)} projects")
        
    except Exception as e:
        logger.error(f"Error analyzing repositories: {e}")


@app.post("/repositories", response_model=Dict[str, int])
async def add_repository(repo_config: RepositoryConfig, background_tasks: BackgroundTasks):
    """Add a new repository configuration"""
    try:
        repo_id = await db_manager.add_repository(repo_config)
        
        # Trigger immediate sync for the new repository
        repo_config.id = repo_id
        background_tasks.add_task(git_manager.clone_or_pull_repository, repo_config)
        background_tasks.add_task(analyze_repositories)
        
        return {"repository_id": repo_id}
    
    except Exception as e:
        logger.error(f"Error adding repository: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/repositories", response_model=List[RepositoryConfig])
async def get_repositories():
    """Get all repository configurations"""
    try:
        repositories = await db_manager.get_repositories()
        # Remove sensitive SSH keys from response
        for repo in repositories:
            repo.ssh_private_key = "***HIDDEN***"
            repo.ssh_public_key = "***HIDDEN***"
        return repositories
    
    except Exception as e:
        logger.error(f"Error getting repositories: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/repositories/{repo_id}")
async def delete_repository(repo_id: int):
    """Delete a repository configuration"""
    try:
        repo_config = await db_manager.get_repository(repo_id)
        if not repo_config:
            raise HTTPException(status_code=404, detail="Repository not found")
        
        # Delete from database
        deleted = await db_manager.delete_repository(repo_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Repository not found")
        
        # Clean up local files
        git_manager.cleanup_repository(repo_config.name)
        
        # Update cache
        await analyze_repositories()
        
        return {"message": "Repository deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting repository: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/repositories/{repo_id}/sync-status", response_model=Optional[SyncStatus])
async def get_sync_status(repo_id: int):
    """Get synchronization status for a repository"""
    try:
        status = await db_manager.get_sync_status(repo_id)
        return status
    
    except Exception as e:
        logger.error(f"Error getting sync status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/repositories/sync")
async def sync_repositories(background_tasks: BackgroundTasks):
    """Manually trigger synchronization of all repositories"""
    try:
        background_tasks.add_task(git_manager.sync_all_repositories)
        background_tasks.add_task(analyze_repositories)
        return {"message": "Repository synchronization started"}
    
    except Exception as e:
        logger.error(f"Error triggering sync: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/projects", response_model=List[ProjectInfo])
async def get_projects():
    """Get all projects with metadata"""
    try:
        # Check if cache needs refresh
        if not projects_cache or (last_analysis_time and 
                                 (datetime.now() - last_analysis_time).total_seconds() > 3600):
            await analyze_repositories()
        
        return list(projects_cache.values())
    
    except Exception as e:
        logger.error(f"Error getting projects: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/projects/{project_id}", response_model=ProjectInfo)
async def get_project(project_id: str):
    """Get a specific project's metadata"""
    try:
        if project_id not in projects_cache:
            await analyze_repositories()
        
        if project_id not in projects_cache:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return projects_cache[project_id]
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting project: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/projects/{project_id}/entrypoints", response_model=List[EntryPoint])
async def get_project_entrypoints(project_id: str):
    """Get entry points for a specific project"""
    try:
        if project_id not in entry_points_cache:
            await analyze_repositories()
        
        if project_id not in entry_points_cache:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return entry_points_cache[project_id]
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting entry points: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "projects_count": len(projects_cache),
        "last_analysis": last_analysis_time.isoformat() if last_analysis_time else None
    }


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Git Repository Manager",
        "version": "1.0.0",
        "description": "Manages git repositories and extracts project metadata using Tree-sitter",
        "endpoints": {
            "repositories": "/repositories",
            "projects": "/projects",
            "health": "/health",
            "docs": "/docs"
        }
    }
