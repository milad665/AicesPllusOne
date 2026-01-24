#!/bin/bash
set -e

# RUN_MODE can be:
# - api: Runs FastAPI server (serving UI + API)
# - mcp: Runs MCP server (stdio)
# - all: Runs both (backgrounded MCP? not practical for stdio, so typically just API or MCP)

MODE=${RUN_MODE:-api}

if [ "$MODE" = "mcp" ]; then
    echo "Starting MCP Server (stdio mode)..." >&2
    exec python -m src.server
elif [ "$MODE" = "api" ]; then
    echo "Starting FastAPI Server..."
    echo "Starting FastAPI Server..."
    exec uvicorn src.api:app --host 0.0.0.0 --port 8080
else
    echo "Unknown RUN_MODE: $MODE"
    exit 1
fi
