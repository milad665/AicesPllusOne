# Google Agent Development Kit (ADK) Implementation

## Overview

This project implements an AI agent following Google's Agent Development Kit (ADK) principles. While Google's ADK/Genkit is primarily available in TypeScript/JavaScript, we've adapted the core concepts to Python.

## ADK Core Concepts

### 1. Agent Architecture

An **Agent** in ADK is an AI-powered system that can:
- Process user requests
- Use tools and external APIs
- Maintain memory/state
- Generate structured outputs
- Make decisions autonomously

Our implementation: `src/agent.py` - C4ArchitectureAgent

### 2. Memory System

ADK provides a **Memory** abstraction for agents to persist information across sessions.

#### Memory Pattern

```python
class MemoryStore:
    def save_architecture(self, architecture: C4Architecture)
    def load_architecture(self) -> Optional[C4Architecture]
    def clear()
    def get_metadata()
```

#### Our Implementation

- **Location**: File-based storage in `data/memory.json`
- **Persistence**: JSON format for easy inspection and backup
- **Versioning**: Tracks creation and update timestamps
- **Retrieval**: Fast in-memory access with disk persistence

#### Memory Schema

```json
{
  "c4_architecture": {
    "ContextView": {...},
    "ContainerView": {...},
    "ComponentView": {...},
    "ArchitectureExplanation": "..."
  },
  "metadata": {
    "created_at": "ISO-8601 timestamp",
    "updated_at": "ISO-8601 timestamp",
    "version": "1.0.0"
  }
}
```

### 3. Tools and Actions

ADK agents can use **Tools** - functions that the agent can call to perform actions or retrieve information.

#### Our Tools (via MCP)

1. **get_c4_architecture**
   - Purpose: Retrieve stored C4 architecture
   - Input: `force_refresh` flag
   - Output: Complete C4 diagram in JSON
   - Uses: Memory retrieval, code analysis, AI generation

2. **update_c4_architecture**
   - Purpose: Update architecture from PlantUML
   - Input: PlantUML script, view type
   - Output: Updated C4 diagram
   - Uses: AI parsing, memory update

### 4. Model Integration

ADK integrates with Google's AI models (Gemini).

#### Our Configuration

```python
import google.generativeai as genai

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.0-flash-exp')
```

#### Generation Config

```python
generation_config=genai.GenerationConfig(
    temperature=0.2,  # Low temperature for consistent output
    response_mime_type="application/json"  # Structured output
)
```

#### Prompting Strategy

We use a **system prompt** that defines:
- Role: Expert software architect
- Task: Generate C4 diagrams
- Format: Strict JSON schema
- Context: Code analysis data

### 5. Structured Output

ADK emphasizes **structured, schema-validated outputs** rather than free-form text.

#### Implementation

```python
from pydantic import BaseModel

class C4Architecture(BaseModel):
    ContextView: ContextView
    ContainerView: ContainerView
    ComponentView: ComponentView
    ArchitectureExplanation: str
```

Benefits:
- Type safety
- Validation
- Clear contracts
- Easy serialization

### 6. External Integrations

ADK agents can integrate with external services and APIs.

#### Our Integration: Code Analysis Service

```python
class CodeAnalyzer:
    async def get_projects()
    async def get_project(project_id)
    async def get_project_entrypoints(project_id)
```

Features:
- Async/await for performance
- Error handling
- Connection pooling
- Graceful degradation

### 7. Agent Workflow

#### High-Level Flow

```
User Request
    ↓
MCP Server (receives tool call)
    ↓
Agent (processes request)
    ↓
Check Memory (cached result?)
    ↓
    No → Generate New
         ↓
         Fetch Code Analysis Data
         ↓
         Call Gemini AI
         ↓
         Parse & Validate Response
         ↓
         Save to Memory
    ↓
    Yes → Return Cached
    ↓
Return Result
```

#### Implementation

```python
async def generate_c4_architecture(self, force_refresh: bool = False):
    # Check cache
    if not force_refresh:
        cached = self.memory.load_architecture()
        if cached:
            return cached
    
    # Get data
    projects = await self.code_analyzer.get_projects()
    
    # Generate with AI
    architecture = await self._generate_with_gemini(projects)
    
    # Save
    self.memory.save_architecture(architecture)
    
    return architecture
```

### 8. Error Handling and Fallbacks

ADK encourages robust error handling.

#### Our Strategy

1. **Graceful Degradation**: If AI fails, return minimal valid architecture
2. **Logging**: Track errors without failing
3. **Validation**: Use Pydantic for automatic validation
4. **Retries**: Could add retry logic for transient failures

```python
try:
    architecture_data = json.loads(response.text)
    return C4Architecture(**architecture_data)
except json.JSONDecodeError:
    # Fallback to minimal architecture
    return self._create_minimal_architecture(project_details)
```

## ADK vs Traditional Approaches

### Traditional Chatbot

```python
def process_message(message: str) -> str:
    response = model.generate(message)
    return response
```

### ADK Agent

```python
async def generate_c4_architecture(self, force_refresh: bool):
    # 1. Check memory
    cached = self.memory.load_architecture()
    
    # 2. Use tools
    projects = await self.code_analyzer.get_projects()
    
    # 3. AI with structured output
    architecture = await self._generate_with_gemini(projects)
    
    # 4. Persist
    self.memory.save_architecture(architecture)
    
    # 5. Return typed result
    return architecture  # C4Architecture object
```

Key Differences:
- **Stateful** vs stateless
- **Structured output** vs text
- **Tool use** vs pure generation
- **Validation** vs raw output

## MCP (Model Context Protocol)

MCP is the interface layer for our agent.

### Why MCP?

1. **Standardization**: Common protocol for AI tools
2. **Interoperability**: Works with multiple clients
3. **Discovery**: Tools are self-describing
4. **Streaming**: Supports real-time communication

### MCP Server Implementation

```python
from mcp.server import Server
from mcp.server.stdio import stdio_server

app = Server("c4-architecture-agent")

@app.list_tools()
async def list_tools() -> list[Tool]:
    return [Tool(...), Tool(...)]

@app.call_tool()
async def call_tool(name: str, arguments: Any):
    # Route to agent
    return agent.execute(name, arguments)
```

### MCP Client Configuration

```json
{
  "mcpServers": {
    "c4-architecture": {
      "command": "python",
      "args": ["src/server.py"]
    }
  }
}
```

## Best Practices from ADK

### 1. Separation of Concerns

- **Agent**: Business logic
- **Memory**: Persistence
- **Tools**: External actions
- **Server**: Communication protocol
- **Schemas**: Data contracts

### 2. Type Safety

Use Pydantic models everywhere:
- Input validation
- Output validation
- Documentation
- IDE support

### 3. Async/Await

All I/O operations are async:
- API calls
- AI generation
- File operations (could be)

### 4. Configuration

Environment-based configuration:
- API keys in `.env`
- URLs configurable
- Paths adjustable

### 5. Testing

Support multiple modes:
- CLI for quick testing
- MCP for production
- Direct import for unit tests

## Advanced ADK Concepts

### Multi-Agent Systems

ADK supports multiple agents working together. Could extend to:

```python
class ArchitectureAgent:
    # Generates architecture

class ReviewerAgent:
    # Reviews and critiques architecture

class OptimizerAgent:
    # Suggests improvements
```

### Streaming

For long-running operations:

```python
async def generate_c4_architecture_stream():
    yield {"status": "fetching_projects"}
    projects = await self.code_analyzer.get_projects()
    
    yield {"status": "analyzing"}
    # ... processing
    
    yield {"status": "complete", "result": architecture}
```

### Context Management

ADK agents maintain context across turns:

```python
class ConversationMemory:
    def add_message(self, role: str, content: str)
    def get_history(self) -> list
    def clear()
```

### Tool Chaining

Agents can call multiple tools in sequence:

```python
# 1. Fetch code
code = await get_code_tool()

# 2. Analyze
analysis = await analyze_code_tool(code)

# 3. Generate diagram
diagram = await generate_diagram_tool(analysis)
```

## Performance Optimization

### Caching

Our memory system acts as a cache:
- First call: Slow (fetches + generates)
- Subsequent calls: Fast (memory retrieval)

### Parallel Execution

```python
# Fetch multiple projects in parallel
tasks = [
    self.code_analyzer.get_project(pid)
    for pid in project_ids
]
results = await asyncio.gather(*tasks)
```

### Lazy Loading

Only fetch data when needed:
```python
if force_refresh or not self.memory.has_data():
    # Fetch and generate
else:
    # Return cached
```

## Security Considerations

### API Key Management

- Never commit keys to git
- Use environment variables
- Rotate keys regularly

### Input Validation

- Validate all tool inputs
- Sanitize PlantUML scripts
- Limit input sizes

### Output Validation

- Validate all AI outputs
- Use Pydantic schemas
- Fail safely

## Monitoring and Observability

### Logging

```python
import logging

logger = logging.getLogger(__name__)
logger.info("Generating architecture")
logger.error("Failed to parse response", exc_info=True)
```

### Metrics

Could add:
- Generation time
- API call latency
- Cache hit rate
- Error rate

### Tracing

Could integrate with:
- OpenTelemetry
- Google Cloud Trace
- Custom logging

## Conclusion

This implementation demonstrates ADK principles:

✅ **Structured output** - C4Architecture schema  
✅ **Memory/State** - MemoryStore  
✅ **Tool use** - Code analyzer integration  
✅ **AI integration** - Gemini 2.5  
✅ **Protocol support** - MCP server  
✅ **Type safety** - Pydantic everywhere  
✅ **Async operations** - Performance  
✅ **Error handling** - Graceful degradation  

The agent is production-ready and follows modern AI agent development patterns.
