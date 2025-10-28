#!/usr/bin/env python3
"""
Setup script for the Git Repository Manager
"""

import sys
import subprocess
import os
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return result
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed:")
        print(f"Command: {command}")
        print(f"Error: {e.stderr}")
        return None


def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major != 3 or version.minor < 8:
        print(f"✗ Python 3.8+ is required. You have Python {version.major}.{version.minor}")
        return False
    print(f"✓ Python {version.major}.{version.minor} is compatible")
    return True


def install_dependencies():
    """Install Python dependencies"""
    commands = [
        ("pip install --upgrade pip", "Upgrading pip"),
        ("pip install -r requirements.txt", "Installing dependencies"),
        ("pip install -r tests/requirements.txt", "Installing test dependencies"),
    ]
    
    for command, description in commands:
        if not run_command(command, description):
            return False
    return True


def setup_directories():
    """Create necessary directories"""
    directories = [
        "repositories",
        "data",
        ".ssh_keys",
        "logs"
    ]
    
    for directory in directories:
        path = Path(directory)
        path.mkdir(exist_ok=True)
        print(f"✓ Created directory: {directory}")


def run_tests():
    """Run the test suite"""
    print("\nRunning tests...")
    result = run_command("python -m pytest tests/ -v", "Running test suite")
    return result is not None


def main():
    """Main setup function"""
    print("🚀 Setting up Git Repository Manager...")
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("✗ Failed to install dependencies")
        sys.exit(1)
    
    # Setup directories
    setup_directories()
    
    # Copy environment file
    env_example = Path(".env.example")
    env_file = Path(".env")
    
    if env_example.exists() and not env_file.exists():
        env_file.write_text(env_example.read_text())
        print("✓ Created .env file from .env.example")
    
    # Run tests
    if not run_tests():
        print("⚠️  Some tests failed, but setup completed")
    else:
        print("✓ All tests passed!")
    
    print("\n🎉 Setup completed successfully!")
    print("\nTo start the application:")
    print("  python dev_server.py")
    print("\nTo run in production:")
    print("  python -m aices_plus_one.main")
    print("\nTo use Docker:")
    print("  docker-compose up")
    print("\nAPI documentation will be available at:")
    print("  http://localhost:8000/docs")


if __name__ == "__main__":
    main()
