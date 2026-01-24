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
from .schemas import C4Architecture
from .tenancy.models import Tenant, CreateTenantRequest, UpdateTenantConfigRequest, SubscriptionStatus, CreditTransaction, CreditTransactionType
from datetime import datetime, timedelta
from fastapi import Depends
from .auth import get_current_tenant, get_current_user

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
def get_agent():
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized. Check /api/debug/init logs.")
    return agent

@app.get("/api/architecture", response_model=Optional[C4Architecture])
async def get_architecture(x_tenant_id: str = Depends(get_current_tenant)):
    return await get_agent().get_current_architecture(tenant_id=x_tenant_id)

@app.post("/api/architecture/regenerate", response_model=C4Architecture)
async def regenerate_architecture(x_tenant_id: str = Depends(get_current_tenant)):
    try:
        return await get_agent().generate_c4_architecture(tenant_id=x_tenant_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class UpdateRequest(BaseModel):
    plantuml_script: str
    view_type: str = "all"

@app.post("/api/architecture/update", response_model=C4Architecture)
async def update_architecture(request: UpdateRequest, x_tenant_id: str = Depends(get_current_tenant)):
    try:
        return await get_agent().update_from_plantuml(
            plantuml_script=request.plantuml_script,
            view_type=request.view_type,
            tenant_id=x_tenant_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class IdentifyRequest(BaseModel):
    file_path: str

@app.post("/api/context/identify")
async def identify_context(request: IdentifyRequest, x_tenant_id: str = Depends(get_current_tenant)):
    result = await get_agent().find_relevant_element(request.file_path, tenant_id=x_tenant_id)
    if not result:
        return {"found": False}
    return {"found": True, **result}

# --- Tenant Management API ---

@app.post("/api/tenants", response_model=Tenant)
async def create_tenant(request: CreateTenantRequest, user = Depends(get_current_user)):
    # Verify user is super admin? For now allow any auth user to create a tenant (self-serve)
    # Ideally check user.get("org_role") == "admin"
    return get_agent().tenant_manager.create_tenant(request.name, request.subscription_tier)

@app.get("/api/tenants", response_model=List[Tenant])
async def list_tenants(user = Depends(get_current_user)):
    # TODO: Filter by user's orgs
    return get_agent().tenant_manager.list_tenants()

@app.get("/api/tenants/{tenant_id}", response_model=Tenant)
async def get_tenant(tenant_id: str, current_tenant_id: str = Depends(get_current_tenant)):
    # Ensure user is accessing their own tenant
    if tenant_id != current_tenant_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this tenant")
        
    tenant = get_agent().tenant_manager.get_tenant(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant

@app.put("/api/tenants/{tenant_id}/config", response_model=Tenant)
async def update_tenant_config(tenant_id: str, updates: UpdateTenantConfigRequest, current_tenant_id: str = Depends(get_current_tenant)):
    if tenant_id != current_tenant_id:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    tenant = get_agent().tenant_manager.update_tenant_config(tenant_id, updates)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant

@app.post("/api/tenants/{tenant_id}/certificates")
async def upload_certificates(
    tenant_id: str,
    client_cert: UploadFile = File(None),
    client_key: UploadFile = File(None),
    ca_cert: UploadFile = File(None),
    current_tenant_id: str = Depends(get_current_tenant)
):
    if tenant_id != current_tenant_id:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    agt = get_agent()
    tenant = agt.tenant_manager.get_tenant(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
        
    cert_dir = f"data/{tenant_id}/certs"
    os.makedirs(cert_dir, exist_ok=True)
    
    paths = {}
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
        
    agt.tenant_manager.update_certificates(
        tenant_id, 
        client_cert=paths.get('client_cert'),
        client_key=paths.get('client_key'),
        ca_cert=paths.get('ca_cert')
    )
    return {"status": "success", "updated_paths": paths}

@app.post("/api/tenants/{tenant_id}/tokens")
async def create_service_token(tenant_id: str, description: str = Body(embed=True), current_tenant_id: str = Depends(get_current_tenant)):
    if tenant_id != current_tenant_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    token = get_agent().tenant_manager.create_service_token(tenant_id, description)
    return {"token": token}

@app.delete("/api/tenants/{tenant_id}/tokens/{token}")
async def revoke_service_token(tenant_id: str, token: str, current_tenant_id: str = Depends(get_current_tenant)):
    if tenant_id != current_tenant_id:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    success = get_agent().tenant_manager.revoke_service_token(tenant_id, token)
    if not success:
        raise HTTPException(status_code=404, detail="Token not found")
    return {"status": "success"}

@app.get("/api/admin/stats")
async def get_admin_stats(user = Depends(get_current_user)):
    # Check for super admin role
    # In Clerk, this is usually stored in public_metadata -> role
    # For now, we allow anyone with "admin" role or specific email
    
    # user payload typically has 'public_metadata' if configured in permission claims
    # OR we can check email
    # user_email = user.get("email", "") # Clerk payload varies based on session token config.
    
    # Simple Admin Gate: Check if user is an admin of the "Platform" org (if you have one)
    # OR just check a hardcoded list for MVP
    
    # For MVP: Allow execution, but ideally we check:
    # if user.get("public_metadata", {}).get("role") != "super_admin":
    #    raise HTTPException(status_code=403, detail="Super Admin access required")
    
    agt = get_agent()
    tenants = agt.tenant_manager.list_tenants()
    
    total_rev = sum([99.0 for t in tenants if t.subscription_tier == "pro"]) + \
                sum([499.0 for t in tenants if t.subscription_tier == "enterprise"])
                
    return {
        "total_tenants": len(tenants),
        "total_revenue": total_rev,
        "active_tenants": len(tenants),
        "system_status": "healthy"
    }

# UI Static Files
ui_dist_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../ui/dist"))
if not os.path.exists(ui_dist_path):
    ui_dist_path = "/app/ui/dist"

if os.path.exists(ui_dist_path):
    print(f"Serving static UI from {ui_dist_path}")
    app.mount("/", StaticFiles(directory=ui_dist_path, html=True), name="ui")
else:
    print(f"UI build directory not found at {ui_dist_path}. Running in API-only mode.")

def start():
    uvicorn.run("src.api:app", host="0.0.0.0", port=8080, reload=True)

# --- Billing API ---

class TrialActivationRequest(BaseModel):
    pass

class PaygActivationRequest(BaseModel):
    stripe_setup_intent_id: str

class CreditAdjustmentRequest(BaseModel):
    amount: float
    description: str

@app.get("/api/billing/status")
async def get_billing_status(current_tenant_id: str = Depends(get_current_tenant)):
    tenant = get_agent().tenant_manager.get_tenant(current_tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
        
    is_eligible_for_trial = not tenant.has_used_trial and tenant.subscription_status == SubscriptionStatus.INACTIVE
    is_eligible_for_welcome_credit = not tenant.has_used_trial and not tenant.has_received_welcome_credit
    
    return {
        "credits_balance": tenant.credits_balance,
        "subscription_status": tenant.subscription_status,
        "trial_expires_at": tenant.trial_expires_at,
        "is_eligible_for_trial": is_eligible_for_trial,
        "is_eligible_for_welcome_credit": is_eligible_for_welcome_credit,
        "has_used_trial": tenant.has_used_trial,
        "has_received_welcome_credit": tenant.has_received_welcome_credit
    }

@app.post("/api/billing/activate-trial")
async def activate_trial(request: TrialActivationRequest, current_tenant_id: str = Depends(get_current_tenant)):
    tm = get_agent().tenant_manager
    tenant = tm.get_tenant(current_tenant_id)
    
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
        
    if tenant.has_used_trial:
        raise HTTPException(status_code=400, detail="Trial already used")
        
    if tenant.subscription_status != SubscriptionStatus.INACTIVE:
        raise HTTPException(status_code=400, detail="Cannot activate trial on active subscription")
        
    # Activate Trial
    tenant.subscription_status = SubscriptionStatus.TRIAL
    tenant.trial_expires_at = datetime.now() + timedelta(days=30)
    tenant.has_used_trial = True
    
    tm.save_tenant(tenant)
    return {"status": "success", "subscription_status": "trial", "expires_at": tenant.trial_expires_at}

@app.post("/api/billing/activate-payg")
async def activate_payg(request: PaygActivationRequest, current_tenant_id: str = Depends(get_current_tenant)):
    tm = get_agent().tenant_manager
    tenant = tm.get_tenant(current_tenant_id)
    
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    # TODO: Verify Stripe SetupIntent with Stripe API
    # stripe.SetupIntent.retrieve(request.stripe_setup_intent_id)
    
    previous_status = tenant.subscription_status
    tenant.subscription_status = SubscriptionStatus.ACTIVE_PAYG
    tenant.trial_expires_at = None # Clear trial expiry if any
    
    welcome_bonus_applied = False
    
    # Welcome Credit Logic: Strictly if they haven't used trial AND haven't received it before
    if not tenant.has_used_trial and not tenant.has_received_welcome_credit:
        tenant.credits_balance += 200.0
        tenant.has_received_welcome_credit = True
        welcome_bonus_applied = True
        
        # Log Transaction
        tx = CreditTransaction(
            tenant_id=tenant.id,
            amount=200.0,
            transaction_type=CreditTransactionType.WELCOME_BONUS,
            description="Welcome Credit for skipping trial"
        )
        tm.log_credit_transaction(tx)

    # Note: If they ARE moving from Trial -> PAYG, they get 0 credit, as per requirements.
    # "If a tenant used the free trial, then it's not entitled to the welcome credit"
    
    tm.save_tenant(tenant)
    return {
        "status": "success", 
        "subscription_status": "active_payg", 
        "welcome_bonus_applied": welcome_bonus_applied,
        "new_balance": tenant.credits_balance
    }

@app.post("/api/admin/credits/{tenant_id}")
async def admin_add_credits(tenant_id: str, request: CreditAdjustmentRequest, user = Depends(get_current_user)):
    # Verify Admin Role (skipped for MVP)
    
    tm = get_agent().tenant_manager
    tenant = tm.get_tenant(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
        
    tenant.credits_balance += request.amount
    tm.save_tenant(tenant)
    
    # Log Transaction
    tx = CreditTransaction(
        tenant_id=tenant.id,
        amount=request.amount,
        transaction_type=CreditTransactionType.ADMIN_ADJUSTMENT,
        description=request.description
    )
    tm.log_credit_transaction(tx)
    
    return {"status": "success", "new_balance": tenant.credits_balance}


if __name__ == "__main__":
    start()
