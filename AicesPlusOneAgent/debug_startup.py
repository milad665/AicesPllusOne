import os
import sys
from google.cloud import storage
import google.generativeai as genai

def debug_gcs():
    print("\n--- Debugging GCS ---")
    bucket_name = os.getenv("GCS_BUCKET_NAME")
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    
    print(f"GCS_BUCKET_NAME: {bucket_name}")
    print(f"GOOGLE_CLOUD_PROJECT: {project_id}")
    
    if not bucket_name:
        print("SKIP: GCS_BUCKET_NAME not set")
        return

    try:
        if project_id:
            print(f"Initializing Storage Client with project={project_id}")
            client = storage.Client(project=project_id)
        else:
            print("Initializing Storage Client (default)")
            client = storage.Client()
            
        print(f"Client Project: {client.project}")
        
        bucket = client.bucket(bucket_name)
        print(f"Checking bucket {bucket_name} exists...")
        exists = bucket.exists()
        print(f"Bucket exists: {exists}")
        
    except Exception as e:
        print(f"ERROR in GCS: {e}")
        import traceback
        traceback.print_exc()

def debug_gemini():
    print("\n--- Debugging Gemini ---")
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("SKIP: GOOGLE_API_KEY not set")
        return
        
    print(f"API Key Length: {len(api_key)}")
    print(f"API Key Prefix: {api_key[:4]}...")
    
    try:
        print("Configuring Gemini...")
        genai.configure(api_key=api_key)
        
        print("Initializing Model...")
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        print("Testing Generation...")
        response = model.generate_content("Hello")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"ERROR in Gemini: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Starting Debug Script...")
    debug_gcs()
    debug_gemini()
    print("\nDebug Script Complete.")
