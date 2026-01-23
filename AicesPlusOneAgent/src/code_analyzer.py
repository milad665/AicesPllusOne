"""
Code Analysis Service Client

Client for interacting with the code analysis service API.
"""

import os
import httpx
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import ssl

load_dotenv()


class CodeAnalyzer:
    """Client for the code analysis service"""
    
    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize the code analyzer client.
        
        Args:
            base_url: Base URL for the code analysis API (Default)
        """
        self.default_base_url = base_url or os.getenv(
            "CODE_ANALYSIS_API_URL",
            "https://aices-plus-one-analyzer-691085128403.europe-west1.run.app"
        )
        # Main client for default operations (or legacy mode)
        self.client = httpx.AsyncClient(base_url=self.default_base_url, timeout=30.0)
        
        # Cache for tenant-specific clients
        self.tenant_clients: Dict[str, httpx.AsyncClient] = {}

    async def _get_client(self, tenant_config=None) -> httpx.AsyncClient:
        """
        Get an HTTP client configured for a specific tenant or return default.
        """
        if not tenant_config:
            return self.client
            
        # Create a unique key for caching based on URL and mTLS settings
        config_key = f"{tenant_config.url}:{tenant_config.use_mtls}:{tenant_config.client_cert_path}"
        
        if config_key in self.tenant_clients:
            return self.tenant_clients[config_key]
            
        # Build new client
        kwargs = {"base_url": tenant_config.url, "timeout": 30.0}
        
        if tenant_config.use_mtls and tenant_config.client_cert_path and tenant_config.client_key_path:
            # Configure SSL Context
            ssl_context = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH)
            if tenant_config.ca_cert_path:
                ssl_context.load_verify_locations(tenant_config.ca_cert_path)
            
            ssl_context.load_cert_chain(
                certfile=tenant_config.client_cert_path, 
                keyfile=tenant_config.client_key_path
            )
            kwargs["verify"] = ssl_context
            # Note: httpx 'cert' arg is also an option but 'verify' with context is more robust for custom CA
            # For simplicity with httpx:
            # kwargs["cert"] = (tenant_config.client_cert_path, tenant_config.client_key_path)
            # kwargs["verify"] = tenant_config.ca_cert_path if tenant_config.ca_cert_path else True

        new_client = httpx.AsyncClient(**kwargs)
        self.tenant_clients[config_key] = new_client
        return new_client

    async def get_repositories(self, tenant_config=None) -> List[Dict[str, Any]]:
        """Get all repository configurations"""
        client = await self._get_client(tenant_config)
        response = await client.get("/repositories")
        response.raise_for_status()
        return response.json()
    
    async def get_projects(self, tenant_config=None) -> List[Dict[str, Any]]:
        """Get all projects with metadata"""
        client = await self._get_client(tenant_config)
        response = await client.get("/projects")
        response.raise_for_status()
        return response.json()
    
    async def get_project(self, project_id: str, tenant_config=None) -> Dict[str, Any]:
        """Get a specific project's metadata"""
        client = await self._get_client(tenant_config)
        response = await client.get(f"/projects/{project_id}")
        response.raise_for_status()
        return response.json()
    
    async def get_project_entrypoints(self, project_id: str, tenant_config=None) -> List[Dict[str, Any]]:
        """Get entry points for a specific project"""
        client = await self._get_client(tenant_config)
        response = await client.get(f"/projects/{project_id}/entrypoints")
        response.raise_for_status()
        return response.json()
    
    async def close(self):
        """Close all HTTP clients"""
        await self.client.aclose()
        for client in self.tenant_clients.values():
            await client.aclose()
        self.tenant_clients.clear()
