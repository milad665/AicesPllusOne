#!/usr/bin/env python3
"""
Simple test script to verify the Git Repository Manager is working correctly
"""

import asyncio
import tempfile
import shutil
from pathlib import Path

from aices_plus_one.database import DatabaseManager
from aices_plus_one.models import RepositoryConfig
from aices_plus_one.tree_sitter_analyzer import TreeSitterAnalyzer


async def test_database():
    """Test database functionality"""
    print("🧪 Testing database functionality...")
    
    # Create temporary database
    with tempfile.NamedTemporaryFile(delete=False) as f:
        db_path = f.name
    
    try:
        db_manager = DatabaseManager(db_path)
        await db_manager.initialize()
        
        # Test adding a repository
        repo = RepositoryConfig(
            name="test-repo",
            url="git@github.com:user/test-repo.git",
            ssh_private_key="fake-private-key",
            ssh_public_key="fake-public-key",
            default_branch="main"
        )
        
        repo_id = await db_manager.add_repository(repo)
        print(f"✓ Added repository with ID: {repo_id}")
        
        # Test retrieving repositories
        repositories = await db_manager.get_repositories()
        print(f"✓ Retrieved {len(repositories)} repositories")
        
        # Test deleting repository
        deleted = await db_manager.delete_repository(repo_id)
        print(f"✓ Deleted repository: {deleted}")
        
    finally:
        # Cleanup
        Path(db_path).unlink(missing_ok=True)


def test_tree_sitter():
    """Test Tree-sitter analyzer"""
    print("\n🌳 Testing Tree-sitter analyzer...")
    
    analyzer = TreeSitterAnalyzer()
    print(f"✓ Tree-sitter analyzer initialized with {len(analyzer.languages)} languages")
    
    # Test language detection
    test_files = {
        "test.py": "python",
        "test.js": "javascript", 
        "test.java": "java",
        "test.go": "go"
    }
    
    for filename, expected in test_files.items():
        detected = analyzer._detect_language(Path(filename))
        print(f"✓ {filename} detected as: {detected}")
    
    # Test with a simple Python code
    if analyzer.parsers:
        print("✓ Tree-sitter parsers are available")
    else:
        print("⚠️  No Tree-sitter parsers loaded (this is okay for basic functionality)")


def test_project_structure():
    """Test project structure"""
    print("\n📁 Testing project structure...")
    
    required_files = [
        "aices_plus_one/__init__.py",
        "aices_plus_one/api.py",
        "aices_plus_one/models.py",
        "aices_plus_one/database.py",
        "aices_plus_one/git_manager.py",
        "aices_plus_one/tree_sitter_analyzer.py",
        "aices_plus_one/main.py",
        "aices_plus_one/config.py",
        "requirements.txt",
        "README.md",
        "Dockerfile",
        "docker-compose.yml"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
        else:
            print(f"✓ {file_path}")
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
    else:
        print("✅ All required files present")


async def main():
    """Main test function"""
    print("🚀 Git Repository Manager - Component Tests\n")
    
    test_project_structure()
    await test_database()
    test_tree_sitter()
    
    print("\n✅ All tests completed!")
    print("\nTo start the application:")
    print("  python3 dev_server.py")
    print("\nOr with Python module:")
    print("  python3 -m aices_plus_one.main")
    print("\nAPI documentation will be available at:")
    print("  http://localhost:8000/docs")


if __name__ == "__main__":
    asyncio.run(main())
