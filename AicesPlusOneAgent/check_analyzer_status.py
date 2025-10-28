"""
Quick demonstration of the full workflow
"""
import asyncio
import httpx

CODE_ANALYZER_URL = "https://aices-plus-one-analyzer-691085128403.europe-west1.run.app"

async def check_status():
    """Check the current status of the code analyzer"""
    async with httpx.AsyncClient(base_url=CODE_ANALYZER_URL, timeout=30.0) as client:
        print("=" * 60)
        print("CODE ANALYZER SERVICE STATUS")
        print("=" * 60)
        
        # Check repositories
        try:
            resp = await client.get("/repositories")
            repos = resp.json()
            print(f"\n📁 Repositories: {len(repos)}")
            for repo in repos:
                print(f"   - {repo.get('name')} ({repo.get('url')})")
        except Exception as e:
            print(f"\n❌ Error fetching repositories: {e}")
        
        # Check projects
        try:
            resp = await client.get("/projects")
            projects = resp.json()
            print(f"\n📦 Projects: {len(projects)}")
            
            if len(projects) == 0:
                print("\n⚠️  NO PROJECTS FOUND")
                print("\nTo use this system, you need to:")
                print("1. Add a git repository to the code analyzer")
                print("2. Sync the repositories")
                print("3. Wait for analysis to complete")
                print("\nSee README_USAGE.md for instructions.")
            else:
                for proj in projects:
                    print(f"\n   {proj.get('name')}:")
                    print(f"      Language: {proj.get('language')}")
                    print(f"      Type: {proj.get('project_type')}")
                    print(f"      Files: {proj.get('file_count')}, LOC: {proj.get('lines_of_code')}")
                    print(f"      Entry Points: {proj.get('entry_points_count')}")
        except Exception as e:
            print(f"\n❌ Error fetching projects: {e}")
        
        print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(check_status())
