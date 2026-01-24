import os
import uvicorn
from fastapi import FastAPI, HTTPException, Body, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from fastapi import Header
import shutil
import traceback

# Import Schemas (usually safe)
# from .schemas import C4Architecture
# from .tenancy.models import Tenant, CreateTenantRequest, UpdateTenantConfigRequest

app = FastAPI(title="C4 Architecture Agent API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global agent instance
agent: Any = None

# startup_event REMOVED to prevent boot-time hangs/crashes.
# Agent is initialized lazily or via /api/debug/init

@app.get("/api/debug/init")
async def debug_init():
    """Force initialize agent and return details."""
    global agent
    try:
        print("Lazy importing C4ArchitectureAgent...")
        from .agent import C4ArchitectureAgent
        
        print("Initializing C4ArchitectureAgent...")
        agent = C4ArchitectureAgent()
        return {"status": "success", "message": "Agent initialized"}
    except Exception as e:
        print(f"Agent Init Failed: {e}")
        traceback.print_exc()
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc()
        }

@app.get("/health")
async def health_check():
    return {"status": "ok", "agent_status": "active" if agent else "inactive"}

# Wrapper to safely access agent
# def get_agent():
#     if not agent:
#         raise HTTPException(status_code=503, detail="Agent not initialized. Check /api/debug/init logs.")
#     return agent

# @app.get("/api/architecture", response_model=Optional[C4Architecture])
# async def get_architecture(x_tenant_id: str = Header("default_tenant", alias="X-Tenant-ID")):
#     return await get_agent().get_current_architecture(tenant_id=x_tenant_id)
# 
# @app.post("/api/architecture/regenerate", response_model=C4Architecture)
# async def regenerate_architecture(x_tenant_id: str = Header("default_tenant", alias="X-Tenant-ID")):
#     try:
#         return await get_agent().generate_c4_architecture(tenant_id=x_tenant_id)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
# 
# class UpdateRequest(BaseModel):
#     plantuml_script: str
#     view_type: str = "all"
# 
# @app.post("/api/architecture/update", response_model=C4Architecture)
# async def update_architecture(request: UpdateRequest, x_tenant_id: str = Header("default_tenant", alias="X-Tenant-ID")):
#     try:
#         return await get_agent().update_from_plantuml(
#             plantuml_script=request.plantuml_script,
#             view_type=request.view_type,
#             tenant_id=x_tenant_id
#         )
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
# 
# class IdentifyRequest(BaseModel):
#     file_path: str
# 
# @app.post("/api/context/identify")
# async def identify_context(request: IdentifyRequest, x_tenant_id: str = Header("default_tenant", alias="X-Tenant-ID")):
#     result = await get_agent().find_relevant_element(request.file_path, tenant_id=x_tenant_id)
#     if not result:
#         return {"found": False}
#     return {"found": True, **result}
# 
# # --- Tenant Management API ---
# 
# @app.post("/api/tenants", response_model=Tenant)
# async def create_tenant(request: CreateTenantRequest):
#     return get_agent().tenant_manager.create_tenant(request.name, request.subscription_tier)
# 
# @app.get("/api/tenants", response_model=List[Tenant])
# async def list_tenants():
#     return get_agent().tenant_manager.list_tenants()
# 
# @app.get("/api/tenants/{tenant_id}", response_model=Tenant)
# async def get_tenant(tenant_id: str):
#     tenant = get_agent().tenant_manager.get_tenant(tenant_id)
#     if not tenant:
#         raise HTTPException(status_code=404, detail="Tenant not found")
#     return tenant
# 
# @app.put("/api/tenants/{tenant_id}/config", response_model=Tenant)
# async def update_tenant_config(tenant_id: str, updates: UpdateTenantConfigRequest):
#     tenant = get_agent().tenant_manager.update_tenant_config(tenant_id, updates)
#     if not tenant:
#         raise HTTPException(status_code=404, detail="Tenant not found")
#     return tenant
# 
# @app.post("/api/tenants/{tenant_id}/certificates")
# async def upload_certificates(
#     tenant_id: str,
#     client_cert: UploadFile = File(None),
#     client_key: UploadFile = File(None),
#     ca_cert: UploadFile = File(None)
# ):
#     agt = get_agent()
#     tenant = agt.tenant_manager.get_tenant(tenant_id)
#     if not tenant:
#         raise HTTPException(status_code=404, detail="Tenant not found")
#         
#     cert_dir = f"data/{tenant_id}/certs"
#     os.makedirs(cert_dir, exist_ok=True)
#     
#     paths = {}
#     if client_cert:
#         path = f"{cert_dir}/client.crt"
#         with open(path, "wb") as buffer:
#             shutil.copyfileobj(client_cert.file, buffer)
#         paths['client_cert'] = path
#     if client_key:
#         path = f"{cert_dir}/client.key"
#         with open(path, "wb") as buffer:
#             shutil.copyfileobj(client_key.file, buffer)
#         paths['client_key'] = path
#     if ca_cert:
#         path = f"{cert_dir}/ca.crt"
#         with open(path, "wb") as buffer:
#             shutil.copyfileobj(ca_cert.file, buffer)
#         paths['ca_cert'] = path
#         
#     agt.tenant_manager.update_certificates(
#         tenant_id, 
#         client_cert=paths.get('client_cert'),
#         client_key=paths.get('client_key'),
#         ca_cert=paths.get('ca_cert')
#     )
#     return {"status": "success", "updated_paths": paths}
# 
# @app.get("/api/admin/stats")
# async def get_admin_stats():
#     agt = get_agent()
#     tenants = agt.tenant_manager.list_tenants()
#     return {
#         "total_tenants": len(tenants),
#         "total_revenue": sum([99.0 for t in tenants if t.subscription_tier == "pro"]), 
#         "active_tenants": len(tenants),
#         "system_status": "healthy"
#     }

# UI Static Files
# ui_dist_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../ui/dist"))
# if not os.path.exists(ui_dist_path):
#     ui_dist_path = "/app/ui/dist"
# 
# if os.path.exists(ui_dist_path):
#     print(f"Serving static UI from {ui_dist_path}")
#     app.mount("/", StaticFiles(directory=ui_dist_path, html=True), name="ui")
# else:
#     print(f"UI build directory not found at {ui_dist_path}. Running in API-only mode.")

def start():
    uvicorn.run("src.api:app", host="0.0.0.0", port=8080, reload=True)

if __name__ == "__main__":
    start()
