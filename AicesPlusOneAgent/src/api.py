import uvicorn
from fastapi import FastAPI
import os

app = FastAPI(title="Debug API")

@app.get("/")
def root():
    return {"status": "ok", "message": "Minimal API running"}

@app.get("/env")
def dump_env():
    # Return env vars (masked) to verify they exist
    return {
        "GCS_BUCKET_NAME": os.getenv("GCS_BUCKET_NAME", "MISSING"),
        "GOOGLE_CLOUD_PROJECT": os.getenv("GOOGLE_CLOUD_PROJECT", "MISSING"),
        "STORAGE_TYPE": os.getenv("STORAGE_TYPE", "MISSING"),
        "GOOGLE_API_KEY_EXISTS": "YES" if os.getenv("GOOGLE_API_KEY") else "NO"
    }

if __name__ == "__main__":
    uvicorn.run("src.api:app", host="0.0.0.0", port=8001)
