#!/usr/bin/env python3
"""
Example script showing how to use the Git Repository Manager API
"""

import requests
import json
from pathlib import Path


API_BASE = "http://localhost:8000"


def add_repository(name: str, url: str, ssh_private_key_path: str, ssh_public_key_path: str, default_branch: str = "main"):
    """Add a repository to the manager"""
    
    # Read SSH keys
    with open(ssh_private_key_path, 'r') as f:
        private_key = f.read()
    
    with open(ssh_public_key_path, 'r') as f:
        public_key = f.read()
    
    repo_config = {
        "name": name,
        "url": url,
        "ssh_private_key": private_key,
        "ssh_public_key": public_key,
        "default_branch": default_branch
    }
    
    response = requests.post(f"{API_BASE}/repositories", json=repo_config)
    
    if response.status_code == 200:
        print(f"Repository '{name}' added successfully!")
        print(f"Repository ID: {response.json()['repository_id']}")
    else:
        print(f"Error adding repository: {response.text}")


def list_repositories():
    """List all configured repositories"""
    response = requests.get(f"{API_BASE}/repositories")
    
    if response.status_code == 200:
        repos = response.json()
        print(f"Found {len(repos)} repositories:")
        for repo in repos:
            print(f"  - {repo['name']} ({repo['url']}) - Branch: {repo['default_branch']}")
    else:
        print(f"Error listing repositories: {response.text}")


def list_projects():
    """List all analyzed projects"""
    response = requests.get(f"{API_BASE}/projects")
    
    if response.status_code == 200:
        projects = response.json()
        print(f"Found {len(projects)} projects:")
        for project in projects:
            print(f"  - {project['name']} ({project['language']}) - {project['project_type']}")
            print(f"    Files: {project['file_count']}, LoC: {project['lines_of_code']}")
            print(f"    Entry points: {project['entry_points_count']}")
            if project['dependencies']:
                print(f"    Dependencies: {', '.join(project['dependencies'][:5])}...")
            print()
    else:
        print(f"Error listing projects: {response.text}")


def get_project_entrypoints(project_id: str):
    """Get entry points for a specific project"""
    response = requests.get(f"{API_BASE}/projects/{project_id}/entrypoints")
    
    if response.status_code == 200:
        entrypoints = response.json()
        print(f"Entry points for project '{project_id}':")
        for ep in entrypoints:
            print(f"  - {ep['name']} ({ep['type']}) in {ep['file_path']}:{ep['line_number']}")
            if ep['parameters']:
                print(f"    Parameters: {', '.join(ep['parameters'])}")
    else:
        print(f"Error getting entry points: {response.text}")


def trigger_sync():
    """Manually trigger repository synchronization"""
    response = requests.post(f"{API_BASE}/repositories/sync")
    
    if response.status_code == 200:
        print("Repository synchronization triggered successfully!")
    else:
        print(f"Error triggering sync: {response.text}")


def health_check():
    """Check application health"""
    response = requests.get(f"{API_BASE}/health")
    
    if response.status_code == 200:
        health = response.json()
        print("Application is healthy!")
        print(f"Status: {health['status']}")
        print(f"Projects: {health['projects_count']}")
        print(f"Last analysis: {health['last_analysis']}")
    else:
        print(f"Health check failed: {response.text}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python example_client.py add <name> <url> <private_key_path> <public_key_path> [branch]")
        print("  python example_client.py list-repos")
        print("  python example_client.py list-projects")
        print("  python example_client.py entrypoints <project_id>")
        print("  python example_client.py sync")
        print("  python example_client.py health")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "add" and len(sys.argv) >= 6:
        name = sys.argv[2]
        url = sys.argv[3]
        private_key = sys.argv[4]
        public_key = sys.argv[5]
        branch = sys.argv[6] if len(sys.argv) > 6 else "main"
        add_repository(name, url, private_key, public_key, branch)
    
    elif command == "list-repos":
        list_repositories()
    
    elif command == "list-projects":
        list_projects()
    
    elif command == "entrypoints" and len(sys.argv) >= 3:
        project_id = sys.argv[2]
        get_project_entrypoints(project_id)
    
    elif command == "sync":
        trigger_sync()
    
    elif command == "health":
        health_check()
    
    else:
        print("Invalid command or missing arguments")
