from datetime import datetime
from typing import Optional, List
from ..tenancy.models import Tenant, ServiceStatus

class FeatureGate:
    """
    Centralized logic for checking if a tenant has access to a specific feature.
    """
    
    @staticmethod
    def check_access(tenant: Tenant, service_name: str) -> bool:
        """
        Check if a tenant has active access to a service.
        Access is granted if:
        1. Service status is ACTIVE.
        2. Service status is CANCELED, but active_until is in the future.
        3. Tenant is in TRIAL mode (Access to ALL features).
        """
        
        # 1. Trial Override
        if tenant.subscription_status == "trial":
            # Check if trial expired?
            if tenant.trial_expires_at and tenant.trial_expires_at > datetime.now():
                return True
            # Expired trial => No access
            return False
            
        # 2. Service Check
        if service_name not in tenant.services:
            return False
            
        service = tenant.services[service_name]
        
        if service.status == ServiceStatus.ACTIVE:
            return True
            
        if service.status == ServiceStatus.CANCELED:
            if service.active_until and service.active_until > datetime.now():
                return True
                
        return False

    @staticmethod
    def require_access(tenant: Tenant, service_name: str):
        """
        Raises generic permission exception if check fails.
        Useful for upper layers to catch.
        """
        if not FeatureGate.check_access(tenant, service_name):
            raise PermissionError(f"Access denied. Service '{service_name}' is not active.")
