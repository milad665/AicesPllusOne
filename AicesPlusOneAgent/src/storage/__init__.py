from .base import StorageProvider
from .local import LocalStorage
from .gcs import GCSStorage

def get_storage_provider(type: str = "local", **kwargs) -> StorageProvider:
    if type.lower() == "gcs":
        return GCSStorage(**kwargs)
    return LocalStorage(**kwargs)
