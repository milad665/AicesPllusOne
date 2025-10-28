#!/bin/bash

# Install Tree-sitter language parsers
# This script helps install the required language parsers for Tree-sitter

echo "Installing Tree-sitter language parsers..."

# Create a temporary directory for building
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"

# Function to build and install a language parser
build_parser() {
    local lang=$1
    local repo_url=$2
    
    echo "Building $lang parser..."
    
    if ! git clone "$repo_url" "$lang"; then
        echo "Failed to clone $lang parser repository"
        return 1
    fi
    
    cd "$lang"
    
    # Most Tree-sitter parsers have a similar build process
    if [ -f "Makefile" ]; then
        make
    elif [ -f "binding.gyp" ]; then
        npm install
    elif [ -f "Cargo.toml" ]; then
        cargo build --release
    fi
    
    cd ..
}

# Build language parsers (if needed)
# Note: Most parsers are now available as pip packages, so this is mainly for reference

echo "Tree-sitter language parsers are installed via pip packages:"
echo "- tree-sitter-python"
echo "- tree-sitter-javascript" 
echo "- tree-sitter-typescript"
echo "- tree-sitter-java"
echo "- tree-sitter-cpp"
echo "- tree-sitter-go"
echo "- tree-sitter-rust"
echo "- tree-sitter-c-sharp"

echo "These should be installed automatically with: pip install -r requirements.txt"

# Cleanup
cd ..
rm -rf "$TEMP_DIR"

echo "Language parser setup complete!"
