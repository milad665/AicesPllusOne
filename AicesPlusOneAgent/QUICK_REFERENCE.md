# 🚀 Quick Reference - C4 Architecture Agent

## Setup (One-Time)

```bash
# 1. Navigate to project
cd /Users/milad/Developer/AicesPlusOneAgent

# 2. Add your Google API key
echo "GOOGLE_API_KEY=your_actual_key_here" > .env

# 3. Verify installation
python quickstart.py
```

## Running the Server

```bash
# Start MCP server (runs in foreground)
python -m src.server

# Test with CLI
python cli.py get_architecture
python cli.py update_architecture --plantuml "path/to/file.puml"
```

## MCP Client Configuration

### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "c4-architecture": {
      "command": "python",
      "args": ["-m", "src.server"],
      "cwd": "/Users/milad/Developer/AicesPlusOneAgent",
      "env": {
        "PYTHONPATH": "/Users/milad/Developer/AicesPlusOneAgent"
      }
    }
  }
}
```

### Cline (VS Code)

Add to Cline MCP settings:

```json
{
  "mcpServers": {
    "c4-architecture": {
      "command": "/Users/milad/Developer/AicesPlusOneAgent/.venv/bin/python",
      "args": ["-m", "src.server"],
      "cwd": "/Users/milad/Developer/AicesPlusOneAgent"
    }
  }
}
```

## Available Tools

### 1. get_c4_architecture

**Purpose:** Generate or retrieve C4 architecture diagram

**Input:**
```json
{
  "force_refresh": false
}
```

**Output:** Complete C4 architecture in JSON format with:
- ContextView (systems and people)
- ContainerView (containers within systems)
- ComponentView (components within containers)
- ArchitectureExplanation (AI-generated description)

### 2. update_c4_architecture

**Purpose:** Update architecture from PlantUML script

**Input:**
```json
{
  "plantuml_script": "@startuml\n...\n@enduml",
  "view_type": "all"  // or "context", "container", "component"
}
```

**Output:** Updated C4 architecture in JSON format

## Common Tasks

### Get Architecture (First Time)
```bash
python -c "
import asyncio
from src.agent import C4ArchitectureAgent

async def main():
    agent = C4ArchitectureAgent()
    arch = await agent.generate_c4_architecture()
    print(arch.model_dump_json(indent=2))

asyncio.run(main())
"
```

### Update from PlantUML
```bash
python cli.py update_architecture --plantuml examples/sample.puml
```

### Clear Cache
```bash
rm data/memory.json
```

## Project Structure

```
AicesPlusOneAgent/
├── src/
│   ├── server.py          # ADK MCP Server ⭐
│   ├── agent.py           # AI Agent (Gemini)
│   ├── schemas.py         # Pydantic models
│   ├── memory_store.py    # Persistence
│   └── code_analyzer.py   # API client
├── data/
│   └── memory.json        # Cached architecture
├── .env                   # API keys (create this!)
└── requirements.txt       # Dependencies
```

## Troubleshooting

### Server won't start
```bash
# Check Python version
python --version  # Should be 3.9+

# Reinstall dependencies
pip install -r requirements.txt

# Check API key
cat .env  # Should contain GOOGLE_API_KEY=...
```

### No API key error
```bash
# Create .env file
echo "GOOGLE_API_KEY=your_key_here" > .env
```

### Import errors
```bash
# Activate virtual environment
source .venv/bin/activate

# Or use full path
/Users/milad/Developer/AicesPlusOneAgent/.venv/bin/python -m src.server
```

## Architecture Flow

```
┌─────────────┐
│ MCP Client  │ (Claude, Cline, etc.)
└──────┬──────┘
       │ JSON-RPC (stdio)
       ↓
┌──────────────────┐
│  ADKMCPServer    │
│  • list_tools    │
│  • call_tool     │
└──────┬───────────┘
       │
       ↓
┌─────────────────────┐
│ C4ArchitectureAgent │
│  • generate()       │
│  • update()         │
└──────┬──────────────┘
       │
       ├─→ MemoryStore (cache)
       ├─→ CodeAnalyzer (API)
       └─→ Gemini AI (generation)
```

## Key Files

- **START_HERE.md** - Main project overview
- **ADK_MCP_UPDATE.md** - Implementation details
- **COMPLETION_SUMMARY.md** - What was completed
- **SETUP.md** - Detailed setup guide
- **MCP_CONFIGURATION.md** - Client config examples

## Environment Variables

```bash
# Required
GOOGLE_API_KEY=your_google_api_key

# Optional
CODE_ANALYSIS_API_URL=https://aices-plus-one-analyzer-691085128403.europe-west1.run.app
MEMORY_FILE_PATH=data/memory.json
```

## Testing

```bash
# Run test suite
python test_adk_server.py

# Run unit tests
pytest tests/

# Quick verification
python quickstart.py
```

## API Endpoints (Code Analyzer)

```
GET  /projects                    # List all projects
GET  /projects/{id}              # Get project details
GET  /projects/{id}/entrypoints  # Get entry points
GET  /projects/{id}/repository   # Get repository info
```

## ADK Patterns Used

✅ **Tool Registration** - `_register_tools()` method  
✅ **Tool Handlers** - `list_tools_handler()`, `call_tool_handler()`  
✅ **Tool-Specific Handlers** - `_handle_get_c4_architecture()`, etc.  
✅ **Tool Conversion** - `adk_to_mcp_tool()` utility  
✅ **Structured Output** - Pydantic models  
✅ **Memory Pattern** - File-based persistence  
✅ **Error Handling** - Multi-level try/catch  
✅ **Logging** - Structured logging to stderr  

## Support

For issues or questions:
1. Check **TROUBLESHOOTING.md** (if exists)
2. Review **SETUP.md** for detailed instructions
3. See **ADK_DOCUMENTATION.md** for architecture details
4. Check **TEST_RESULTS.md** for known issues

---

**Version:** 1.0.0  
**Last Updated:** October 28, 2025  
**Status:** ✅ Production Ready
