"""
Example usage of the C4 Architecture Agent MCP Server

This demonstrates how to use the agent both directly and via MCP.
"""

import asyncio
import json
from src.agent import C4ArchitectureAgent


async def example_direct_usage():
    """Example of using the agent directly"""
    print("=== Direct Agent Usage Example ===\n")
    
    agent = C4ArchitectureAgent()
    
    try:
        # Generate architecture
        print("1. Generating C4 architecture...")
        architecture = await agent.generate_c4_architecture(force_refresh=True)
        print(f"   ✓ Generated with {len(architecture.ContextView.SoftwareSystems)} systems")
        
        # Get current architecture
        print("\n2. Getting current architecture from memory...")
        current = await agent.get_current_architecture()
        if current:
            print(f"   ✓ Retrieved from memory")
        
        # Update from PlantUML (example)
        print("\n3. Updating from PlantUML script...")
        plantuml_example = """
@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Context.puml

Person(user, "User", "End User")
System(system, "Main System", "Primary software system")
Rel(user, system, "Uses")

@enduml
"""
        updated = await agent.update_from_plantuml(plantuml_example, "context")
        print(f"   ✓ Updated context view")
        
        # Display results
        print("\n4. Final Architecture Summary:")
        print(f"   - Context View: {len(updated.ContextView.SoftwareSystems)} systems, {len(updated.ContextView.Actors)} actors")
        print(f"   - Container View: {len(updated.ContainerView.Containers)} containers")
        print(f"   - Component View: {len(updated.ComponentView.Components)} components")
        
    finally:
        await agent.close()


async def example_mcp_client():
    """Example of how an MCP client would interact with the server"""
    print("\n\n=== MCP Client Usage Example ===\n")
    
    print("To use the MCP server, configure your MCP client with:")
    print("""
{
  "mcpServers": {
    "c4-architecture": {
      "command": "python",
      "args": ["/Users/milad/Developer/AicesPlusOneAgent/src/server.py"]
    }
  }
}
""")
    
    print("\nAvailable MCP Tools:")
    print("1. get_c4_architecture")
    print("   - Get the latest C4 architecture diagram in JSON")
    print("   - Arguments: { force_refresh: boolean }")
    
    print("\n2. update_c4_architecture")
    print("   - Update C4 architecture from PlantUML")
    print("   - Arguments: { plantuml_script: string, view_type: string }")


if __name__ == "__main__":
    asyncio.run(example_direct_usage())
    asyncio.run(example_mcp_client())
