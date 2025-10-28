#!/usr/bin/env python3
"""
CLI interface for the C4 Architecture Agent

This provides a simple command-line interface to test the agent
without running it as an MCP server.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.agent import C4ArchitectureAgent


async def main():
    """Main CLI function"""
    print("C4 Architecture Agent - CLI Interface")
    print("=" * 50)
    
    # Initialize agent
    agent = C4ArchitectureAgent()
    
    try:
        # Generate C4 architecture
        print("\n🔄 Generating C4 architecture from code analysis...")
        architecture = await agent.generate_c4_architecture(force_refresh=True)
        
        print("\n✅ Architecture generated successfully!")
        print(f"\n📊 Summary:")
        print(f"  - Systems: {len(architecture.ContextView.SoftwareSystems)}")
        print(f"  - Containers: {len(architecture.ContainerView.Containers)}")
        print(f"  - Components: {len(architecture.ComponentView.Components)}")
        
        # Save to file
        output_file = Path("data/c4_architecture.json")
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(architecture.model_dump(mode='json'), f, indent=2)
        
        print(f"\n💾 Architecture saved to: {output_file}")
        
        # Display explanation
        print(f"\n📝 Architecture Explanation:")
        print(f"  {architecture.ArchitectureExplanation}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await agent.close()


if __name__ == "__main__":
    asyncio.run(main())
