import json
import os
from typing import Optional, Dict, Any
from datetime import datetime
from google.cloud import storage
from ..schemas import C4Architecture
from .base import StorageProvider

class GCSStorage(StorageProvider):
    """
    Google Cloud Storage (GCS) implementation for C4 Architecture.
    Stores data in a JSON blob within a bucket.
    """

    def __init__(self, bucket_name: Optional[str] = None, blob_name: str = "c4_architecture.json"):
        self.bucket_name = bucket_name or os.getenv("GCS_BUCKET_NAME")
        self.blob_name = blob_name
        
        if not self.bucket_name:
            raise ValueError("GCS_BUCKET_NAME is required for GCSStorage")
            
        self.client = storage.Client()
        self.bucket = self.client.bucket(self.bucket_name)
        self.blob = self.bucket.blob(self.blob_name)

    def save(self, architecture: C4Architecture) -> None:
        """Save to GCS."""
        # Get existing metadata if possible, or create new
        try:
            current_data = self._load_raw()
            metadata = current_data.get("metadata", {})
        except Exception:
             metadata = {
                "created_at": datetime.utcnow().isoformat(),
                "version": "1.0.0"
            }

        metadata["updated_at"] = datetime.utcnow().isoformat()
        
        data = {
            "c4_architecture": architecture.model_dump(mode='json'),
            "metadata": metadata
        }
        
        self.blob.upload_from_string(
            json.dumps(data, indent=2),
            content_type="application/json"
        )

    def load(self) -> Optional[C4Architecture]:
        """Load from GCS."""
        try:
            data = self._load_raw()
            arch_data = data.get("c4_architecture")
            if arch_data is None:
                return None
            return C4Architecture(**arch_data)
        except Exception:
            return None

    def get_metadata(self) -> Dict[str, Any]:
        try:
            data = self._load_raw()
            return data.get("metadata", {})
        except Exception:
            return {}

    def _load_raw(self) -> Dict[str, Any]:
        """Download and parse JSON from GCS."""
        if not self.blob.exists():
            return {}
        content = self.blob.download_as_text()
        return json.loads(content)
