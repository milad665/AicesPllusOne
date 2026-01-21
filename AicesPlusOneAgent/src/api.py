import os
import uvicorn
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

from .agent import C4ArchitectureAgent
from .schemas import C4Architecture

app = FastAPI(title="C4 Architecture Agent API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global agent instance
agent: Optional[C4ArchitectureAgent] = None

@app.on_event("startup")
async def startup_event():
    global agent
    try:
        agent = C4ArchitectureAgent()
        print("C4ArchitectureAgent initialized successfully")
    except Exception as e:
        print(f"Failed to initialize agent: {e}")
        # We don't raise here to allow the server to start even if agent fails config
        # Individual endpoints will handle the missing agent

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/api/architecture", response_model=Optional[C4Architecture])
async def get_architecture():
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    return await agent.get_current_architecture()

@app.post("/api/architecture/regenerate", response_model=C4Architecture)
async def regenerate_architecture():
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    try:
        return await agent.generate_c4_architecture()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class UpdateRequest(BaseModel):
    plantuml_script: str
    view_type: str = "all"

@app.post("/api/architecture/update", response_model=C4Architecture)
async def update_architecture(request: UpdateRequest):
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    try:
        return await agent.update_from_plantuml(
            plantuml_script=request.plantuml_script,
            view_type=request.view_type
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class IdentifyRequest(BaseModel):
    file_path: str

@app.post("/api/context/identify")
async def identify_context(request: IdentifyRequest):
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    result = await agent.find_relevant_element(request.file_path)
    if not result:
        # Return empty or specific status? 404 might be too harsh for "unknown context"
        return {"found": False}
        
    return {"found": True, **result}


def start():
    """Entry point for running the API server"""
    uvicorn.run("src.api:app", host="0.0.0.0", port=8001, reload=True)

if __name__ == "__main__":
    start()
