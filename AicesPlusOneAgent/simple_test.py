import asyncio
import sys
from src.agent import C4ArchitectureAgent

async def test():
    print("Creating agent...")
    agent = C4ArchitectureAgent()
    
    print("Generating C4 architecture (this may take a minute)...")
    try:
        architecture = await agent.generate_c4_architecture(force_refresh=True)
        print("\n=== SUCCESS ===")
        print(f"Context View has {len(architecture.ContextView.SoftwareSystems)} systems")
        print(f"Container View has {len(architecture.ContainerView.Containers)} containers")
        print(f"Component View has {len(architecture.ComponentView.Components)} components")
        print(f"\nArchitecture Explanation: {architecture.ArchitectureExplanation[:200]}...")
    except Exception as e:
        print(f"\n=== ERROR ===")
        print(f"Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await agent.close()

if __name__ == "__main__":
    asyncio.run(test())
