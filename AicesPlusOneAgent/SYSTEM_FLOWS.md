# C4 Architecture Agent - System Flow Diagrams

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        MCP CLIENT                            │
│              (Claude Desktop, Custom Client, etc.)           │
└────────────────────────┬────────────────────────────────────┘
                         │ MCP Protocol (stdio)
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      MCP SERVER                              │
│                    (src/server.py)                           │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Tool 1: get_c4_architecture                        │    │
│  │  Tool 2: update_c4_architecture                     │    │
│  └─────────────────────────────────────────────────────┘    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  C4 ARCHITECTURE AGENT                       │
│                     (src/agent.py)                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Gemini AI  │  │ Code Analyzer│  │ Memory Store │      │
│  │  (Gemini 2.5)│  │   (HTTP API) │  │  (JSON File) │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  EXTERNAL SERVICES                           │
│  ┌─────────────────────────────────────────────┐            │
│  │  Code Analysis Service                      │            │
│  │  https://aices-plus-one-analyzer-...        │            │
│  │  • Get projects                             │            │
│  │  • Get project details                      │            │
│  │  • Get entrypoints                          │            │
│  └─────────────────────────────────────────────┘            │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow: Get C4 Architecture

```
┌─────────┐
│  User   │
└────┬────┘
     │ 1. Request C4 architecture
     ▼
┌─────────────────┐
│   MCP Client    │
└────┬────────────┘
     │ 2. Call tool: get_c4_architecture
     │    { force_refresh: false }
     ▼
┌─────────────────────────────────────┐
│         MCP Server                  │
│  @app.call_tool()                   │
└────┬────────────────────────────────┘
     │ 3. Forward to agent
     ▼
┌─────────────────────────────────────┐
│    C4 Architecture Agent            │
│  generate_c4_architecture()         │
└────┬────────────────────────────────┘
     │
     │ 4. Check memory cache
     ▼
┌─────────────────┐        ┌────────────────┐
│  Memory Store   │  Yes   │  Return cached │
│  Has cached?    ├───────▶│  architecture  │
└────┬────────────┘        └────────────────┘
     │ No
     │ 5. Fetch project data
     ▼
┌─────────────────────────────────────┐
│     Code Analysis Service           │
│  • GET /projects                    │
│  • GET /projects/{id}               │
│  • GET /projects/{id}/entrypoints   │
└────┬────────────────────────────────┘
     │ 6. Return project metadata
     ▼
┌─────────────────────────────────────┐
│         Gemini AI Model             │
│  • Analyze projects                 │
│  • Generate C4 structure            │
│  • Create PlantUML scripts          │
└────┬────────────────────────────────┘
     │ 7. Return structured JSON
     ▼
┌─────────────────────────────────────┐
│    Validate & Save to Memory        │
│  • Pydantic validation              │
│  • Save to data/memory.json         │
└────┬────────────────────────────────┘
     │ 8. Return to MCP server
     ▼
┌─────────────────────────────────────┐
│         MCP Server                  │
│  • Format as TextContent            │
│  • JSON serialize                   │
└────┬────────────────────────────────┘
     │ 9. Send response
     ▼
┌─────────────────┐
│   MCP Client    │
│  Receives JSON  │
└─────────────────┘
```

## Data Flow: Update C4 Architecture

```
┌─────────┐
│  User   │
└────┬────┘
     │ 1. Provide PlantUML script
     ▼
┌─────────────────┐
│   MCP Client    │
└────┬────────────┘
     │ 2. Call tool: update_c4_architecture
     │    { plantuml_script: "...", view_type: "context" }
     ▼
┌─────────────────────────────────────┐
│         MCP Server                  │
└────┬────────────────────────────────┘
     │ 3. Forward to agent
     ▼
┌─────────────────────────────────────┐
│    C4 Architecture Agent            │
│  update_from_plantuml()             │
└────┬────────────────────────────────┘
     │
     │ 4. Load current architecture
     ▼
┌─────────────────┐
│  Memory Store   │
│  Load current   │
└────┬────────────┘
     │ 5. Current architecture JSON
     ▼
┌─────────────────────────────────────┐
│         Gemini AI Model             │
│  • Parse PlantUML script            │
│  • Extract entities & relationships │
│  • Merge with current architecture  │
│  • Update specified view(s)         │
└────┬────────────────────────────────┘
     │ 6. Return updated architecture
     ▼
┌─────────────────────────────────────┐
│    Validate & Save to Memory        │
│  • Pydantic validation              │
│  • Update memory.json               │
│  • Update metadata timestamps       │
└────┬────────────────────────────────┘
     │ 7. Return to MCP server
     ▼
┌─────────────────────────────────────┐
│         MCP Server                  │
│  • Format response                  │
└────┬────────────────────────────────┘
     │ 8. Send updated architecture
     ▼
┌─────────────────┐
│   MCP Client    │
└─────────────────┘
```

## Memory Store Structure

```
data/memory.json
├── c4_architecture
│   ├── ContextView
│   │   ├── Actors []
│   │   │   └── { Id, Name, PersonType, Exists }
│   │   ├── SoftwareSystems []
│   │   │   └── { Id, Name, Description, IsExternalSoftwareSystem, Exists }
│   │   ├── Relationships []
│   │   │   └── { FromId, ToId, Name }
│   │   └── C4PlantUmlScript (string)
│   │
│   ├── ContainerView
│   │   ├── Actors []
│   │   ├── Containers []
│   │   │   └── { Id, Name, ContainerType, Description, ... }
│   │   ├── Relationships []
│   │   └── C4PlantUmlScript (string)
│   │
│   ├── ComponentView
│   │   ├── Actors []
│   │   ├── Components []
│   │   │   └── { Id, Name, Description, ... }
│   │   ├── Relationships []
│   │   └── C4PlantUmlScript (string)
│   │
│   └── ArchitectureExplanation (string)
│
└── metadata
    ├── created_at (timestamp)
    ├── updated_at (timestamp)
    └── version (string)
```

## Agent Decision Flow

```
generate_c4_architecture(force_refresh)
    │
    ├─▶ if not force_refresh
    │   └─▶ Check memory
    │       ├─▶ Has cached? → Return cached ✓
    │       └─▶ No cached → Continue ▼
    │
    ├─▶ Fetch projects from Code Analysis Service
    │   ├─▶ GET /projects
    │   └─▶ For each project:
    │       └─▶ GET /projects/{id}/entrypoints
    │
    ├─▶ Build prompt with:
    │   ├─▶ System instructions
    │   ├─▶ Project metadata
    │   └─▶ JSON schema
    │
    ├─▶ Call Gemini AI
    │   ├─▶ Temperature: 0.2 (consistent)
    │   ├─▶ Response format: JSON
    │   └─▶ Receive structured output
    │
    ├─▶ Parse & Validate
    │   ├─▶ JSON decode
    │   ├─▶ Pydantic validation
    │   └─▶ If error → Create minimal architecture
    │
    ├─▶ Save to Memory
    │   └─▶ Update metadata timestamps
    │
    └─▶ Return C4Architecture object
```

## Error Handling Flow

```
Error Occurs
    │
    ├─▶ API Connection Error
    │   ├─▶ Log error
    │   ├─▶ Use fallback data
    │   └─▶ Return minimal architecture
    │
    ├─▶ AI Generation Error
    │   ├─▶ Log error
    │   ├─▶ Attempt JSON parsing
    │   └─▶ Create minimal valid architecture
    │
    ├─▶ Validation Error
    │   ├─▶ Log validation errors
    │   ├─▶ Return specific error to user
    │   └─▶ Suggest fixes
    │
    └─▶ Memory Error
        ├─▶ Log error
        ├─▶ Attempt recovery
        └─▶ Initialize new storage
```

## Component Interaction Matrix

```
┌─────────────┬──────────┬──────────┬────────────┬──────────┐
│ Component   │ Agent    │ Memory   │ Code API   │ Gemini   │
├─────────────┼──────────┼──────────┼────────────┼──────────┤
│ MCP Server  │   Calls  │    -     │     -      │    -     │
│ Agent       │    -     │  R/W     │   Calls    │  Calls   │
│ Memory      │  Used by │    -     │     -      │    -     │
│ Code API    │  Used by │    -     │     -      │    -     │
│ Gemini      │  Used by │    -     │     -      │    -     │
└─────────────┴──────────┴──────────┴────────────┴──────────┘

Legend: R/W = Read/Write, Calls = Makes API calls to
```

## Sequence: First Run

```
1. User starts MCP server
   └─▶ python src/server.py

2. MCP Server initializes
   ├─▶ Load environment variables
   ├─▶ Wait for stdio input
   └─▶ Ready state

3. MCP Client connects
   └─▶ Initialize handshake

4. Client requests tool list
   └─▶ Server returns 2 tools

5. Client calls get_c4_architecture
   └─▶ force_refresh: true

6. Agent initializes
   ├─▶ Configure Gemini API
   ├─▶ Create CodeAnalyzer
   ├─▶ Create MemoryStore
   └─▶ Load system prompt

7. Memory check (empty)
   └─▶ No cached data

8. Fetch code analysis
   ├─▶ Connect to API
   ├─▶ GET /projects
   └─▶ GET /projects/{id}/entrypoints

9. Generate with AI
   ├─▶ Build prompt
   ├─▶ Call Gemini
   └─▶ Parse response

10. Save to memory
    ├─▶ Validate structure
    ├─▶ Write to data/memory.json
    └─▶ Update metadata

11. Return to client
    └─▶ JSON formatted response

12. Client displays result
    └─▶ C4 architecture diagram
```

## Sequence: Subsequent Runs

```
1. Client calls get_c4_architecture
   └─▶ force_refresh: false

2. Agent checks memory
   └─▶ Cached data found ✓

3. Return cached architecture
   └─▶ Fast response (no AI call)

4. Client receives result
   └─▶ Same architecture as before
```

---

**These diagrams illustrate the complete system architecture and data flows**
