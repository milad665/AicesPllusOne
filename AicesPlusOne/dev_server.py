#!/usr/bin/env python3
"""
Development server script for the Git Repository Manager
"""

import uvicorn
import logging
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from aices_plus_one.config import Config
from aices_plus_one.main import main

if __name__ == "__main__":
    # Create necessary directories
    Config.create_directories()
    
    # Configure logging for development
    logging.basicConfig(
        level=getattr(logging, Config.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("Starting Git Repository Manager in development mode...")
    print(f"API will be available at: http://{Config.API_HOST}:{Config.API_PORT}")
    print(f"API documentation at: http://{Config.API_HOST}:{Config.API_PORT}/docs")
    
    # Start the development server
    main()
