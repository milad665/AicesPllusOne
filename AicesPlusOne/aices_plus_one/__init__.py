"""
Git Repository Manager

A Python application that manages multiple git repositories and provides 
API endpoints for project metadata extraction using Tree-sitter.
"""

__version__ = "1.0.0"

# Core components (avoid importing agent.py which depends on Google SDK)
from .api import app
from .models import *
from .database import DatabaseManager
from .git_manager import GitManager
from .tree_sitter_analyzer import TreeSitterAnalyzer
