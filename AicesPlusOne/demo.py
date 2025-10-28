#!/usr/bin/env python3
"""
Demo script showing how to use the Git Repository Manager API
"""

import requests
import json
import time

API_BASE = "http://localhost:8000"

def demo_basic_functionality():
    """Demonstrate basic API functionality"""
    print("🚀 Git Repository Manager Demo\n")
    
    # Check health
    print("1. Checking application health...")
    response = requests.get(f"{API_BASE}/health")
    if response.status_code == 200:
        health = response.json()
        print(f"   ✓ Status: {health['status']}")
        print(f"   ✓ Projects: {health['projects_count']}")
    else:
        print(f"   ❌ Health check failed: {response.status_code}")
        return
    
    # List repositories (should be empty initially)
    print("\n2. Listing repositories...")
    response = requests.get(f"{API_BASE}/repositories")
    repos = response.json()
    print(f"   ✓ Found {len(repos)} repositories")
    
    # List projects (should be empty initially)
    print("\n3. Listing projects...")
    response = requests.get(f"{API_BASE}/projects")
    projects = response.json()
    print(f"   ✓ Found {len(projects)} projects")
    
    print("\n📝 To add a repository, you need:")
    print("   - Repository name")
    print("   - Git URL (SSH format)")
    print("   - SSH private key")
    print("   - SSH public key")
    print("   - Default branch (optional, defaults to 'main')")
    
    print("\n🔧 Example using curl:")
    print("""
curl -X POST "http://localhost:8000/repositories" \\
     -H "Content-Type: application/json" \\
     -d '{
       "name": "my-project",
       "url": "git@github.com:user/repo.git",
       "ssh_private_key": "-----BEGIN OPENSSH PRIVATE KEY-----\\n...\\n-----END OPENSSH PRIVATE KEY-----",
       "ssh_public_key": "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAI...",
       "default_branch": "main"
     }'
    """)
    
    print("\n📊 API Endpoints:")
    print("   GET  /health - Application health check")
    print("   GET  /repositories - List repositories")
    print("   POST /repositories - Add repository")
    print("   GET  /projects - List analyzed projects")
    print("   GET  /projects/{id}/entrypoints - Get entry points")
    print("   POST /repositories/sync - Trigger manual sync")
    
    print("\n🌐 Open http://localhost:8000/docs for interactive API documentation")

def demo_with_sample_repository():
    """Demo with a sample repository (requires SSH keys)"""
    print("\n🔐 To demo with a real repository:")
    print("1. Generate SSH keys: ssh-keygen -t ed25519 -f ~/.ssh/demo_key")
    print("2. Add the public key to your GitHub/GitLab account")
    print("3. Use the example_client.py script:")
    print("   python3 example_client.py add my-repo git@github.com:user/repo.git ~/.ssh/demo_key ~/.ssh/demo_key.pub")

if __name__ == "__main__":
    try:
        demo_basic_functionality()
        demo_with_sample_repository()
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to the API. Make sure the server is running:")
        print("   python3 dev_server.py")
    except Exception as e:
        print(f"❌ Error: {e}")
