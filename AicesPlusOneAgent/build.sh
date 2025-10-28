#!/usr/bin/env bash
# Build script for C4 Architecture MCP Server

set -e

echo "🏗️  Building C4 Architecture MCP Server..."
echo "==========================================="

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found. Please run this script from the project root."
    exit 1
fi

# Check Python version
echo "🐍 Checking Python version..."
python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
echo "   Python version: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
    echo "   Virtual environment created at .venv/"
else
    echo "📦 Using existing virtual environment..."
fi

# Set up Python executable path
PYTHON_EXE=".venv/bin/python"

# Upgrade pip
echo "⬆️  Upgrading pip..."
$PYTHON_EXE -m pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
$PYTHON_EXE -m pip install -r requirements.txt

# Compile all Python files to check for syntax errors
echo "🔍 Checking syntax..."
$PYTHON_EXE -m py_compile src/*.py

# Run tests
echo "🧪 Running tests..."
$PYTHON_EXE test_server.py

# Make scripts executable
echo "🔧 Setting permissions..."
chmod +x start_server.py

# Check environment file
echo "🔧 Checking environment configuration..."
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "   Please edit .env and set your GOOGLE_API_KEY"
else
    echo "   .env file exists ✓"
fi

# Check if GOOGLE_API_KEY is set
if grep -q "your-gemini-api-key-here" .env 2>/dev/null; then
    echo "⚠️  Warning: Please set your actual GOOGLE_API_KEY in .env file"
fi

# Create data directory if it doesn't exist
echo "📁 Creating data directory..."
mkdir -p data

echo ""
echo "✅ Build completed successfully!"
echo ""
echo "🚀 To start the MCP server:"
echo "   python start_server.py"
echo ""
echo "📚 For more information, see:"
echo "   - MCP_SERVER_README.md"
echo "   - README.md"
echo ""
echo "🔧 Don't forget to:"
echo "   1. Set GOOGLE_API_KEY in .env file"
echo "   2. Configure your MCP client (Claude Desktop, etc.)"
echo "==========================================="