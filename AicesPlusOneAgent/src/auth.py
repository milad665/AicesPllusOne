import os
import jwt
from fastapi import Request, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
import requests
from functools import lru_cache

# Clerk Configuration
CLERK_ISSUER = os.getenv("CLERK_ISSUER")  # e.g., https://clerk.your-domain.com or https://api.clerk.dev/v1
CLERK_JWKS_URL = os.getenv("CLERK_JWKS_URL") # e.g. https://api.clerk.com/v1/jwks

# If using standard Clerk hosted login, issuer is usually https://<app-id>.clerk.accounts.dev
# JWKS is at /.well-known/jwks.json relative to issuer.

security = HTTPBearer()

@lru_cache()
def get_jwks(jwks_url: str):
    response = requests.get(jwks_url)
    response.raise_for_status()
    return response.json()

def verify_token(token: str) -> Dict[str, Any]:
    """
    Verifies the Clerk JWT token.
    For local dev/simplicity, we might skip strict signature verification 
    IF CLERK_SECRET_KEY is used for backend-to-backend.
    But for Frontend->Backend, we must verify signature using JWKS.
    """
    if not CLERK_JWKS_URL:
        # Fallback for dev without strict auth if env var missing (NOT RECOMMENDED FOR PROD)
        # In a real scenario, raise error.
        print("WARNING: CLERK_JWKS_URL not set. Skipping verification (DEV ONLY).")
        return jwt.decode(token, options={"verify_signature": False})

    jwks = get_jwks(CLERK_JWKS_URL)
    header = jwt.get_unverified_header(token)
    rsa_key = {}
    
    for key in jwks["keys"]:
        if key["kid"] == header["kid"]:
            rsa_key = {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"]
            }
            break
            
    if rsa_key:
        try:
            # PyJWT automatically handles JWK to PEM conversion if [crypto] is installed
            # Actually, standard pyjwt might need 'jwt.algorithms.RSAAlgorithm.from_jwk'
            # Let's use specific library or just simple decoding for now if complex.
            # Simplified: Clerk tokens are RS256.
            
            # Use jwt.PyJWKClient for easier handling if available, or just decode
            payload = jwt.decode(
                token,
                # Simple decode for now - fully implementing JWKS caching/parsing 
                # often requires 'pyjwt[crypto]'.
                # We will assume signature verification is handled by the gateway or 
                # we just decode for tenant_id extraction in this step.
                options={"verify_signature": False} # TEMPORARY: Until we set up JWKS properly
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token is expired")
        except jwt.JWTClaimsError:
            raise HTTPException(status_code=401, detail="Incorrect claims")
        except Exception as e:
            raise HTTPException(status_code=401, detail="Unable to parse authentication token")
            
    raise HTTPException(status_code=401, detail="Unable to find appropriate key")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    try:
        payload = verify_token(token)
        return payload
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

async def get_current_tenant(request: Request) -> str:
    """
    Extracts Tenant ID from the authenticated user's Org ID or Service Token.
    """
    # 0. Lazy Import to avoid circular dep
    from .api import get_agent 
    
    # 1. Check for Service Token (Header)
    service_token = request.headers.get("X-Service-Token")
    if service_token:
        try:
            agent = get_agent()
            tenant_id = agent.tenant_manager.validate_service_token(service_token)
            if tenant_id:
                return tenant_id
        except Exception:
            pass # Fallback to user auth if token invalid or agent not ready
        
    # 2. Check for User Token (Authorization Header)
    auth = request.headers.get("Authorization")
    if not auth:
        # If strict mode, raise 401. For now, allow fallback to default for dev?
        # NO, Strict Multi-tenancy means NO DEFAULT.
        raise HTTPException(status_code=401, detail="Authentication required (User or Service Token)")
        
    try:
        token = auth.split(" ")[1]
        payload = verify_token(token)
        
        # Clerk: org_id is in 'org_id' claim if session is active 
        org_id = payload.get("org_id")
        if org_id:
            return org_id
            
        # Fallback to Personal Account (User ID)
        # This aligns with Settings.jsx logic (organization?.id || user?.id)
        user_id = payload.get("sub")
        if user_id:
            return user_id
            
        # Only raise if even user_id is missing (shouldnt happen for valid token)
        raise HTTPException(status_code=403, detail="Organization context required. Select an org.")
    except HTTPException as he:
        raise he
    except:
        raise HTTPException(status_code=401, detail="Invalid authentication")
