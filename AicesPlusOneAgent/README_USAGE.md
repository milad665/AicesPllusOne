# C4 Architecture Agent - Usage Guide

## Overview

This MCP server provides AI-powered C4 architecture diagram generation from code analysis. It uses:
- **Google Gemini 2.0** for AI-powered architecture analysis
- **Code Analyzer Service** for extracting project metadata and entry points
- **MCP Protocol** for integration with VS Code/GitHub Copilot

## Current Status

✅ **Working Components:**
- MCP server with `get_c4_architecture` and `update_c4_architecture` tools
- Integration with Code Analyzer Service API
- Gemini-powered architecture generation
- Memory persistence for generated architectures
- VS Code integration via `.vscode/mcp.json`

⚠️ **Next Step: Add Repositories**

The Code Analyzer Service currently has **0 projects** because no repositories have been added yet.

## Setup Steps

### 1. Add Repositories to Code Analyzer

You need to add git repositories to the Code Analyzer Service so it can analyze your code.

**Option A: Use the setup script**
```bash
.venv/bin/python setup_repositories.py
```

**Option B: Manual API call**
```bash
curl -X POST "https://aices-plus-one-analyzer-691085128403.europe-west1.run.app/repositories" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-project",
    "url": "https://github.com/username/repo.git",
    "ssh_private_key": "YOUR_SSH_PRIVATE_KEY",
    "ssh_public_key": "YOUR_SSH_PUBLIC_KEY",
    "default_branch": "main"
  }'
```

For **public repositories** using HTTPS, you can use dummy SSH keys:
```json
{
  "name": "public-project",
  "url": "https://github.com/username/repo.git",
  "ssh_private_key": "not-required-for-https",
  "ssh_public_key": "not-required-for-https",
  "default_branch": "main"
}
```

### 2. Trigger Repository Sync

After adding repositories, trigger synchronization:

```bash
curl -X POST "https://aices-plus-one-analyzer-691085128403.europe-west1.run.app/repositories/sync"
```

Wait 30-60 seconds for the service to clone and analyze the repositories.

### 3. Verify Projects

Check that projects were detected:

```bash
curl "https://aices-plus-one-analyzer-691085128403.europe-west1.run.app/projects"
```

or use the test script:

```bash
.venv/bin/python test_real_projects.py
```

### 4. Generate Architecture

Once projects are available, generate C4 architecture:

**Via Python:**
```python
import asyncio
from src.agent import C4ArchitectureAgent

async def main():
    agent = C4ArchitectureAgent()
    
    # Force refresh to generate from real projects
    arch = await agent.generate_c4_architecture(force_refresh=True)
    
    print(f"Systems: {len(arch.ContextView.SoftwareSystems)}")
    print(f"Containers: {len(arch.ContainerView.Containers)}")
    print(f"Components: {len(arch.ComponentView.Components)}")
    
    await agent.close()

asyncio.run(main())
```

**Via MCP (from GitHub Copilot):**
The MCP server is already configured in `.vscode/mcp.json`. Just ask GitHub Copilot:
- "Get the project architecture"
- "Show me the C4 architecture diagram"
- "What are the containers in this system?"

**Via MCP Tool:**
```python
# Use the c4-architecture MCP tool
from mcp_client import call_tool

result = call_tool("get_c4_architecture", {"force_refresh": True})
```

## How It Works

### Architecture Generation Flow

1. **Code Analysis**
   - Agent calls Code Analyzer Service `/projects` endpoint
   - Gets project metadata (name, language, type, dependencies, LOC, etc.)
   - Fetches entry points for each project (functions, classes, etc.)

2. **AI Processing**
   - Project data is sent to Gemini 2.0 with specialized prompt
   - Gemini analyzes the code structure and generates:
     - **Context View**: Systems and actors
     - **Container View**: Applications, databases, services
     - **Component View**: Internal components and their relationships
     - **PlantUML Scripts**: For visualization

3. **Validation & Storage**
   - Response is validated against Pydantic schemas
   - Architecture is saved to `data/memory.json`
   - Cached for future requests (unless `force_refresh=True`)

### MCP Server Tools

**1. get_c4_architecture**
```json
{
  "name": "get_c4_architecture",
  "description": "Get the latest C4 architecture diagram in JSON format",
  "inputSchema": {
    "type": "object",
    "properties": {
      "force_refresh": {
        "type": "boolean",
        "description": "Force regeneration even if cached version exists",
        "default": false
      }
    }
  }
}
```

**2. update_c4_architecture**
```json
{
  "name": "update_c4_architecture",
  "description": "Update C4 architecture from PlantUML markup",
  "inputSchema": {
    "type": "object",
    "properties": {
      "plantuml_script": {
        "type": "string",
        "description": "PlantUML C4 diagram script"
      },
      "view_type": {
        "type": "string",
        "enum": ["context", "container", "component", "all"],
        "default": "all"
      }
    },
    "required": ["plantuml_script"]
  }
}
```

## Example Output

Once you have projects in the analyzer, you'll get output like:

```json
{
  "ContextView": {
    "Actors": [
      {"Id": "dev1", "Name": "Developer", "PersonType": "SystemDeveloper", "Exists": true},
      {"Id": "user1", "Name": "End User", "PersonType": "EndUser", "Exists": true}
    ],
    "SoftwareSystems": [
      {
        "Id": "sys_agent",
        "Name": "AicesPlusOneAgent",
        "Description": "AI-powered C4 architecture generation system",
        "IsExternalSoftwareSystem": false,
        "Exists": true
      }
    ],
    "Relationships": [
      {"FromId": "dev1", "ToId": "sys_agent", "Name": "Develops"},
      {"FromId": "user1", "ToId": "sys_agent", "Name": "Uses"}
    ],
    "C4PlantUmlScript": "..."
  },
  "ContainerView": {
    "Containers": [
      {
        "Id": "cont_server",
        "Name": "MCP Server",
        "ContainerType": "Application",
        "Description": "Exposes C4 architecture tools via MCP protocol",
        "ContainerTechnology": "Python",
        "ParentSoftwareSystemId": "sys_agent",
        "TechnologyOrLanguage": "Python",
        "Exists": true
      },
      {
        "Id": "cont_agent",
        "Name": "C4 Architecture Agent",
        "ContainerType": "Application",
        "Description": "AI agent for generating C4 diagrams",
        "ContainerTechnology": "Python + Gemini",
        "ParentSoftwareSystemId": "sys_agent",
        "TechnologyOrLanguage": "Python",
        "Exists": true
      }
    ],
    "..."
  }
}
```

## Testing

Run the test suite:

```bash
# Test code analyzer connection
.venv/bin/python test_real_projects.py

# Test agent directly
.venv/bin/python simple_test.py

# Test MCP server
.venv/bin/python test_mcp_call.py
```

## Troubleshooting

**No projects found**
- Add repositories to the Code Analyzer Service (see Step 1)
- Trigger sync and wait for analysis to complete
- Check `/projects` endpoint to verify

**Gemini API errors**
- Verify `GOOGLE_API_KEY` is set in `.env`
- Check you have quota remaining
- Try with `gemini-2.0-flash-exp` model (currently used)

**MCP connection issues**
- Reload VS Code window
- Check `.vscode/mcp.json` configuration
- Verify MCP server starts: `.venv/bin/python -m src.server`

## Next Steps

1. **Add your repositories** to the Code Analyzer Service
2. **Sync and verify** projects are detected
3. **Generate architecture** with `force_refresh=True`
4. **Use via GitHub Copilot** in VS Code
5. **Visualize** PlantUML scripts using online tools or extensions
