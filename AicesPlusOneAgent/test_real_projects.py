import asyncio
from src.code_analyzer import CodeAnalyzer

async def test():
    analyzer = CodeAnalyzer()
    
    print("Fetching projects from code analyzer service...")
    projects = await analyzer.get_projects()
    
    print(f"\n✅ Found {len(projects)} projects:\n")
    for i, proj in enumerate(projects, 1):
        print(f"{i}. {proj.get('name', 'Unknown')}")
        print(f"   ID: {proj.get('id')}")
        print(f"   Language: {proj.get('language')}")
        print(f"   Type: {proj.get('project_type')}")
        print(f"   Description: {proj.get('description', 'N/A')}")
        print(f"   Files: {proj.get('file_count', 0)}, LOC: {proj.get('lines_of_code', 0)}")
        print(f"   Entry points: {proj.get('entry_points_count', 0)}")
        print()
    
    # Get entrypoints for first project if available
    if projects and projects[0].get('id'):
        proj_id = projects[0]['id']
        print(f"Fetching entrypoints for project '{projects[0].get('name')}'...")
        try:
            entrypoints = await analyzer.get_project_entrypoints(proj_id)
            print(f"✅ Found {len(entrypoints)} entrypoints:")
            for ep in entrypoints[:5]:  # Show first 5
                print(f"  - {ep.get('name')} ({ep.get('type')}) in {ep.get('file_path')}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    await analyzer.close()

if __name__ == "__main__":
    asyncio.run(test())
