#!/usr/bin/env python3
"""
Test script to validate SSH key format and troubleshoot repository cloning
"""

import tempfile
import os
import subprocess
from pathlib import Path

def test_ssh_key_format(ssh_private_key: str):
    """Test if SSH key is in correct format"""
    print("🔐 Testing SSH Key Format...")
    
    # Create temporary SSH key file
    with tempfile.NamedTemporaryFile(mode='w', suffix='_test_key', delete=False) as f:
        key_file = f.name
        f.write(ssh_private_key.strip() + '\n')
    
    try:
        # Set proper permissions
        os.chmod(key_file, 0o600)
        
        # Test SSH key format with ssh-keygen
        result = subprocess.run(
            ['ssh-keygen', '-l', '-f', key_file],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ SSH key format is valid")
            print(f"   Key fingerprint: {result.stdout.strip()}")
            return True
        else:
            print("❌ SSH key format is invalid")
            print(f"   Error: {result.stderr.strip()}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing SSH key: {e}")
        return False
    finally:
        # Clean up
        try:
            os.remove(key_file)
        except:
            pass

def test_github_connection(ssh_private_key: str):
    """Test connection to GitHub with the SSH key"""
    print("\n🌐 Testing GitHub Connection...")
    
    # Create temporary SSH key file
    with tempfile.NamedTemporaryFile(mode='w', suffix='_test_key', delete=False) as f:
        key_file = f.name
        f.write(ssh_private_key.strip() + '\n')
    
    try:
        # Set proper permissions
        os.chmod(key_file, 0o600)
        
        # Test connection to GitHub
        ssh_cmd = [
            'ssh', '-i', key_file,
            '-o', 'StrictHostKeyChecking=no',
            '-o', 'UserKnownHostsFile=/dev/null',
            '-o', 'ConnectTimeout=10',
            '-T', 'git@github.com'
        ]
        
        result = subprocess.run(ssh_cmd, capture_output=True, text=True)
        
        # GitHub SSH test returns exit code 1 but with success message
        if "successfully authenticated" in result.stderr:
            print("✅ GitHub SSH authentication successful")
            return True
        else:
            print("❌ GitHub SSH authentication failed")
            print(f"   stdout: {result.stdout}")
            print(f"   stderr: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing GitHub connection: {e}")
        return False
    finally:
        # Clean up
        try:
            os.remove(key_file)
        except:
            pass

if __name__ == "__main__":
    print("🔧 SSH Key Troubleshooting Tool")
    print("=" * 50)
    
    # Get the SSH key from the current repository in the database
    import requests
    import json
    
    try:
        response = requests.get("http://localhost:8000/repositories")
        repositories = response.json()
        
        if not repositories:
            print("❌ No repositories found in the system")
            exit(1)
        
        repo = repositories[0]
        print(f"📁 Testing repository: {repo['name']}")
        print(f"🔗 URL: {repo['url']}")
        
        # We can't get the actual SSH key from the API (it's hidden)
        # So we'll provide instructions for manual testing
        print("\n💡 To test your SSH key manually:")
        print("1. Save your SSH private key to a temporary file")
        print("2. Run: chmod 600 /path/to/your/key")
        print("3. Test key format: ssh-keygen -l -f /path/to/your/key")
        print("4. Test GitHub connection: ssh -i /path/to/your/key -T git@github.com")
        print("5. Test repository access: git clone git@github.com:mmramezani/Mo.ProjectFilesToJson.git /tmp/test_clone")
        
        print("\n🔍 Common SSH key issues:")
        print("• Key missing newline at the end")
        print("• Wrong key format (needs to be OpenSSH format)")
        print("• Key not added to GitHub account")
        print("• Repository doesn't exist or you don't have access")
        
    except Exception as e:
        print(f"❌ Error getting repository info: {e}")
