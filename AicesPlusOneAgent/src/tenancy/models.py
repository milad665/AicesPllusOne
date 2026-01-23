from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from enum import Enum
from datetime import datetime
import uuid

class SubscriptionTier(str, Enum):
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

class Tenant(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    subscription_tier: SubscriptionTier = SubscriptionTier.FREE
    created_at: datetime = Field(default_factory=datetime.now)
    config: Dict[str, Any] = Field(default_factory=dict)
    
    # New Field: Analyzer Configuration
    analyzer_config: AnalyzerConfig = Field(default_factory=AnalyzerConfig)
    
class CreateTenantRequest(BaseModel):
    name: str
    subscription_tier: SubscriptionTier = SubscriptionTier.FREE

class UpdateTenantConfigRequest(BaseModel):
    url: Optional[str] = None
    use_mtls: Optional[bool] = None
    whitelisted_ips: Optional[List[str]] = None
