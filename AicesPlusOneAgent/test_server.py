#!/usr/bin/env python3
"""
Test script for the MCP server
"""
import asyncio
import json
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.server import ADKMCPServer


async def test_server():
    """Test the MCP server functionality"""
    print("Testing MCP Server...")
    
    server = ADKMCPServer()
    
    # Test 1: Initialize request
    print("\n1. Testing initialize request...")
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        }
    }
    
    response = await server.handle_request(init_request)
    print(f"Initialize response: {json.dumps(response, indent=2)}")
    
    # Test 2: List tools
    print("\n2. Testing tools/list request...")
    list_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list"
    }
    
    response = await server.handle_request(list_request)
    print(f"Tools list response: {json.dumps(response, indent=2)}")
    
    # Test 3: Call get_c4_architecture tool (this might take a while)
    print("\n3. Testing get_c4_architecture tool...")
    try:
        call_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "get_c4_architecture",
                "arguments": {
                    "force_refresh": True
                }
            }
        }
        
        response = await server.handle_request(call_request)
        print(f"Tool call response: {json.dumps(response, indent=2)[:500]}...")
    except Exception as e:
        print(f"Tool call failed (expected if no API key): {e}")
    
    print("\nServer test completed!")


if __name__ == "__main__":
    asyncio.run(test_server())