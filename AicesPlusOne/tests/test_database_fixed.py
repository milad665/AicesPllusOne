import pytest
import pytest_asyncio
import asyncio
from pathlib import Path
import tempfile
import shutil
from aices_plus_one.database import DatabaseManager
from aices_plus_one.models import RepositoryConfig


@pytest_asyncio.fixture
async def db_manager():
    """Create a temporary database manager for testing"""
    with tempfile.NamedTemporaryFile(delete=False) as f:
        db_path = f.name
    
    manager = DatabaseManager(db_path)
    await manager.initialize()
    
    yield manager
    
    # Cleanup
    Path(db_path).unlink(missing_ok=True)


@pytest.mark.asyncio
async def test_add_repository(db_manager):
    """Test adding a repository configuration"""
    repo = RepositoryConfig(
        name="test-repo",
        url="git@github.com:user/test-repo.git",
        ssh_private_key="fake-private-key",
        ssh_public_key="fake-public-key",
        default_branch="main"
    )
    
    repo_id = await db_manager.add_repository(repo)
    assert repo_id is not None
    assert isinstance(repo_id, int)


@pytest.mark.asyncio
async def test_get_repositories(db_manager):
    """Test retrieving repository configurations"""
    # Add a test repository
    repo = RepositoryConfig(
        name="test-repo",
        url="git@github.com:user/test-repo.git",
        ssh_private_key="fake-private-key",
        ssh_public_key="fake-public-key",
        default_branch="main"
    )
    
    repo_id = await db_manager.add_repository(repo)
    
    # Retrieve repositories
    repositories = await db_manager.get_repositories()
    assert len(repositories) == 1
    assert repositories[0].name == "test-repo"
    assert repositories[0].id == repo_id


@pytest.mark.asyncio
async def test_delete_repository(db_manager):
    """Test deleting a repository configuration"""
    # Add a test repository
    repo = RepositoryConfig(
        name="test-repo",
        url="git@github.com:user/test-repo.git",
        ssh_private_key="fake-private-key",
        ssh_public_key="fake-public-key",
        default_branch="main"
    )
    
    repo_id = await db_manager.add_repository(repo)
    
    # Delete the repository
    deleted = await db_manager.delete_repository(repo_id)
    assert deleted is True
    
    # Verify it's gone
    repositories = await db_manager.get_repositories()
    assert len(repositories) == 0
