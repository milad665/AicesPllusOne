# C4 Architecture Agent - Setup Guide

## Overview

This project implements an AI agent using Google's Agent Development Kit (ADK) principles that generates C4 architecture diagrams. The agent is exposed as an MCP (Model Context Protocol) server and integrates with a code analysis service.

## Architecture

### Components

1. **C4 Architecture Agent** (`src/agent.py`)
   - Uses Google Gemini 2.5 for AI-powered architecture generation
   - Integrates with code analysis service for project metadata
   - Implements ADK-style memory for persistent storage

2. **MCP Server** (`src/server.py`)
   - Exposes the agent via Model Context Protocol
   - Provides tools for getting and updating C4 diagrams

3. **Code Analyzer Client** (`src/code_analyzer.py`)
   - Interfaces with the code analysis API
   - Fetches project metadata, entrypoints, and repository information

4. **Memory Store** (`src/memory_store.py`)
   - Implements ADK-style persistent memory
   - Stores C4 architecture for long-term use

5. **Schema Definitions** (`src/schemas.py`)
   - Pydantic models for C4 architecture
   - Enforces the specified JSON schema

## Installation

### Prerequisites

- Python 3.10 or higher
- Google Cloud account with Gemini API access
- Access to the code analysis service

### Step 1: Clone and Setup

```bash
cd /Users/milad/Developer/AicesPlusOneAgent
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
pip install -r requirements.txt
```

### Step 2: Configure Environment

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```bash
GOOGLE_API_KEY=your-actual-gemini-api-key
CODE_ANALYSIS_API_URL=https://aices-plus-one-analyzer-691085128403.europe-west1.run.app
MEMORY_STORE_PATH=./data/memory.json
```

### Step 3: Get Google API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key to your `.env` file

## Usage

### Option 1: CLI Mode (Testing)

Test the agent directly without MCP:

```bash
python cli.py
```

This will:
- Connect to the code analysis service
- Generate a C4 architecture diagram
- Save the result to `data/c4_architecture.json`

### Option 2: MCP Server Mode (Production)

Run as an MCP server:

```bash
python src/server.py
```

The server will start and communicate via stdio (standard input/output) following the MCP protocol.

### Option 3: Examples

Run the examples to see different usage patterns:

```bash
python examples.py
```

## MCP Integration

### Configure MCP Client

To use this agent with an MCP-compatible client (like Claude Desktop), add to your MCP configuration:

```json
{
  "mcpServers": {
    "c4-architecture": {
      "command": "python",
      "args": ["/Users/milad/Developer/AicesPlusOneAgent/src/server.py"],
      "env": {
        "GOOGLE_API_KEY": "your-api-key",
        "CODE_ANALYSIS_API_URL": "https://aices-plus-one-analyzer-691085128403.europe-west1.run.app"
      }
    }
  }
}
```

### Available MCP Tools

#### 1. get_c4_architecture

Get the latest C4 architecture diagram in JSON format.

**Input:**
```json
{
  "force_refresh": false
}
```

**Output:**
Complete C4 architecture in JSON format with:
- ContextView (System context with actors and systems)
- ContainerView (Containers/applications)
- ComponentView (Internal components)
- ArchitectureExplanation (Overall description)

#### 2. update_c4_architecture

Update C4 architecture from PlantUML markup.

**Input:**
```json
{
  "plantuml_script": "@startuml\n!include C4_Context.puml\nPerson(user, \"User\")\n@enduml",
  "view_type": "context"
}
```

**Output:**
Updated C4 architecture in JSON format.

## ADK Memory Pattern

The agent implements ADK-style memory for persistence:

- **Location**: `./data/memory.json`
- **Structure**:
  ```json
  {
    "c4_architecture": { ... },
    "metadata": {
      "created_at": "2025-01-01T00:00:00",
      "updated_at": "2025-01-01T00:00:00",
      "version": "1.0.0"
    }
  }
  ```
- **Features**:
  - Long-term persistence across restarts
  - Automatic versioning
  - Metadata tracking

## C4 Architecture Schema

The agent generates architecture following this schema:

### Levels

1. **Context View** - Shows the system in its environment
   - Actors/Persons
   - Software Systems
   - Relationships
   - PlantUML script

2. **Container View** - Shows applications and data stores
   - Actors
   - Containers (with technology details)
   - Relationships
   - PlantUML script

3. **Component View** - Shows internal components
   - Actors
   - Components (with technology details)
   - Relationships
   - PlantUML script

### Entity Types

- **Person**: End users, administrators, stakeholders, etc.
- **SoftwareSystem**: Software systems (internal/external)
- **Container**: Applications, databases, file systems
- **Component**: Services, repositories, controllers, etc.
- **Relationship**: Connections between entities

## Code Analysis Service

The agent integrates with the code analysis service:

- **Base URL**: https://aices-plus-one-analyzer-691085128403.europe-west1.run.app
- **Endpoints Used**:
  - `GET /projects` - Get all projects
  - `GET /projects/{id}` - Get project details
  - `GET /projects/{id}/entrypoints` - Get project entry points
  - `GET /repositories` - Get repositories

## Troubleshooting

### Common Issues

1. **"GOOGLE_API_KEY is required"**
   - Solution: Add your Gemini API key to `.env` file

2. **Connection errors to code analysis service**
   - Solution: Check network connectivity and API URL

3. **JSON parsing errors**
   - Solution: The agent will fall back to creating a minimal valid architecture

### Debug Mode

Enable detailed logging by modifying the agent:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Development

### Project Structure

```
/Users/milad/Developer/AicesPlusOneAgent/
├── src/
│   ├── __init__.py
│   ├── agent.py           # Main agent implementation
│   ├── server.py          # MCP server
│   ├── schemas.py         # C4 schema definitions
│   ├── code_analyzer.py   # Code analysis client
│   └── memory_store.py    # ADK memory implementation
├── data/
│   └── memory.json        # Persistent storage
├── cli.py                 # CLI interface
├── examples.py            # Usage examples
├── requirements.txt       # Python dependencies
├── .env                   # Environment configuration
└── README.md             # Documentation
```

### Testing

Run the CLI test:
```bash
python cli.py
```

Run examples:
```bash
python examples.py
```

## Next Steps

1. **Configure your API keys** in `.env`
2. **Run the CLI** to test basic functionality
3. **Configure MCP client** to use the server
4. **Generate your first C4 diagram**

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review the examples
3. Examine the generated `data/memory.json` for debugging
