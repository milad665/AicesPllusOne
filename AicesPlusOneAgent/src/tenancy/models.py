from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from enum import Enum
from datetime import datetime
import uuid

class SubscriptionStatus(str, Enum):
    INACTIVE = "inactive"
    TRIAL = "trial"
    ACTIVE_PAYG = "active_payg"

class SubscriptionTier(str, Enum):
    # Deprecated but kept for backward compatibility if needed, 
    # though we are moving to Status-based.
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class AnalyzerConfig(BaseModel):
    """Configuration for connecting to the tenant's Code Analyzer."""
    url: str = Field(default="http://localhost:8000", description="Base URL of the code analyzer")
    use_mtls: bool = Field(default=False, description="Whether to use mTLS for connection")
    client_cert_path: Optional[str] = Field(default=None, description="Path to client certificate (.crt)")
    client_key_path: Optional[str] = Field(default=None, description="Path to client private key (.key)")
    ca_cert_path: Optional[str] = Field(default=None, description="Path to CA certificate (.crt)")
    whitelisted_ips: List[str] = Field(default_factory=list, description="List of IPs tenant needs to whitelist")

class ServiceStatus(str, Enum):
    ACTIVE = "active"
    CANCELED = "canceled"
    INACTIVE = "inactive"

class TenantService(BaseModel):
    name: str 
    status: ServiceStatus = ServiceStatus.INACTIVE
    active_until: Optional[datetime] = None
    last_billed: Optional[datetime] = None

class Tenant(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    subscription_tier: SubscriptionTier = SubscriptionTier.FREE
    
    # Billing / Subscription Fields
    credits_balance: float = Field(default=0.0, description="Current credit balance in EUR")
    has_used_trial: bool = Field(default=False, description="If tenant has already used the Free Trial")
    has_received_welcome_credit: bool = Field(default=False, description="If tenant received the one-time welcome credit")
    subscription_status: SubscriptionStatus = Field(default=SubscriptionStatus.INACTIVE, description="Current subscription state")
    trial_expires_at: Optional[datetime] = Field(default=None, description="Expiration date of free trial")
    stripe_customer_id: Optional[str] = Field(default=None, description="Stripe Customer ID")
    active_subscription_id: Optional[str] = Field(default=None, description="Active Stripe Subscription ID")

    # Service-Based Billing
    seat_count: int = Field(default=1, description="Number of billable users")
    services: Dict[str, TenantService] = Field(default_factory=dict, description="Active Services")

    created_at: datetime = Field(default_factory=datetime.now)
    config: Dict[str, Any] = Field(default_factory=dict)
    
    # New Field: Analyzer Configuration
    analyzer_config: AnalyzerConfig = Field(default_factory=AnalyzerConfig)

    # Service Tokens: {token: "description"}
    service_tokens: Dict[str, str] = Field(default_factory=dict)
    
class CreateTenantRequest(BaseModel):
    name: str
    subscription_tier: SubscriptionTier = SubscriptionTier.FREE

class UpdateTenantConfigRequest(BaseModel):
    url: Optional[str] = None
    use_mtls: Optional[bool] = None
    whitelisted_ips: Optional[List[str]] = None


class CreditTransactionType(str, Enum):
    WELCOME_BONUS = "welcome_bonus"
    ADMIN_ADJUSTMENT = "admin_adjustment"
    USAGE_CHARGE = "usage_charge"
    PAYMENT_TOPUP = "payment_topup"

class CreditTransaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    amount: float
    transaction_type: CreditTransactionType
    description: str
    timestamp: datetime = Field(default_factory=datetime.now)
    reference_id: Optional[str] = None  # e.g., Stripe Charge ID or Admin User ID
