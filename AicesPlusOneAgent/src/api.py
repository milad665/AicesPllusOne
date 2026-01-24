import os
import uvicorn
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from fastapi import UploadFile, File
import shutil
import os

from .agent import C4ArchitectureAgent
from .schemas import C4Architecture
from .tenancy.models import Tenant, CreateTenantRequest, UpdateTenantConfigRequest
from fastapi import Header

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
        print("Attempting to initialize C4ArchitectureAgent...")
        agent = C4ArchitectureAgent()
        print("C4ArchitectureAgent initialized successfully")
    except Exception as e:
        print(f"Failed to initialize agent (Safe Mode Active): {e}")
        # We allow startup to continue so we can debug via /api/debug/init

@app.get("/api/debug/init")
async def debug_init():
    """Force initialize agent and return details."""
    global agent
    import traceback
    try:
        agent = C4ArchitectureAgent()
        return {"status": "success", "message": "Agent initialized"}
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc()
        }

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/api/architecture", response_model=Optional[C4Architecture])
async def get_architecture(x_tenant_id: str = Header("default_tenant", alias="X-Tenant-ID")):
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    return await agent.get_current_architecture(tenant_id=x_tenant_id)

@app.post("/api/architecture/regenerate", response_model=C4Architecture)
async def regenerate_architecture(x_tenant_id: str = Header("default_tenant", alias="X-Tenant-ID")):
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    try:
        return await agent.generate_c4_architecture(tenant_id=x_tenant_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class UpdateRequest(BaseModel):
    plantuml_script: str
    view_type: str = "all"

@app.post("/api/architecture/update", response_model=C4Architecture)
async def update_architecture(request: UpdateRequest, x_tenant_id: str = Header("default_tenant", alias="X-Tenant-ID")):
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    try:
        return await agent.update_from_plantuml(
            plantuml_script=request.plantuml_script,
            view_type=request.view_type,
            tenant_id=x_tenant_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class IdentifyRequest(BaseModel):
    file_path: str

@app.post("/api/context/identify")
async def identify_context(request: IdentifyRequest, x_tenant_id: str = Header("default_tenant", alias="X-Tenant-ID")):
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    result = await agent.find_relevant_element(request.file_path, tenant_id=x_tenant_id)
    if not result:
        # Return empty or specific status? 404 might be too harsh for "unknown context"
        return {"found": False}
        
    return {"found": True, **result}

# --- Tenant Management API ---

@app.post("/api/tenants", response_model=Tenant)
async def create_tenant(request: CreateTenantRequest):
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    return agent.tenant_manager.create_tenant(request.name, request.subscription_tier)

@app.get("/api/tenants", response_model=List[Tenant])
async def list_tenants():
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    return agent.tenant_manager.list_tenants()

@app.get("/api/tenants/{tenant_id}", response_model=Tenant)
async def get_tenant(tenant_id: str):
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    tenant = agent.tenant_manager.get_tenant(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant

@app.put("/api/tenants/{tenant_id}/config", response_model=Tenant)
async def update_tenant_config(tenant_id: str, updates: UpdateTenantConfigRequest):
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    tenant = agent.tenant_manager.update_tenant_config(tenant_id, updates)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant

@app.post("/api/tenants/{tenant_id}/certificates")
async def upload_certificates(
    tenant_id: str,
    client_cert: UploadFile = File(None),
    client_key: UploadFile = File(None),
    ca_cert: UploadFile = File(None)
):
    """
    Upload mTLS certificates for a tenant.
    """
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    tenant = agent.tenant_manager.get_tenant(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
        
    # Define storage path for certs
    cert_dir = f"data/{tenant_id}/certs"
    os.makedirs(cert_dir, exist_ok=True)
    
    paths = {}
    
    # Save files
    if client_cert:
        path = f"{cert_dir}/client.crt"
        with open(path, "wb") as buffer:
            shutil.copyfileobj(client_cert.file, buffer)
        paths['client_cert'] = path
        
    if client_key:
        path = f"{cert_dir}/client.key"
        with open(path, "wb") as buffer:
            shutil.copyfileobj(client_key.file, buffer)
        paths['client_key'] = path
        
    if ca_cert:
        path = f"{cert_dir}/ca.crt"
        with open(path, "wb") as buffer:
            shutil.copyfileobj(ca_cert.file, buffer)
        paths['ca_cert'] = path
        
    # Update tenant config
    updated_tenant = agent.tenant_manager.update_certificates(
        tenant_id, 
        client_cert=paths.get('client_cert'),
        client_key=paths.get('client_key'),
        ca_cert=paths.get('ca_cert')
    )
    
    return {"status": "success", "updated_paths": paths}

@app.get("/api/admin/stats")
async def get_admin_stats():
    """Get global admin statistics."""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
        
    tenants = agent.tenant_manager.list_tenants()
    
    return {
        "total_tenants": len(tenants),
        "total_revenue": sum([99.0 for t in tenants if t.subscription_tier == "pro"]), # Mock
        "active_tenants": len(tenants), # Mock
        "system_status": "healthy"
    }


# Serve Static Files (Frontend)
# In Docker, we copy built UI to /app/ui/dist
# We check relative to current file or absolute path
from fastapi.staticfiles import StaticFiles

# Resolve path to UI dist
# 1. Docker path: /app/ui/dist
# 2. Local dev path (if built): ../ui/dist ? (Usually dev uses Vite dev server, so this is mostly for Prod Docker)
ui_dist_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../ui/dist"))
if not os.path.exists(ui_dist_path):
    # Fallback to absolute Docker path
    ui_dist_path = "/app/ui/dist"

if os.path.exists(ui_dist_path):
    print(f"Serving static UI from {ui_dist_path}")
    app.mount("/", StaticFiles(directory=ui_dist_path, html=True), name="ui")
else:
    print(f"UI build directory not found at {ui_dist_path}. Running in API-only mode.")


def start():
    """Entry point for running the API server"""
    uvicorn.run("src.api:app", host="0.0.0.0", port=8001, reload=True)

if __name__ == "__main__":
    start()
