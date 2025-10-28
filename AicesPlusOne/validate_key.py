#!/usr/bin/env python3
"""
Quick SSH Key Validation Tool
"""

import tempfile
import os
import subprocess

def validate_ssh_key():
    """Quick SSH key validation"""
    print("🔑 SSH Key Validator")
    print("===================")
    print("Paste your SSH private key below (Ctrl+D when done):")
    
    try:
        # Read all input
        import sys
        ssh_key = sys.stdin.read().strip()
        
        if not ssh_key:
            print("❌ No SSH key provided")
            return
        
        # Basic format check
        if not ssh_key.startswith("-----BEGIN"):
            print("❌ SSH key must start with -----BEGIN")
            return
            
        if not ssh_key.endswith("-----"):
            print("❌ SSH key must end with -----")
            return
        
        print("✅ Basic format looks correct")
        
        # Write to temporary file and validate
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.pem') as f:
            # Ensure proper formatting
            lines = ssh_key.split('\n')
            formatted_lines = [line.strip() for line in lines if line.strip()]
            formatted_key = '\n'.join(formatted_lines) + '\n'
            
            f.write(formatted_key)
            temp_path = f.name
        
        try:
            os.chmod(temp_path, 0o600)
            
            # Validate with ssh-keygen
            result = subprocess.run(['ssh-keygen', '-l', '-f', temp_path], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ SSH key is valid!")
                print(f"Fingerprint: {result.stdout.strip()}")
                
                # Test connection to GitHub
                print("\n🌐 Testing GitHub connection...")
                github_result = subprocess.run([
                    'ssh', '-i', temp_path, 
                    '-o', 'StrictHostKeyChecking=no',
                    '-o', 'UserKnownHostsFile=/dev/null',
                    '-o', 'LogLevel=ERROR',
                    '-T', 'git@github.com'
                ], capture_output=True, text=True, timeout=10)
                
                if "successfully authenticated" in github_result.stderr:
                    print("✅ GitHub authentication successful!")
                    print("Your SSH key is properly configured for GitHub.")
                else:
                    print("❌ GitHub authentication failed")
                    print("Make sure the SSH key is added to your GitHub account")
                    
            else:
                print("❌ SSH key validation failed:")
                print(result.stderr)
                
        finally:
            os.unlink(temp_path)
            
    except KeyboardInterrupt:
        print("\nCancelled")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    validate_ssh_key()
