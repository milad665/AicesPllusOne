import json
import subprocess
import sys

def call_mcp_method(method, params=None):
    """Call an MCP method via JSON-RPC"""
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
        text=True
    )
    
    # Send request
    request_str = json.dumps(request) + '\n'
    stdout, stderr = process.communicate(input=request_str, timeout=60)
    
    # Print stderr for debugging
    if stderr:
        print("=== SERVER LOG ===", file=sys.stderr)
        for line in stderr.split('\n'):
            if line.strip():
                print(line, file=sys.stderr)
        print("==================", file=sys.stderr)
    
    # Parse response
    lines = stdout.strip().split('\n')
    for line in lines:
        if line.strip():
            try:
                return json.loads(line)
            except json.JSONDecodeError:
                continue
    
    return None

# Test get_c4_architecture tool
print("Calling get_c4_architecture tool via MCP server...")
result = call_mcp_method("tools/call", {
    "name": "get_c4_architecture",
    "arguments": {"force_refresh": False}  # Use cached version if available
})

if result:
    if "error" in result:
        print(f"\n❌ ERROR: {result['error']}")
    elif "result" in result:
        print("\n✅ SUCCESS!")
        content = result["result"].get("content", [])
        if content and len(content) > 0:
            # Parse the architecture from the response
            arch_text = content[0].get("text", "")
            if arch_text:
                try:
                    arch = json.loads(arch_text)
                    print(f"\nContext View:")
                    print(f"  - Systems: {len(arch.get('ContextView', {}).get('SoftwareSystems', []))}")
                    print(f"  - Actors: {len(arch.get('ContextView', {}).get('Actors', []))}")
                    print(f"\nContainer View:")
                    print(f"  - Containers: {len(arch.get('ContainerView', {}).get('Containers', []))}")
                    print(f"\nComponent View:")
                    print(f"  - Components: {len(arch.get('ComponentView', {}).get('Components', []))}")
                    print(f"\nExplanation: {arch.get('ArchitectureExplanation', 'N/A')[:100]}...")
                except json.JSONDecodeError:
                    print(f"\nArchitecture data (first 500 chars):\n{arch_text[:500]}")
        else:
            print(f"\nFull result: {json.dumps(result, indent=2)}")
else:
    print("\n❌ No response received from server")

