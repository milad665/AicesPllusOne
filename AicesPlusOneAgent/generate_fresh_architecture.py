import asyncio
from src.agent import C4ArchitectureAgent

async def main():
    print("Generating C4 architecture from real project data...\n")
    
    agent = C4ArchitectureAgent()
    
    # Force refresh to generate from actual code analyzer data
    architecture = await agent.generate_c4_architecture(force_refresh=True)
    
    print("\n" + "=" * 60)
    print("C4 ARCHITECTURE GENERATED SUCCESSFULLY")
    print("=" * 60)
    
    print(f"\n📊 Context View:")
    print(f"   - Actors: {len(architecture.ContextView.Actors)}")
    print(f"   - Software Systems: {len(architecture.ContextView.SoftwareSystems)}")
    print(f"   - Relationships: {len(architecture.ContextView.Relationships)}")
    
    print(f"\n📦 Container View:")
    print(f"   - Containers: {len(architecture.ContainerView.Containers)}")
    print(f"   - Relationships: {len(architecture.ContainerView.Relationships)}")
    
    print(f"\n🔧 Component View:")
    print(f"   - Components: {len(architecture.ComponentView.Components)}")
    print(f"   - Relationships: {len(architecture.ComponentView.Relationships)}")
    
    print(f"\n📝 Explanation:")
    print(f"   {architecture.ArchitectureExplanation[:200]}...")
    
    # Show some details
    if architecture.ContextView.SoftwareSystems:
        print(f"\n🏗️  Main System:")
        sys = architecture.ContextView.SoftwareSystems[0]
        print(f"   Name: {sys.Name}")
        print(f"   Description: {sys.Description}")
    
    if architecture.ContainerView.Containers:
        print(f"\n📦 Containers:")
        for cont in architecture.ContainerView.Containers[:3]:
            print(f"   - {cont.Name} ({cont.ContainerTechnology})")
            print(f"     {cont.Description}")
    
    if architecture.ComponentView.Components:
        print(f"\n🔧 Components:")
        for comp in architecture.ComponentView.Components[:5]:
            print(f"   - {comp.Name} ({comp.ComponentTechnology})")
            print(f"     {comp.Description}")
    
    print("\n" + "=" * 60)
    print("Architecture saved to: data/memory.json")
    print("=" * 60)
    
    await agent.close()

if __name__ == "__main__":
    asyncio.run(main())
