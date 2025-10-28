"""
Code Analysis Service Client

Client for interacting with the code analysis service API.
"""

import os
import httpx
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()


class CodeAnalyzer:
    """Client for the code analysis service"""
    
    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize the code analyzer client
        
        Args:
            base_url: Base URL for the code analysis API
        """
        self.base_url = base_url or os.getenv(
            "CODE_ANALYSIS_API_URL",
            "https://aices-plus-one-analyzer-691085128403.europe-west1.run.app"
        )
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=30.0)
    
    async def get_repositories(self) -> List[Dict[str, Any]]:
        """
        Get all repository configurations
        
        Returns:
            List of repository configurations
        """
        response = await self.client.get("/repositories")
        response.raise_for_status()
        return response.json()
    
    async def get_projects(self) -> List[Dict[str, Any]]:
        """
        Get all projects with metadata
        
        Returns:
            List of projects with their metadata
        """
        response = await self.client.get("/projects")
        response.raise_for_status()
        return response.json()
    
    async def get_project(self, project_id: str) -> Dict[str, Any]:
        """
        Get a specific project's metadata
        
        Args:
            project_id: The project identifier
            
        Returns:
            Project metadata
        """
        response = await self.client.get(f"/projects/{project_id}")
        response.raise_for_status()
        return response.json()
    
    async def get_project_entrypoints(self, project_id: str) -> List[Dict[str, Any]]:
        """
        Get entry points for a specific project
        
        Args:
            project_id: The project identifier
            
        Returns:
            List of entry points for the project
        """
        response = await self.client.get(f"/projects/{project_id}/entrypoints")
        response.raise_for_status()
        return response.json()
    
    async def get_sync_status(self, repo_id: int) -> Optional[Dict[str, Any]]:
        """
        Get synchronization status for a repository
        
        Args:
            repo_id: The repository ID
            
        Returns:
            Sync status information or None
        """
        response = await self.client.get(f"/repositories/{repo_id}/sync-status")
        response.raise_for_status()
        return response.json()
    
    async def sync_repositories(self) -> Dict[str, Any]:
        """
        Manually trigger synchronization of all repositories
        
        Returns:
            Sync result
        """
        response = await self.client.post("/repositories/sync")
        response.raise_for_status()
        return response.json()
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
