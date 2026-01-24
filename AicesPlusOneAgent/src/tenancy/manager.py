import json
import os
from typing import List, Optional, Dict
import uuid
from .models import Tenant, SubscriptionTier, AnalyzerConfig, UpdateTenantConfigRequest

class TenantManager:
    """
    Manages tenant creation, retrieval, and persistence.
    """
    
    def __init__(self, storage_file: str = "data/tenants.json"):
        self.storage_file = storage_file
        # Ensure data dir exists
        os.makedirs(os.path.dirname(self.storage_file), exist_ok=True)
        self._load()

    def _load(self):
        """Load tenants from disk."""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    data = json.load(f)
                    self.tenants = {t['id']: Tenant(**t) for t in data}
            except Exception as e:
                print(f"Error loading tenants: {e}")
                self.tenants = {}
        else:
            self.tenants = {}

    def _save(self):
        """Save tenants to disk."""
        data = [t.model_dump(mode='json') for t in self.tenants.values()]
        with open(self.storage_file, 'w') as f:
            json.dump(data, f, indent=2)

    def create_tenant(self, name: str, tier: SubscriptionTier = SubscriptionTier.FREE) -> Tenant:
        """Create a new tenant."""
        tenant = Tenant(name=name, subscription_tier=tier)
        self.tenants[tenant.id] = tenant
        self._save()
        return tenant

    def get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        """Get a tenant by ID."""
        return self.tenants.get(tenant_id)
    
    def list_tenants(self) -> List[Tenant]:
        """List all tenants."""
        return list(self.tenants.values())

    def delete_tenant(self, tenant_id: str) -> bool:
        """Delete a tenant."""
        if tenant_id in self.tenants:
            del self.tenants[tenant_id]
            self._save()
            return True
        return False

    def update_tenant_config(self, tenant_id: str, updates: UpdateTenantConfigRequest) -> Optional[Tenant]:
        """Update tenant configuration."""
        tenant = self.get_tenant(tenant_id)
        if not tenant:
            return None
            
        config = tenant.analyzer_config
        
        if updates.url is not None:
            config.url = updates.url
        if updates.use_mtls is not None:
            config.use_mtls = updates.use_mtls
        if updates.whitelisted_ips is not None:
            config.whitelisted_ips = updates.whitelisted_ips
            
        self._save()
        return tenant
        
    def update_certificates(self, tenant_id: str, client_cert: str = None, client_key: str = None, ca_cert: str = None) -> Optional[Tenant]:
        """Update certificate paths for tenant."""
        tenant = self.get_tenant(tenant_id)
        if not tenant:
            return None
            
        if client_cert:
            tenant.analyzer_config.client_cert_path = client_cert
        if client_key:
            tenant.analyzer_config.client_key_path = client_key
        if ca_cert:
            tenant.analyzer_config.ca_cert_path = ca_cert
            
        self._save()
        return tenant

    def create_service_token(self, tenant_id: str, description: str = "MCP Token") -> Optional[str]:
        """Generate a new service token for the tenant."""
        tenant = self.get_tenant(tenant_id)
        if not tenant:
            return None
        
        # Simple UUID token for now. In prod, use crypto secure random or JWT.
        token = f"st_{uuid.uuid4().hex}"
        tenant.service_tokens[token] = description
        self._save()
        return token

    def revoke_service_token(self, tenant_id: str, token: str) -> bool:
        """Revoke a service token."""
        tenant = self.get_tenant(tenant_id)
        if not tenant:
            return False
            
        if token in tenant.service_tokens:
            del tenant.service_tokens[token]
            self._save()
            return True
        return False
        
    def validate_service_token(self, token: str) -> Optional[str]:
        """Validate a token and return the tenant_id if valid."""
        # Simple linear scan. For high scale, use a reverse index or database.
        for tenant in self.tenants.values():
            if token in tenant.service_tokens:
                return tenant.id
        return None
