#!/usr/bin/env python3
"""
MCP Server Launcher for C4 Architecture Agent

Usage:
    python start_server.py

This script starts the MCP server and handles proper logging and error handling.
"""
import os
import sys
import logging
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from src.server import main


def setup_logging():
    """Setup logging configuration"""
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stderr),
            logging.FileHandler('mcp_server.log')
        ]
    )


def check_environment():
    """Check if required environment variables are set"""
    required_vars = ["GOOGLE_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set them in your .env file or environment.")
        sys.exit(1)


def main_launcher():
    """Main launcher function"""
    print("Starting C4 Architecture MCP Server...")
    print("Server name: c4-architecture-agent")
    print("Version: 1.0.0")
    print("Protocol: MCP (Model Context Protocol)")
    print("Communication: JSON-RPC over stdio")
    print("")
    
    # Setup logging
    setup_logging()
    
    # Check environment
    check_environment()
    
    # Print ready message
    print("Server is ready. Listening for MCP requests on stdin...")
    print("To stop the server, send EOF (Ctrl+D on Unix/Linux/macOS, Ctrl+Z on Windows)")
    print("=" * 60)
    
    # Start the actual server
    main()


if __name__ == "__main__":
    main_launcher()