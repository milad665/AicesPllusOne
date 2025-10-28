#!/usr/bin/env python3
"""
Quick start script for C4 Architecture Agent

This script helps you get started quickly by:
1. Checking prerequisites
2. Setting up environment
3. Running a simple test
"""

import os
import sys
from pathlib import Path


def check_python_version():
    """Check if Python version is adequate"""
    print("🔍 Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 10:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} (need 3.10+)")
        return False


def check_env_file():
    """Check if .env file exists"""
    print("\n🔍 Checking environment configuration...")
    env_file = Path(".env")
    if env_file.exists():
        print("   ✅ .env file found")
        return True
    else:
        print("   ⚠️  .env file not found")
        print("   Creating from template...")
        try:
            import shutil
            shutil.copy(".env.example", ".env")
            print("   ✅ Created .env from .env.example")
            print("   ⚠️  Please edit .env and add your GOOGLE_API_KEY")
            return False
        except Exception as e:
            print(f"   ❌ Error creating .env: {e}")
            return False


def check_dependencies():
    """Check if dependencies are installed"""
    print("\n🔍 Checking dependencies...")
    try:
        import google.generativeai
        print("   ✅ google-generativeai installed")
    except ImportError:
        print("   ❌ google-generativeai not installed")
        print("   Run: pip install -r requirements.txt")
        return False
    
    try:
        import mcp
        print("   ✅ mcp installed")
    except ImportError:
        print("   ❌ mcp not installed")
        print("   Run: pip install -r requirements.txt")
        return False
    
    try:
        import httpx
        print("   ✅ httpx installed")
    except ImportError:
        print("   ❌ httpx not installed")
        print("   Run: pip install -r requirements.txt")
        return False
    
    return True


def check_api_key():
    """Check if API key is configured"""
    print("\n🔍 Checking API key configuration...")
    
    # Try to load from .env
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key and api_key != "your-gemini-api-key-here":
        print("   ✅ GOOGLE_API_KEY is configured")
        return True
    else:
        print("   ❌ GOOGLE_API_KEY not configured")
        print("   Please edit .env and set your API key")
        print("   Get one at: https://makersuite.google.com/app/apikey")
        return False


def create_data_directory():
    """Create data directory if it doesn't exist"""
    print("\n🔍 Setting up data directory...")
    data_dir = Path("data")
    if not data_dir.exists():
        data_dir.mkdir(parents=True)
        print("   ✅ Created data/ directory")
    else:
        print("   ✅ data/ directory exists")
    return True


def main():
    """Main setup function"""
    print("=" * 60)
    print("C4 Architecture Agent - Quick Start")
    print("=" * 60)
    
    all_ok = True
    
    # Check Python version
    if not check_python_version():
        all_ok = False
    
    # Check environment file
    env_ok = check_env_file()
    
    # Check dependencies
    if not check_dependencies():
        all_ok = False
        print("\n📦 Installing dependencies...")
        print("   Run: pip install -r requirements.txt")
    
    # Check API key
    if env_ok and not check_api_key():
        all_ok = False
    
    # Create data directory
    create_data_directory()
    
    print("\n" + "=" * 60)
    if all_ok:
        print("✅ All checks passed! You're ready to go.")
        print("\n📚 Next steps:")
        print("   1. Test the agent: python cli.py")
        print("   2. Run examples: python examples.py")
        print("   3. Start MCP server: python src/server.py")
        print("\n📖 Documentation:")
        print("   - README.md - Project overview")
        print("   - SETUP.md - Detailed setup guide")
        print("   - ADK_DOCUMENTATION.md - ADK concepts")
    else:
        print("⚠️  Some checks failed. Please fix the issues above.")
        print("\n📖 See SETUP.md for detailed instructions")
    print("=" * 60)


if __name__ == "__main__":
    main()
