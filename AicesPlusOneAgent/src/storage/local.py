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
    
    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = Path(
            storage_path or os.getenv("MEMORY_STORE_PATH", "./data/memory.json")
        )
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        if not self.storage_path.exists():
            self._init_storage()
    
    def _init_storage(self):
        """Initialize empty storage file."""
        initial_data = {
            "c4_architecture": None,
            "metadata": {
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "version": "1.0.0"
            }
        }
        with open(self.storage_path, 'w') as f:
            json.dump(initial_data, f, indent=2)
    
    def _load_raw(self) -> Dict[str, Any]:
        """Load raw JSON data."""
        with open(self.storage_path, 'r') as f:
            return json.load(f)

    def save(self, architecture: C4Architecture) -> None:
        data = self._load_raw()
        data["c4_architecture"] = architecture.model_dump(mode='json')
        data["metadata"]["updated_at"] = datetime.utcnow().isoformat()
        
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)

    def load(self) -> Optional[C4Architecture]:
        data = self._load_raw()
        arch_data = data.get("c4_architecture")
        
        if arch_data is None:
            return None
        
        return C4Architecture(**arch_data)

    def get_metadata(self) -> Dict[str, Any]:
        data = self._load_raw()
        return data.get("metadata", {})
