"""
Setup script to add repositories to the code analyzer service
"""
import asyncio
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

CODE_ANALYZER_URL = os.getenv(
    "CODE_ANALYSIS_API_URL",
    "https://aices-plus-one-analyzer-691085128403.europe-west1.run.app"
)

async def add_repository(name: str, url: str, ssh_private_key: str, ssh_public_key: str):
    """Add a repository to the code analyzer"""
    async with httpx.AsyncClient(base_url=CODE_ANALYZER_URL, timeout=60.0) as client:
        payload = {
            "name": name,
            "url": url,
            "ssh_private_key": ssh_private_key,
            "ssh_public_key": ssh_public_key,
            "default_branch": "main"
        }
        
        print(f"Adding repository: {name}")
        print(f"URL: {url}")
        
        response = await client.post("/repositories", json=payload)
        response.raise_for_status()
        
        result = response.json()
        print(f"✅ Repository added with ID: {result}")
        
        return result

async def sync_repositories():
    """Trigger repository synchronization"""
    async with httpx.AsyncClient(base_url=CODE_ANALYZER_URL, timeout=300.0) as client:
        print("\nTriggering repository sync...")
        response = await client.post("/repositories/sync")
        response.raise_for_status()
        
        print("✅ Sync initiated")
        
        # Wait a bit for sync to complete
        print("Waiting for sync to complete (30 seconds)...")
        await asyncio.sleep(30)

async def check_projects():
    """Check what projects are available"""
    async with httpx.AsyncClient(base_url=CODE_ANALYZER_URL, timeout=60.0) as client:
        response = await client.get("/projects")
        response.raise_for_status()
        
        projects = response.json()
        print(f"\n✅ Found {len(projects)} projects:")
        for proj in projects:
            print(f"  - {proj.get('name')} ({proj.get('language')}) - {proj.get('project_type')}")
        
        return projects

async def main():
    print("=== Code Analyzer Repository Setup ===\n")
    print("This script will help you add repositories to the code analyzer service.")
    print("You'll need SSH keys for private repositories.\n")
    
    # Example: Add this current project
    print("Example: Adding AicesPlusOneAgent repository (this project)")
    print("\nNote: For public repos, you can use dummy SSH keys.")
    print("For private repos, provide actual SSH keys.\n")
    
    choice = input("Would you like to add this project as a repository? (y/n): ")
    
    if choice.lower() == 'y':
        # For a local directory, we'd need to push it to a git remote first
        repo_url = input("Enter the git repository URL (e.g., https://github.com/user/repo.git): ")
        
        # For public repos, we can use empty keys
        use_ssh = input("Is this a private repository requiring SSH keys? (y/n): ")
        
        if use_ssh.lower() == 'y':
            print("\nPaste your SSH private key (multi-line, end with Ctrl+D on a new line):")
            ssh_private = ""
            try:
                while True:
                    line = input()
                    ssh_private += line + "\n"
            except EOFError:
                pass
            
            ssh_public = input("\nEnter your SSH public key: ")
        else:
            # For public repos over HTTPS
            ssh_private = "dummy-key"
            ssh_public = "dummy-key"
        
        repo_name = input("Enter a name for this repository: ")
        
        try:
            await add_repository(repo_name, repo_url, ssh_private, ssh_public)
            await sync_repositories()
            await check_projects()
        except Exception as e:
            print(f"\n❌ Error: {e}")
    else:
        print("\nSkipping repository setup.")
        print("You can manually add repositories via the API:")
        print(f"POST {CODE_ANALYZER_URL}/repositories")
    
    print("\n=== Checking current projects ===")
    await check_projects()

if __name__ == "__main__":
    asyncio.run(main())
