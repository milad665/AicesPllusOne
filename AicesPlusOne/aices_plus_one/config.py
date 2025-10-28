import os
from pathlib import Path


class Config:
    """Application configuration"""
    
    # Database settings
    DATABASE_PATH = os.getenv("DATABASE_PATH", "repositories.db")
    
    # Repository settings
    REPOSITORIES_DIR = os.getenv("REPOSITORIES_DIR", "repositories")
    
    # Synchronization settings
    SYNC_INTERVAL_MINUTES = int(os.getenv("SYNC_INTERVAL_MINUTES", "5"))
    
    # API settings
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))
    
    # Security settings
    SSH_KEYS_DIR = os.getenv("SSH_KEYS_DIR", "/tmp/git_ssh_keys")
    
    # Analysis settings
    CACHE_REFRESH_HOURS = int(os.getenv("CACHE_REFRESH_HOURS", "1"))
    MAX_DEPENDENCIES = int(os.getenv("MAX_DEPENDENCIES", "50"))
    
    # Logging settings
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def create_directories(cls):
        """Create necessary directories"""
        Path(cls.REPOSITORIES_DIR).mkdir(exist_ok=True)
        Path(cls.SSH_KEYS_DIR).mkdir(exist_ok=True, mode=0o700)
