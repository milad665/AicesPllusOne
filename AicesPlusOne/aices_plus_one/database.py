import asyncio
import aiosqlite
from typing import List, Optional
from .models import RepositoryConfig, SyncStatus
import json
from datetime import datetime


class DatabaseManager:
    """Database manager for repository configurations and sync status"""
    
    def __init__(self, db_path: str = "repositories.db"):
        self.db_path = db_path
    
    async def initialize(self):
        """Initialize database tables"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS repositories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    url TEXT NOT NULL,
                    ssh_private_key TEXT NOT NULL,
                    ssh_public_key TEXT NOT NULL,
                    default_branch TEXT DEFAULT 'main',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS sync_status (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    repository_id INTEGER,
                    last_sync TIMESTAMP,
                    status TEXT NOT NULL,
                    error_message TEXT,
                    commits_ahead INTEGER DEFAULT 0,
                    current_commit TEXT,
                    FOREIGN KEY (repository_id) REFERENCES repositories (id)
                )
            """)
            
            await db.commit()
    
    async def add_repository(self, repo: RepositoryConfig) -> int:
        """Add a new repository configuration"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                INSERT INTO repositories (name, url, ssh_private_key, ssh_public_key, default_branch)
                VALUES (?, ?, ?, ?, ?)
            """, (repo.name, repo.url, repo.ssh_private_key, repo.ssh_public_key, repo.default_branch))
            
            repo_id = cursor.lastrowid
            await db.commit()
            return repo_id
    
    async def get_repositories(self) -> List[RepositoryConfig]:
        """Get all repository configurations"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT * FROM repositories")
            rows = await cursor.fetchall()
            
            repositories = []
            for row in rows:
                repo = RepositoryConfig(
                    id=row['id'],
                    name=row['name'],
                    url=row['url'],
                    ssh_private_key=row['ssh_private_key'],
                    ssh_public_key=row['ssh_public_key'],
                    default_branch=row['default_branch'],
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
                    updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None
                )
                repositories.append(repo)
            
            return repositories
    
    async def get_repository(self, repo_id: int) -> Optional[RepositoryConfig]:
        """Get a specific repository configuration"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT * FROM repositories WHERE id = ?", (repo_id,))
            row = await cursor.fetchone()
            
            if row:
                return RepositoryConfig(
                    id=row['id'],
                    name=row['name'],
                    url=row['url'],
                    ssh_private_key=row['ssh_private_key'],
                    ssh_public_key=row['ssh_public_key'],
                    default_branch=row['default_branch'],
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
                    updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None
                )
            return None
    
    async def delete_repository(self, repo_id: int) -> bool:
        """Delete a repository configuration"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("DELETE FROM repositories WHERE id = ?", (repo_id,))
            await db.execute("DELETE FROM sync_status WHERE repository_id = ?", (repo_id,))
            await db.commit()
            return cursor.rowcount > 0
    
    async def update_sync_status(self, status: SyncStatus):
        """Update synchronization status for a repository"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO sync_status 
                (repository_id, last_sync, status, error_message, commits_ahead, current_commit)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                status.repository_id,
                status.last_sync.isoformat() if status.last_sync else None,
                status.status,
                status.error_message,
                status.commits_ahead,
                status.current_commit
            ))
            await db.commit()
    
    async def get_sync_status(self, repo_id: int) -> Optional[SyncStatus]:
        """Get synchronization status for a repository"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM sync_status WHERE repository_id = ? ORDER BY last_sync DESC LIMIT 1",
                (repo_id,)
            )
            row = await cursor.fetchone()
            
            if row:
                return SyncStatus(
                    repository_id=row['repository_id'],
                    last_sync=datetime.fromisoformat(row['last_sync']) if row['last_sync'] else None,
                    status=row['status'],
                    error_message=row['error_message'],
                    commits_ahead=row['commits_ahead'],
                    current_commit=row['current_commit']
                )
            return None
