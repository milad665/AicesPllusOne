from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime


class RepositoryConfig(BaseModel):
    """Configuration for a git repository"""
    id: Optional[int] = None
    name: str
    url: str
    ssh_private_key: str
    ssh_public_key: str
    default_branch: str = "main"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ProjectLanguage(str, Enum):
    """Supported programming languages"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    CPP = "cpp"
    C = "c"
    GO = "go"
    RUST = "rust"
    CSHARP = "csharp"
    UNKNOWN = "unknown"


class ProjectType(str, Enum):
    """Project types"""
    WEB_APP = "web_app"
    API = "api"
    CLI = "cli"
    LIBRARY = "library"
    MICROSERVICE = "microservice"
    MOBILE_APP = "mobile_app"
    DESKTOP_APP = "desktop_app"
    UNKNOWN = "unknown"


class EntryPoint(BaseModel):
    """Entry point information"""
    name: str
    file_path: str
    line_number: int
    type: str  # function, class, method, etc.
    parameters: List[str] = []
    return_type: Optional[str] = None
    documentation: Optional[str] = None


class ProjectInfo(BaseModel):
    """Project metadata"""
    id: str
    name: str
    repository_name: str
    language: ProjectLanguage
    project_type: ProjectType
    description: Optional[str] = None
    version: Optional[str] = None
    dependencies: List[str] = []
    file_count: int = 0
    lines_of_code: int = 0
    last_updated: datetime
    entry_points_count: int = 0


class SyncStatus(BaseModel):
    """Repository synchronization status"""
    repository_id: int
    last_sync: Optional[datetime] = None
    status: str  # success, error, in_progress
    error_message: Optional[str] = None
    commits_ahead: int = 0
    current_commit: Optional[str] = None
