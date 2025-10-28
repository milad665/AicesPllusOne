import json
import subprocess
import sys

def call_mcp_tool(method, params=None):
    """Call an MCP tool via JSON-RPC"""
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params or {}
    }
    
    # Run the server
    process = subprocess.Popen(
        ['.venv/bin/python', '-m', 'src.server'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=0
    )
    
    # Send request
    request_str = json.dumps(request) + '\n'
    stdout, stderr = process.communicate(input=request_str, timeout=30)
    
    # Print any stderr output
    if stderr:
        print("=== STDERR ===", file=sys.stderr)
        print(stderr, file=sys.stderr)
        print("=============", file=sys.stderr)
    
    # Parse response
    lines = stdout.strip().split('\n')
    for line in lines:
        if line.strip():
            try:
                response = json.loads(line)
                return response
            except json.JSONDecodeError:
                continue
    
    return None

# Test get_c4_architecture
print("Testing get_c4_architecture...")
result = call_mcp_tool("tools/call", {
    "name": "get_c4_architecture",
    "arguments": {"force_refresh": True}
})

if result:
    print(json.dumps(result, indent=2))
else:
    print("No response received")
