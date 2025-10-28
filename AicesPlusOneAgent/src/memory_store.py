"""
Memory Store for C4 Architecture

Implements persistent storage for C4 architecture using ADK-style memory patterns.
This provides long-term persistence for the C4 architecture diagrams.
"""

import json
import os
from pathlib import Path
from typing import Optional
from datetime import datetime
from dotenv import load_dotenv

from .schemas import C4Architecture

load_dotenv()


class MemoryStore:
    """
    Persistent memory store for C4 Architecture
    
    This implements a simple file-based memory store that follows
    the ADK Memory pattern for long-term storage.
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize the memory store
        
        Args:
            storage_path: Path to the JSON file for storage
        """
        self.storage_path = Path(
            storage_path or os.getenv("MEMORY_STORE_PATH", "./data/memory.json")
        )
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize storage file if it doesn't exist
        if not self.storage_path.exists():
            self._init_storage()
    
    def _init_storage(self):
        """Initialize empty storage file"""
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
    
    def save_architecture(self, architecture: C4Architecture) -> None:
        """
        Save C4 architecture to memory
        
        Args:
            architecture: The C4 architecture to save
        """
        data = self._load_storage()
        data["c4_architecture"] = architecture.model_dump(mode='json')
        data["metadata"]["updated_at"] = datetime.utcnow().isoformat()
        
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_architecture(self) -> Optional[C4Architecture]:
        """
        Load C4 architecture from memory
        
        Returns:
            The stored C4 architecture or None if not found
        """
        data = self._load_storage()
        arch_data = data.get("c4_architecture")
        
        if arch_data is None:
            return None
        
        return C4Architecture(**arch_data)
    
    def _load_storage(self) -> dict:
        """Load the entire storage file"""
        with open(self.storage_path, 'r') as f:
            return json.load(f)
    
    def clear(self):
        """Clear all stored architecture data"""
        self._init_storage()
    
    def get_metadata(self) -> dict:
        """Get metadata about the stored architecture"""
        data = self._load_storage()
        return data.get("metadata", {})
