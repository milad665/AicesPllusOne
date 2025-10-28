# C4 Architecture Agent with MCP Server

> An intelligent AI agent that automatically generates and maintains C4 architecture diagrams from your codebase.

Powered by **Gemini 2.5**, and exposed as a **Model Context Protocol (MCP)** server.

(We also built a version with **Google's Agent Development Kit (ADK)**, which is included in this repo, but well ... we are still not so proud of it! So in case we should demo, we will demo the non-adk version)

## 🎪 The Pitch (Because Every Hackathon Needs One)

**"Automations"** - they said. *Yawn*. Could the theme be a bit less... boring? 😴

But here's the thing: we're not building toy automations. We come from the enterprise trenches where "automation" means orchestrating 47 microservices, 3 databases, 2 message queues, and that one legacy SOAP API from 2009 that nobody wants to touch but everybody depends on.

Now, let's get serious for a moment. 🎯

Modern software doesn't work in isolation anymore. Your beautiful React app talks to a Spring Boot backend, which calls an AWS Lambda, which triggers a Kafka event, which updates a Redis cache, which... you get the point. This isn't just code - it's a **choreographed symphony of services**, and understanding the high-level architecture is absolutely critical.

Here's the problem: **AI coding agents are getting really good at writing code, but they're flying blind without architectural context.** They can help you write a function, sure, but can they tell you if it fits into your overall system design? Can they understand which services this component should communicate with? Do they know if you're about to create circular dependencies that'll haunt you at 3 AM?

**That's where we come in.** 

This tool automatically generates C4 architecture diagrams from your actual codebase - not some outdated documentation from 2021 that nobody maintains. It gives AI coding agents (and humans, we still matter!) the high-level architectural context they need to write **production-ready code** that actually fits into your system.

Because let's face it: the difference between a code snippet and production code is understanding where it lives in the grand scheme of things. 

TL;DR: We make your AI coding assistant architecturally aware. You're welcome. 🎤⬇️

## 🎯 What It Does

This agent analyzes your code repositories and automatically generates comprehensive C4 architecture diagrams at three levels:

1. **Context View** - Shows your system in its environment with users and external systems
2. **Container View** - Details the applications, services, and data stores
3. **Component View** - Breaks down the internal structure of containers

All diagrams are generated in structured JSON format with PlantUML scripts for visualization.

## ✨ Key Features

- **🤖 AI-Powered Generation**: Uses Gemini 2.5 to intelligently analyze code and create architecture diagrams
- **🔗 Code Analysis Integration**: Automatically fetches project metadata from a code analysis service
- **🔌 MCP Server**: Exposes functionality via Model Context Protocol for universal compatibility
- **💾 Persistent Memory**: Uses ADK-style memory to maintain architecture across sessions
- **📊 Structured Output**: Generates diagrams in standardized JSON format with full schema validation
- **🔄 Live Updates**: Update architecture by providing PlantUML scripts

## 🛠️ MCP Tools

### 1. `get_c4_architecture`
Get the latest C4 architecture diagram in JSON format.

**Input:**
```json
{
  "force_refresh": false  // Optional: force regeneration
}
```

**Output:** Complete C4 architecture with Context, Container, and Component views.

### 2. `update_c4_architecture`
Update C4 architecture from PlantUML markup.

**Input:**
```json
{
  "plantuml_script": "@startuml...",  // PlantUML C4 script
  "view_type": "context"  // "context", "container", "component", or "all"
}
```

**Output:** Updated C4 architecture in JSON format.

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.10 or higher
- Google API key for Gemini ([Get one here](https://makersuite.google.com/app/apikey))

### 2. Installation

```bash
# Clone or navigate to the project
cd /Users/milad/Developer/AicesPlusOneAgent

# Install dependencies
pip install -r requirements.txt

# Run the quickstart script
python quickstart.py
```

### 3. Configuration

Create a `.env` file (or copy from `.env.example`):

```bash
GOOGLE_API_KEY=your-gemini-api-key-here
CODE_ANALYSIS_API_URL=https://aices-plus-one-analyzer-691085128403.europe-west1.run.app
MEMORY_STORE_PATH=./data/memory.json
```

### 4. Test It

```bash
# Test with CLI
python cli.py

# Run examples
python examples.py

# Start MCP server
python src/server.py
```

## 📖 Usage Modes

### Mode 1: CLI (Quick Testing)

```bash
python cli.py
```

Generates a C4 architecture and saves it to `data/c4_architecture.json`.

### Mode 2: MCP Server (Production)

```bash
python src/server.py
```

Runs as an MCP server for integration with AI assistants like Claude Desktop.

### Mode 3: Direct Import (Programmatic)

```python
from src.agent import C4ArchitectureAgent

agent = C4ArchitectureAgent()
architecture = await agent.generate_c4_architecture()
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│         MCP Server (src/server.py)          │
│  Exposes tools via Model Context Protocol   │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│      C4 Agent (src/agent.py)                │
│  • Orchestrates architecture generation     │
│  • Uses Gemini 2.5 for AI analysis          │
│  • Manages memory and state                 │
└──────┬──────────────────────┬───────────────┘
       │                      │
       ▼                      ▼
┌─────────────────┐   ┌──────────────────────┐
│  Code Analyzer  │   │   Memory Store       │
│  (API Client)   │   │   (Persistence)      │
│  • Fetches      │   │  • Saves/loads       │
│    projects     │   │    architecture      │
│  • Gets entry   │   │  • JSON storage      │
│    points       │   │  • Metadata          │
└─────────────────┘   └──────────────────────┘
```

### Components

- **`src/server.py`** - MCP server implementation
- **`src/agent.py`** - Core agent with AI-powered C4 generation
- **`src/schemas.py`** - Pydantic models for C4 architecture
- **`src/code_analyzer.py`** - HTTP client for code analysis service
- **`src/memory_store.py`** - Persistent storage using ADK memory pattern
- **`cli.py`** - Command-line interface for testing
- **`examples.py`** - Usage examples and documentation

## 🔌 MCP Integration

### For Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "c4-architecture": {
      "command": "python3",
      "args": ["/Users/milad/Developer/AicesPlusOneAgent/src/server.py"],
      "env": {
        "GOOGLE_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

See **[MCP_CONFIGURATION.md](MCP_CONFIGURATION.md)** for more details.

## 📚 Documentation

- **[README.md](README.md)** (this file) - Quick overview and getting started
- **[SETUP.md](SETUP.md)** - Detailed setup and configuration guide
- **[ADK_DOCUMENTATION.md](ADK_DOCUMENTATION.md)** - Google ADK concepts and implementation
- **[MCP_CONFIGURATION.md](MCP_CONFIGURATION.md)** - MCP server configuration examples

## 🧪 Testing

Run the test suite:

```bash
pip install pytest pytest-asyncio
python -m pytest tests/ -v
```

Run the quickstart check:

```bash
python quickstart.py
```

## 📊 C4 Architecture Schema

The agent generates architecture following this structure:

```json
{
  "ContextView": {
    "Actors": [...],
    "SoftwareSystems": [...],
    "Relationships": [...],
    "C4PlantUmlScript": "..."
  },
  "ContainerView": {
    "Actors": [...],
    "Containers": [...],
    "Relationships": [...],
    "C4PlantUmlScript": "..."
  },
  "ComponentView": {
    "Actors": [...],
    "Components": [...],
    "Relationships": [...],
    "C4PlantUmlScript": "..."
  },
  "ArchitectureExplanation": "Overall architecture description"
}
```

See **[src/schemas.py](src/schemas.py)** for the complete Pydantic schema.

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- Additional code analysis service integrations
- Enhanced PlantUML parsing
- More sophisticated AI prompting strategies
- Diagram visualization tools
- Unit test coverage

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- Built with [Google's Generative AI](https://ai.google.dev/)
- Uses [Model Context Protocol](https://modelcontextprotocol.io/)
- Implements [C4 Model](https://c4model.com/) architecture patterns
- Inspired by Google's Agent Development Kit (ADK) principles
