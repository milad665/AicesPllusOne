# Aices Plus One: Complete C4 Architecture Intelligence System

> An intelligent AI-powered MCP service that automatically generates and provides detailed architectural context from the entire organization's codebase, combining a comprehensive code analysis service with an AI agent.

## 🏗️ System Overview

This project consists of two main components working together to provide complete architectural intelligence:

1. **🔍 Code Analyzer Service** (`AicesPlusOne/`) - A comprehensive Git repository manager that extracts project metadata using Tree-sitter
2. **🤖 C4 Architecture Agent** (`AicesPlusOneAgent/`) - An AI agent powered by **Gemini 2.5** that generates C4 architecture diagrams and exposes functionality via **Model Context Protocol (MCP)**

## 🎯 What It Does

### C4 Architecture Agent
This agent analyzes your code repositories and automatically generates comprehensive C4 architecture diagrams at three levels:

1. **Context View** - Shows your system in its environment with users and external systems
2. **Container View** - Details the applications, services, and data stores
3. **Component View** - Breaks down the internal structure of containers

All diagrams are generated in structured JSON format with PlantUML scripts for visualization.

### Code Analyzer Service
The underlying code analysis service provides:

- **Multi-Repository Management**: Configure multiple git repositories with SSH keys
- **Language-Agnostic Analysis**: Tree-sitter powered parsing for 8+ programming languages
- **Automatic Synchronization**: Periodic cloning/pulling of repositories (configurable interval)
- **Project Intelligence**: Automatic project type detection and technology stack identification
- **REST API**: Comprehensive API for project information and entry points
- **Real-time Updates**: Background synchronization with status tracking
- **Docker Support**: Container-ready for easy deployment

## � Quick Start

### 1. Start the Code Analyzer Service

```bash
# Navigate to the analyzer service
cd AicesPlusOne

# Quick setup and start
python setup.py
python dev_server.py
```

The service will be available at `http://localhost:8000` with API docs at `/docs`.

### 2. Start the C4 Architecture Agent

```bash
# Navigate to the agent
cd AicesPlusOneAgent

# Install dependencies
pip install -r requirements.txt

# Configure (create .env file)
echo "GOOGLE_API_KEY=your-gemini-api-key" > .env
echo "CODE_ANALYSIS_API_URL=http://localhost:8000" >> .env

# Test the agent
python cli.py

# Start MCP server
python src/server.py
```

## � Supported Languages & Capabilities

| Language   | Entry Points | Dependencies | Project Type Detection | Frameworks Detected |
|------------|--------------|--------------|----------------------|-------------------|
| Python     | ✅ Functions, Classes | ✅ requirements.txt, setup.py | ✅ | FastAPI, Flask, Django |
| JavaScript | ✅ Functions, Classes | ✅ package.json | ✅ | Express, React, Vue |
| TypeScript | ✅ Functions, Classes | ✅ package.json | ✅ | Angular, Next.js |
| Java       | ✅ Methods, Classes | ✅ pom.xml, build.gradle | ✅ | Spring Boot, Maven |
| C++        | ⏳ Coming Soon | ⏳ CMakeLists.txt | ✅ | |
| Go         | ⏳ Coming Soon | ✅ go.mod | ✅ | Gin, Echo |
| Rust       | ⏳ Coming Soon | ✅ Cargo.toml | ✅ | Actix, Rocket |
| C#         | ⏳ Coming Soon | ✅ .csproj | ✅ | ASP.NET Core |

## 🛠️ MCP Tools

### 1. `get_c4_architecture`
Get the latest C4 architecture diagram in JSON format.

### 2. `update_c4_architecture`
Update C4 architecture from PlantUML markup.

## 🔌 Integration Examples

### Claude Desktop Integration

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "c4-architecture": {
      "command": "python3",
      "args": ["/path/to/AicesPlusOneAgent/src/server.py"],
      "env": {
        "GOOGLE_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### Using the Code Analyzer API

```bash
# Add a repository
curl -X POST "http://localhost:8000/repositories" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "my-repo",
       "url": "git@github.com:user/repo.git",
       "ssh_private_key": "...",
       "ssh_public_key": "...",
       "default_branch": "main"
     }'

# Get projects and their architecture
curl "http://localhost:8000/projects"
```

## 🎪 The Vision

Modern software doesn't work in isolation anymore. Your React app talks to a Spring Boot backend, which calls an AWS Lambda, which triggers a Kafka event, which updates a Redis cache, and so on. This isn't just code - it's a **choreographed symphony of services**.

**AI coding agents are getting really good at writing code, but they're flying blind without architectural context.** They can help you write a function, but can they tell you if it fits into your overall system design?

**That's where we come in.** This tool automatically generates C4 architecture diagrams from your actual codebase - not outdated documentation. It gives AI coding agents (and humans!) the high-level architectural context they need to write **production-ready code** that actually fits into your system.

## 🚀 Future Roadmap

### 🎨 **IDE Extensions for Interactive C4 Manipulation**
- Visually manipulate C4 diagrams directly in development environment
- Real-time sync between diagram changes and code structure
- Interactive architecture exploration with zoom levels

### 📚 **Extensive Project Documentation Store**
- Store detailed project descriptions, business context, and domain models
- Track architectural evolution over time with version history
- Cross-reference between code changes and architectural impacts

### 🤖 **MCP Tool for Agent Memory Integration**
- Auto-capture important project details during development sessions
- Build institutional knowledge that persists across development teams
- Enable AI agents to make architecturally-aware code suggestions

### 🐛 **Bug History and Solution Database**
- Maintain a searchable database of past bugs and their solutions
- AI-powered bug pattern recognition and prevention suggestions

## 📚 Documentation

- **[Code Analyzer Service README](AicesPlusOne/README.md)** - Detailed service documentation
- **[C4 Agent README](AicesPlusOneAgent/README.md)** - Agent setup and MCP configuration
- **[Setup Guide](AicesPlusOneAgent/SETUP.md)** - Detailed setup and configuration
- **[MCP Configuration](AicesPlusOneAgent/MCP_CONFIGURATION.md)** - MCP server examples

## 🧪 Testing

```bash
# Test the code analyzer service
cd AicesPlusOne
python -m pytest tests/ -v

# Test the C4 agent
cd AicesPlusOneAgent
python -m pytest tests/ -v
python quickstart.py
```

## 🤝 Contributing

We welcome contributions! Areas for improvement:

- Additional language support for Tree-sitter analysis
- Enhanced PlantUML parsing and generation
- More sophisticated AI prompting strategies
- Diagram visualization tools
- Integration with more development tools

## 📄 License

MIT License - See LICENSE file for details.

## 🙏 Acknowledgments

- Built with [Google's Generative AI](https://ai.google.dev/)
- Uses [Model Context Protocol](https://modelcontextprotocol.io/)
- Implements [C4 Model](https://c4model.com/) architecture patterns
- Powered by [Tree-sitter](https://tree-sitter.github.io/tree-sitter/) for code analysis
