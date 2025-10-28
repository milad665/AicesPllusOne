# C4 Architecture MCP Server

A Model Context Protocol (MCP) server that generates C4 architecture diagrams from code analysis using AI.

## Overview

This MCP server provides tools to generate and update C4 architecture diagrams by analyzing code projects. It uses Google's Gemini AI model to create comprehensive architecture documentation at three levels:

1. **Context View** - Shows the system in its environment with users and external systems
2. **Container View** - Shows high-level technology choices and responsibilities  
3. **Component View** - Shows internal structure of containers

## Features

- 🔍 **Code Analysis** - Scans projects and analyzes code structure
- 🤖 **AI-Powered** - Uses Gemini 2.0 Flash for intelligent architecture generation
- 📊 **C4 Model** - Follows the C4 model standard for software architecture
- 🔄 **PlantUML Support** - Generates and parses PlantUML diagrams
- 💾 **Persistent Memory** - Stores and reuses architecture diagrams
- 🔌 **MCP Compatible** - Works with any MCP client (Claude Desktop, etc.)

## Quick Start

### 1. Prerequisites

- Python 3.9+
- Google API key for Gemini
- Virtual environment (recommended)

### 2. Installation

```bash
# Clone and navigate to project
cd /Users/milad/Developer/Aices_PlusOne/AicesPlusOneAgent

# Install dependencies (already done)
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

### 3. Running the Server

#### Method 1: Direct Start (Recommended)
```bash
python start_server.py
```

#### Method 2: Using package.json script
```bash
npm start
```

#### Method 3: Direct Python execution
```bash
python src/server.py
```

### 4. Testing the Server

```bash
# Run the test script
python test_server.py
```

## Server Information

- **Name**: `c4-architecture-agent`
- **Version**: `1.0.0`
- **Protocol**: MCP (Model Context Protocol)
- **Communication**: JSON-RPC over stdio
- **Capabilities**: Tools execution

## Available Tools

### 1. `get_c4_architecture`

Generates or retrieves C4 architecture diagrams from code analysis.

**Parameters:**
- `force_refresh` (boolean, optional): Force regeneration even if cached version exists

**Example:**
```json
{
  "name": "get_c4_architecture",
  "arguments": {
    "force_refresh": true
  }
}
```

### 2. `update_c4_architecture`

Updates C4 architecture from PlantUML script.

**Parameters:**
- `plantuml_script` (string, required): PlantUML C4 diagram script
- `view_type` (string, optional): Which view to update ("context", "container", "component", "all")

**Example:**
```json
{
  "name": "update_c4_architecture", 
  "arguments": {
    "plantuml_script": "@startuml\\n!include C4_Context.puml\\nPerson(user, \"User\")\\nSystem(sys, \"System\")\\n@enduml",
    "view_type": "context"
  }
}
```

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```bash
# Required
GOOGLE_API_KEY=your-gemini-api-key-here

# Optional
CODE_ANALYSIS_API_URL=https://aices-plus-one-analyzer-691085128403.europe-west1.run.app
MEMORY_STORE_PATH=./data/memory.json
LOG_LEVEL=INFO
```

### Memory Storage

The server automatically stores generated architectures in `./data/memory.json` for persistence across sessions.

## Usage with MCP Clients

### Claude Desktop

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "c4-architecture-agent": {
      "command": "python",
      "args": ["/Users/milad/Developer/Aices_PlusOne/AicesPlusOneAgent/start_server.py"],
      "env": {
        "GOOGLE_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### Generic MCP Client

The server communicates via JSON-RPC over stdin/stdout. Send requests like:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/list"
}
```

## Architecture

```
src/
├── server.py          # Main MCP server implementation
├── agent.py           # C4 Architecture Agent with Gemini integration
├── schemas.py         # Pydantic models for C4 architecture
├── code_analyzer.py   # Code analysis service client
└── memory_store.py    # Persistent memory storage

data/
└── memory.json        # Stored architecture diagrams

start_server.py        # Main launcher script
test_server.py         # Server testing script
```

## Troubleshooting

### Common Issues

1. **Missing API Key**
   ```
   Error: Missing required environment variables: GOOGLE_API_KEY
   ```
   Solution: Set `GOOGLE_API_KEY` in your `.env` file

2. **Import Errors**
   ```
   ModuleNotFoundError: No module named 'google.generativeai'
   ```
   Solution: Install dependencies with `pip install -r requirements.txt`

3. **Network Issues**
   ```
   httpx.ConnectError: Connection refused
   ```
   Solution: Check internet connection and API endpoint availability

### Debug Mode

Run with debug logging:
```bash
LOG_LEVEL=DEBUG python start_server.py
```

### Logs

Server logs are written to:
- Console (stderr)
- File: `mcp_server.log`

## Development

### Running Tests
```bash
python test_server.py
```

### Manual Testing
```bash
# Test tool listing
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | python start_server.py

# Test architecture generation  
echo '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"get_c4_architecture","arguments":{}}}' | python start_server.py
```

## License

MIT License

## Support

For issues and questions, please check:
1. Server logs (`mcp_server.log`)
2. Environment variable configuration
3. Network connectivity to code analysis API
4. Google API key validity