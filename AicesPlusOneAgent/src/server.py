"""
MCP Server for C4 Architecture Agent

ADK-style MCP server implementation using JSON-RPC over stdio.
Follows Google's Agent Development Kit (ADK) patterns for tool registration and handling.

This implementation uses a simplified JSON-RPC protocol since the official MCP Python SDK
is not yet available in PyPI. It maintains compatibility with MCP clients while following
ADK best practices.
"""

import asyncio
import json
import logging
import sys
from typing import Any, Dict, List

from .agent import C4ArchitectureAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# Global agent instance (ADK pattern - singleton for memory persistence)
agent: C4ArchitectureAgent = None


def adk_to_mcp_tool(name: str, description: str, input_schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert ADK tool definition to MCP tool format.
    
    This utility function follows the ADK pattern of tool conversion,
    adapting our tool definitions to the MCP protocol.
    
    Args:
        name: Tool identifier
        description: Human-readable tool description
        input_schema: JSON Schema for tool inputs
        
    Returns:
        MCP-compatible tool definition
    """
    return {
        "name": name,
        "description": description,
        "inputSchema": input_schema
    }


class ADKMCPServer:
    """
    ADK-style MCP Server implementation.
    
    This server follows ADK patterns:
    - Tool registration via list_tools()
    - Tool execution via call_tool()
    - Structured error handling
    - Async/await for performance
    - Logging for observability
    """
    
    def __init__(self):
        """Initialize server with registered tools."""
        self.tools = self._register_tools()
        logger.info(f"Initialized ADK MCP Server with {len(self.tools)} tools")
    
    def _register_tools(self) -> List[Dict[str, Any]]:
        """
        Register all available tools.
        
        This follows the ADK pattern of tool registration,
        similar to @app.list_tools() decorator pattern.
        
        Returns:
            List of MCP tool definitions
        """
        return [
            adk_to_mcp_tool(
                name="get_stored_c4_architecture",
                description="Get the latest C4 architecture diagram from storage in JSON format. "
                           "This is a fast, read-only operation that returns the currently stored architecture.",
                input_schema={
                    "type": "object",
                    "properties": {}
                }
            ),
            adk_to_mcp_tool(
                name="generate_new_c4_architecture",
                description="Force a fresh code analysis and AI generation of the C4 architecture. "
                           "This is an expensive operation that uses Gemini to analyze code and generate a new diagram.",
                input_schema={
                    "type": "object",
                    "properties": {}
                }
            ),
            adk_to_mcp_tool(
                name="update_c4_architecture_with_plantuml",
                description="Update the stored C4 architecture by parsing a PlantUML script. "
                           "Parses the script and merges changes into the architecture model.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "plantuml_script": {
                            "type": "string",
                            "description": "PlantUML C4 diagram script to parse and update from"
                        },
                        "view_type": {
                            "type": "string",
                            "enum": ["context", "container", "component", "all"],
                            "description": "Which C4 view(s) to update",
                            "default": "all"
                        }
                    },
                    "required": ["plantuml_script"]
                }
            )
        ]
    
    async def list_tools_handler(self) -> List[Dict[str, Any]]:
        """
        Handle tools/list request.
        
        ADK pattern: Equivalent to @app.list_tools() decorator.
        Returns all registered tools for client discovery.
        
        Returns:
            List of tool definitions
        """
        logger.info("Listing available tools")
        return self.tools
    
    async def call_tool_handler(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle tools/call request.
        
        ADK pattern: Equivalent to @app.call_tool() decorator.
        Routes tool calls to the appropriate agent methods.
        
        Args:
            name: Tool name to execute
            arguments: Tool-specific arguments
            
        Returns:
            Tool execution result in MCP format
            
        Raises:
            ValueError: If tool name is unknown or arguments are invalid
        """
        global agent
        
        # Lazy initialization of agent (ADK pattern - defer heavy initialization)
        if agent is None:
            logger.info("Initializing C4ArchitectureAgent")
            agent = C4ArchitectureAgent()
        
        logger.info(f"Executing tool: {name}")
        
        if name == "get_stored_c4_architecture":
            return await self._handle_get_c4_architecture(arguments)
        elif name == "generate_new_c4_architecture":
            return await self._handle_regenerate_c4_architecture(arguments)
        elif name == "update_c4_architecture_with_plantuml":
            return await self._handle_update_c4_architecture(arguments)
        else:
            error_msg = f"Unknown tool: {name}"
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    async def _handle_get_c4_architecture(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute get_c4_architecture tool.
        
        Args:
            arguments: Tool arguments (empty)
            
        Returns:
            MCP-formatted result with C4 architecture JSON
        """
        logger.info("Getting stored C4 architecture")
        
        try:
            architecture = await agent.get_current_architecture()
            if not architecture:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": "No architecture stored. Use regenerate_c4_architecture to create one."
                        }
                    ]
                }
                
            result_json = json.dumps(architecture.model_dump(mode='json'), indent=2)
            
            logger.info("Successfully retrieved C4 architecture")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": result_json
                    }
                ]
            }
        except Exception as e:
            logger.error(f"Failed to get C4 architecture: {e}", exc_info=True)
            raise

    async def _handle_regenerate_c4_architecture(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute regenerate_c4_architecture tool.
        
        Args:
            arguments: Tool arguments (empty)
            
        Returns:
            MCP-formatted result with new C4 architecture JSON
        """
        logger.info("Regenerating C4 architecture")
        
        try:
            architecture = await agent.generate_c4_architecture()
            result_json = json.dumps(architecture.model_dump(mode='json'), indent=2)
            
            logger.info("Successfully regenerated C4 architecture")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": result_json
                    }
                ]
            }
        except Exception as e:
            logger.error(f"Failed to regenerate C4 architecture: {e}", exc_info=True)
            raise
    
    async def _handle_update_c4_architecture(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute update_c4_architecture tool.
        
        ADK pattern: Tool-specific handler with validation and error handling.
        
        Args:
            arguments: Tool arguments (plantuml_script, view_type)
            
        Returns:
            MCP-formatted result with updated C4 architecture JSON
            
        Raises:
            ValueError: If plantuml_script is missing
        """
        plantuml_script = arguments.get("plantuml_script")
        if not plantuml_script:
            error_msg = "plantuml_script is required"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        view_type = arguments.get("view_type", "all")
        logger.info(f"Updating C4 architecture from PlantUML (view_type={view_type})")
        
        try:
            architecture = await agent.update_from_plantuml(
                plantuml_script=plantuml_script,
                view_type=view_type
            )
            result_json = json.dumps(architecture.model_dump(mode='json'), indent=2)
            
            logger.info("Successfully updated C4 architecture from PlantUML")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": result_json
                    }
                ]
            }
        except Exception as e:
            logger.error(f"Failed to update C4 architecture: {e}", exc_info=True)
            raise
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle incoming JSON-RPC request.
        
        ADK pattern: Protocol adapter that routes to appropriate handlers.
        
        Args:
            request: JSON-RPC 2.0 request
            
        Returns:
            JSON-RPC 2.0 response
        """
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        logger.debug(f"Received request: method={method}, id={request_id}")
        
        try:
            if method == "initialize":
                # MCP protocol initialization
                logger.info("Handling initialize request")
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "c4-architecture-agent",
                            "version": "1.0.0"
                        }
                    }
                }
            elif method == "tools/list":
                tools = await self.list_tools_handler()
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"tools": tools}
                }
            elif method == "tools/call":
                result = await self.call_tool_handler(
                    params.get("name"),
                    params.get("arguments", {})
                )
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": result
                }
            else:
                error_msg = f"Method not found: {method}"
                logger.warning(error_msg)
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": error_msg
                    }
                }
        except Exception as e:
            logger.error(f"Error handling request: {e}", exc_info=True)
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32000,
                    "message": str(e)
                }
            }


async def run_server():
    """
    Main server loop.
    
    ADK pattern: Async server lifecycle management.
    Implements stdio-based JSON-RPC communication for MCP protocol.
    """
    server = ADKMCPServer()
    logger.info("C4 Architecture MCP Server started")
    logger.info("Listening for JSON-RPC requests on stdin...")
    
    while True:
        try:
            # Read request from stdin (blocking, run in executor for async)
            line = await asyncio.get_event_loop().run_in_executor(
                None,
                sys.stdin.readline
            )
            
            # Empty line indicates EOF
            if not line:
                logger.info("Received EOF, shutting down server")
                break
            
            # Parse JSON-RPC request
            try:
                request = json.loads(line.strip())
            except json.JSONDecodeError as e:
                logger.error(f"JSON parse error: {e}")
                response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": f"Parse error: {str(e)}"
                    }
                }
                print(json.dumps(response), flush=True)
                continue
            
            # Process request
            response = await server.handle_request(request)
            
            # Send response to stdout
            print(json.dumps(response), flush=True)
            
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt, shutting down server")
            break
        except Exception as e:
            logger.error(f"Unexpected error in server loop: {e}", exc_info=True)
            break
    
    logger.info("Server shutdown complete")


def main():
    """
    Entry point for MCP server.
    
    ADK pattern: Clean entry point with proper async setup.
    """
    try:
        asyncio.run(run_server())
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
