from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from ..schemas import C4Architecture

class StorageProvider(ABC):
    """Abstract base class for C4 architecture storage providers."""

    @abstractmethod
    def save(self, architecture: C4Architecture) -> None:
        """Save C4 architecture to storage."""
        pass

    @abstractmethod
    def load(self) -> Optional[C4Architecture]:
        """Load C4 architecture from storage."""
        pass

    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """Get metadata about the stored architecture."""
        pass
