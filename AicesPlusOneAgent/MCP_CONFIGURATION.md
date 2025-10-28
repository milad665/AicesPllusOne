# MCP Server Configuration Examples

## For GitHub Copilot (VS Code)

**Location:** VS Code User Settings (`settings.json`)

**Steps:**
1. Open Command Palette: `Cmd + Shift + P` (macOS) or `Ctrl + Shift + P` (Windows/Linux)
2. Type "Preferences: Open User Settings (JSON)" and press Enter
3. Add the following configuration:

```json
{
  "github.copilot.mcp.servers": {
    "c4-architecture-agent": {
      "command": "/Users/milad/Developer/AicesPlusOneAgent/.venv/bin/python",
      "args": ["-m", "src.server"],
      "cwd": "/Users/milad/Developer/AicesPlusOneAgent"
    }
  }
}
```

**Usage:**
- Reload VS Code: Command Palette → "Developer: Reload Window"
- In Copilot Chat, type: `@c4-architecture-agent generate a C4 architecture diagram`
- The agent will use the code analysis service and Gemini AI to create the diagram

**Notes:**
- Replace the paths with your actual project location
- Make sure you've added `GOOGLE_API_KEY` to your `.env` file
- The agent name `c4-architecture-agent` can be customized

## For Claude Desktop

Add this to your Claude Desktop configuration file:

**Location (macOS):** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "c4-architecture": {
      "command": "python3",
      "args": ["/Users/milad/Developer/AicesPlusOneAgent/src/server.py"],
      "env": {
        "GOOGLE_API_KEY": "your-google-api-key-here",
        "CODE_ANALYSIS_API_URL": "https://aices-plus-one-analyzer-691085128403.europe-west1.run.app",
        "MEMORY_STORE_PATH": "/Users/milad/Developer/AicesPlusOneAgent/data/memory.json"
      }
    }
  }
}
```

## For VS Code with Cline Extension

Add this to your Cline MCP settings:

```json
{
  "mcpServers": {
    "c4-architecture": {
      "command": "python3",
      "args": ["/Users/milad/Developer/AicesPlusOneAgent/src/server.py"],
      "env": {
        "GOOGLE_API_KEY": "your-google-api-key-here",
        "CODE_ANALYSIS_API_URL": "https://aices-plus-one-analyzer-691085128403.europe-west1.run.app"
      }
    }
  }
}
```

## For Custom MCP Client

If you're building a custom MCP client:

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    server_params = StdioServerParameters(
        command="python3",
        args=["/Users/milad/Developer/AicesPlusOneAgent/src/server.py"],
        env={
            "GOOGLE_API_KEY": "your-api-key",
            "CODE_ANALYSIS_API_URL": "https://aices-plus-one-analyzer-691085128403.europe-west1.run.app"
        }
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # List available tools
            tools = await session.list_tools()
            print(f"Available tools: {tools}")
            
            # Call a tool
            result = await session.call_tool(
                "get_c4_architecture",
                {"force_refresh": False}
            )
            print(result)

asyncio.run(main())
```

## Environment Variables

The MCP server uses these environment variables:

- `GOOGLE_API_KEY` - **Required** - Your Google Gemini API key
- `CODE_ANALYSIS_API_URL` - URL for the code analysis service (has default)
- `MEMORY_STORE_PATH` - Path to store persistent memory (has default)

### Getting a Google API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key and add it to your configuration

## Tool Usage Examples

### Using get_c4_architecture tool

**From Claude Desktop:**
```
Please use the get_c4_architecture tool to show me the current architecture.
```

**MCP Call:**
```json
{
  "tool": "get_c4_architecture",
  "arguments": {
    "force_refresh": false
  }
}
```

**Response:**
```json
{
  "ContextView": {
    "Actors": [...],
    "SoftwareSystems": [...],
    "Relationships": [...],
    "C4PlantUmlScript": "..."
  },
  "ContainerView": {...},
  "ComponentView": {...},
  "ArchitectureExplanation": "..."
}
```

### Using update_c4_architecture tool

**From Claude Desktop:**
```
Please update the C4 architecture using this PlantUML script:

@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Context.puml

Person(admin, "Administrator", "System admin")
System(mainSystem, "Main System", "Core application")
System_Ext(externalAPI, "External API", "Third-party service")

Rel(admin, mainSystem, "Manages")
Rel(mainSystem, externalAPI, "Integrates with")

@enduml
```

**MCP Call:**
```json
{
  "tool": "update_c4_architecture",
  "arguments": {
    "plantuml_script": "@startuml\n!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Context.puml\n\nPerson(admin, \"Administrator\", \"System admin\")\nSystem(mainSystem, \"Main System\", \"Core application\")\nSystem_Ext(externalAPI, \"External API\", \"Third-party service\")\n\nRel(admin, mainSystem, \"Manages\")\nRel(mainSystem, externalAPI, \"Integrates with\")\n\n@enduml",
    "view_type": "context"
  }
}
```

## Troubleshooting

### Server won't start

1. Check Python version: `python3 --version` (need 3.10+)
2. Check dependencies: `pip install -r requirements.txt`
3. Check API key is set in environment

### Tools not appearing

1. Restart your MCP client
2. Check server logs for errors
3. Verify configuration file path is correct

### Authentication errors

1. Verify `GOOGLE_API_KEY` is valid
2. Check API key has necessary permissions
3. Try generating a new API key

### Connection to code analysis service fails

1. Check internet connection
2. Verify the service URL is accessible
3. Check for firewall/proxy issues

## Advanced Configuration

### Custom Memory Location

```json
{
  "env": {
    "MEMORY_STORE_PATH": "/custom/path/to/memory.json"
  }
}
```

### Debug Mode

Enable Python logging:

```json
{
  "env": {
    "PYTHONUNBUFFERED": "1",
    "LOG_LEVEL": "DEBUG"
  }
}
```

### Virtual Environment

If using a virtual environment:

```json
{
  "command": "/Users/milad/Developer/AicesPlusOneAgent/venv/bin/python",
  "args": ["/Users/milad/Developer/AicesPlusOneAgent/src/server.py"]
}
```

## Testing the Configuration

Run the quickstart script to verify setup:

```bash
cd /Users/milad/Developer/AicesPlusOneAgent
python3 quickstart.py
```

Then test the server directly:

```bash
python3 src/server.py
```

The server will wait for MCP protocol messages on stdin. Press Ctrl+C to exit.

For interactive testing, use the CLI:

```bash
python3 cli.py
```
