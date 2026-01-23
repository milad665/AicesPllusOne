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

    def __init__(self, bucket_name: Optional[str] = None):
        self.bucket_name = bucket_name or os.getenv("GCS_BUCKET_NAME")
        
        if not self.bucket_name:
            raise ValueError("GCS_BUCKET_NAME is required for GCSStorage")
            
        self.client = storage.Client()
        self.bucket = self.client.bucket(self.bucket_name)

    def _get_blob(self, tenant_id: str):
        """Get blob for specific tenant."""
        blob_name = f"{tenant_id}/c4_architecture.json"
        return self.bucket.blob(blob_name)

    def save(self, architecture: C4Architecture, tenant_id: str = "default") -> None:
        """Save to GCS."""
        # Get existing metadata if possible, or create new
        try:
            current_data = self._load_raw(tenant_id)
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
        
        blob = self._get_blob(tenant_id)
        blob.upload_from_string(
            json.dumps(data, indent=2),
            content_type="application/json"
        )

    def load(self, tenant_id: str = "default") -> Optional[C4Architecture]:
        """Load from GCS."""
        try:
            data = self._load_raw(tenant_id)
            arch_data = data.get("c4_architecture")
            if arch_data is None:
                return None
            return C4Architecture(**arch_data)
        except Exception:
            return None

    def get_metadata(self, tenant_id: str = "default") -> Dict[str, Any]:
        try:
            data = self._load_raw(tenant_id)
            return data.get("metadata", {})
        except Exception:
            return {}

    def _load_raw(self, tenant_id: str) -> Dict[str, Any]:
        """Download and parse JSON from GCS."""
        blob = self._get_blob(tenant_id)
        if not blob.exists():
            return {}
        content = blob.download_as_text()
        return json.loads(content)
