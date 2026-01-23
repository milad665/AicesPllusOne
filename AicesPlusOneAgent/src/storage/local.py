import json
import os
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
from ..schemas import C4Architecture
from .base import StorageProvider

class LocalStorage(StorageProvider):
    """
    Local file system storage for C4 Architecture.
    Stores data in a single JSON file.
    """
    
    def __init__(self, root_dir: Optional[str] = None):
        self.root_dir = Path(
            root_dir or os.getenv("STORAGE_ROOT", "data")
        )
        self.root_dir.mkdir(parents=True, exist_ok=True)
        
    def _get_tenant_path(self, tenant_id: str) -> Path:
        """Get path to tenant's storage file"""
        tenant_dir = self.root_dir / tenant_id
        tenant_dir.mkdir(parents=True, exist_ok=True)
        return tenant_dir / "c4_architecture.json"

    def _init_storage(self, file_path: Path):
        """Initialize empty storage file."""
        initial_data = {
            "c4_architecture": None,
            "metadata": {
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "version": "1.0.0"
            }
        }
        with open(file_path, 'w') as f:
            json.dump(initial_data, f, indent=2)

    def _load_raw(self, tenant_id: str) -> Dict[str, Any]:
        """Load raw JSON data for tenant."""
        path = self._get_tenant_path(tenant_id)
        if not path.exists():
            self._init_storage(path)
            
        with open(path, 'r') as f:
            return json.load(f)

    def save(self, architecture: C4Architecture, tenant_id: str = "default") -> None:
        """Save architecture for specific tenant."""
        data = self._load_raw(tenant_id)
        data["c4_architecture"] = architecture.model_dump(mode='json')
        data["metadata"]["updated_at"] = datetime.utcnow().isoformat()
        
        path = self._get_tenant_path(tenant_id)
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)

    def load(self, tenant_id: str = "default") -> Optional[C4Architecture]:
        """Load architecture for specific tenant."""
        data = self._load_raw(tenant_id)
        arch_data = data.get("c4_architecture")
        
        if arch_data is None:
            return None
        
        return C4Architecture(**arch_data)

    def get_metadata(self, tenant_id: str = "default") -> Dict[str, Any]:
        data = self._load_raw(tenant_id)
        return data.get("metadata", {})
