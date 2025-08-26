"""
Enterprise Integration Routes (STEP 9)
API endpoints for API Gateway, webhooks, external integrations, and enterprise features
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
from pydantic import BaseModel

from services.api_gateway_service import get_api_gateway_service

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()

# Pydantic models for request/response
class CreateAPIKeyRequest(BaseModel):
    client_name: str
    tier: str = "basic"  # basic, premium, enterprise

class CreateWebhookRequest(BaseModel):
    client_id: str
    url: str
    events: List[str]
    secret: Optional[str] = None

class CreateIntegrationRequest(BaseModel):
    provider: str
    api_key: str
    endpoint_url: str
    rate_limit: int = 100

class ExternalAPICallRequest(BaseModel):
    integration_id: str
    endpoint: str
    params: Optional[Dict[str, Any]] = None

@router.get("/enterprise/status")
async def get_enterprise_status() -> Dict[str, Any]:
    """Get enterprise API Gateway status"""
    try:
        gateway_service = get_api_gateway_service()
        
        if not gateway_service:
            return {
                "service_running": False,
                "message": "API Gateway service not started",
                "api_keys": {"total": 0, "active": 0},
                "webhooks": {"total": 0, "active": 0},
                "external_integrations": {"total": 0, "active": 0}
            }
        
        return gateway_service.get_gateway_status()
        
    except Exception as e:
        logger.error(f"Error getting enterprise status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get enterprise status")

@router.post("/enterprise/start")
async def start_enterprise_services() -> Dict[str, Any]:
    """Start enterprise API Gateway services"""
    try:
        from services.api_gateway_service import start_api_gateway
        
        await start_api_gateway()
        
        return {
            "message": "Enterprise API Gateway services started successfully",
            "features": [
                "API Key Management & Authentication",
                "Multi-tier Rate Limiting (Basic/Premium/Enterprise)",
                "Advanced Webhook System with Retries",
                "External API Integration Management",
                "JWT Token Authentication",
                "Real-time Monitoring & Health Checks",
                "Multi-tenant Architecture Support"
            ],
            "rate_limits": {
                "basic": "100 req/min (burst: 150)",
                "premium": "500 req/min (burst: 750)",
                "enterprise": "2000 req/min (burst: 3000)"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error starting enterprise services: {e}")
        raise HTTPException(status_code=500, detail="Failed to start enterprise services")

@router.post("/enterprise/stop")
async def stop_enterprise_services() -> Dict[str, Any]:
    """Stop enterprise API Gateway services"""
    try:
        from services.api_gateway_service import stop_api_gateway
        
        await stop_api_gateway()
        
        return {
            "message": "Enterprise API Gateway services stopped successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error stopping enterprise services: {e}")
        raise HTTPException(status_code=500, detail="Failed to stop enterprise services")

# API Key Management
@router.post("/enterprise/api-keys")
async def create_api_key(request: CreateAPIKeyRequest) -> Dict[str, Any]:
    """Create a new API key for a client"""
    try:
        gateway_service = get_api_gateway_service()
        
        if not gateway_service:
            raise HTTPException(status_code=503, detail="API Gateway service not running")
        
        # Validate tier
        valid_tiers = ["basic", "premium", "enterprise"]
        if request.tier not in valid_tiers:
            raise HTTPException(status_code=400, detail=f"Invalid tier. Must be one of: {valid_tiers}")
        
        # Create API key
        api_key_obj = await gateway_service.create_api_key(request.client_name, request.tier)
        
        return {
            "api_key": {
                "key_id": api_key_obj.key_id,
                "api_key": api_key_obj.api_key,
                "client_name": api_key_obj.client_name,
                "tier": api_key_obj.tier,
                "rate_limit_per_minute": api_key_obj.rate_limit_per_minute,
                "allowed_endpoints": api_key_obj.allowed_endpoints,
                "created_at": api_key_obj.created_at.isoformat()
            },
            "usage_instructions": {
                "header": "Authorization: Bearer <api_key>",
                "rate_limits": f"{api_key_obj.rate_limit_per_minute} requests per minute",
                "allowed_endpoints": len(api_key_obj.allowed_endpoints) if api_key_obj.allowed_endpoints != ["*"] else "All endpoints"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating API key: {e}")
        raise HTTPException(status_code=500, detail="Failed to create API key")

@router.get("/enterprise/api-keys")
async def list_api_keys() -> Dict[str, Any]:
    """List all API keys (without revealing the actual keys)"""
    try:
        gateway_service = get_api_gateway_service()
        
        if not gateway_service:
            raise HTTPException(status_code=503, detail="API Gateway service not running")
        
        api_keys_info = []
        for api_key_obj in gateway_service.api_keys.values():
            api_keys_info.append({
                "key_id": api_key_obj.key_id,
                "client_name": api_key_obj.client_name,
                "tier": api_key_obj.tier,
                "rate_limit_per_minute": api_key_obj.rate_limit_per_minute,
                "is_active": api_key_obj.is_active,
                "created_at": api_key_obj.created_at.isoformat(),
                "last_used": api_key_obj.last_used.isoformat() if api_key_obj.last_used else None,
                "endpoints_count": len(api_key_obj.allowed_endpoints) if api_key_obj.allowed_endpoints != ["*"] else "unlimited"
            })
        
        # Group by tier
        by_tier = {"basic": 0, "premium": 0, "enterprise": 0}
        for key_info in api_keys_info:
            by_tier[key_info["tier"]] += 1
        
        return {
            "api_keys": api_keys_info,
            "total_keys": len(api_keys_info),
            "active_keys": len([k for k in api_keys_info if k["is_active"]]),
            "distribution_by_tier": by_tier
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing API keys: {e}")
        raise HTTPException(status_code=500, detail="Failed to list API keys")

@router.delete("/enterprise/api-keys/{key_id}")
async def deactivate_api_key(key_id: str) -> Dict[str, Any]:
    """Deactivate an API key"""
    try:
        gateway_service = get_api_gateway_service()
        
        if not gateway_service:
            raise HTTPException(status_code=503, detail="API Gateway service not running")
        
        # Find and deactivate the API key
        api_key_obj = None
        for key_obj in gateway_service.api_keys.values():
            if key_obj.key_id == key_id:
                api_key_obj = key_obj
                break
        
        if not api_key_obj:
            raise HTTPException(status_code=404, detail="API key not found")
        
        api_key_obj.is_active = False
        await gateway_service._save_api_keys()
        
        return {
            "message": f"API key for {api_key_obj.client_name} deactivated successfully",
            "key_id": key_id,
            "client_name": api_key_obj.client_name,
            "deactivated_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deactivating API key: {e}")
        raise HTTPException(status_code=500, detail="Failed to deactivate API key")

# Webhook Management
@router.post("/enterprise/webhooks")
async def create_webhook(request: CreateWebhookRequest) -> Dict[str, Any]:
    """Register a new webhook for a client"""
    try:
        gateway_service = get_api_gateway_service()
        
        if not gateway_service:
            raise HTTPException(status_code=503, detail="API Gateway service not running")
        
        # Validate events
        valid_events = [
            "yield_update", "anomaly_alert", "index_update", "risk_alert",
            "performance_update", "compliance_report", "system_health"
        ]
        
        invalid_events = [event for event in request.events if event not in valid_events]
        if invalid_events:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid events: {invalid_events}. Valid events: {valid_events}"
            )
        
        # Register webhook
        webhook = await gateway_service.register_webhook(
            request.client_id, request.url, request.events, request.secret
        )
        
        return {
            "webhook": {
                "webhook_id": webhook.webhook_id,
                "client_id": webhook.client_id,
                "url": webhook.url,
                "events": webhook.events,
                "is_active": webhook.is_active,
                "created_at": webhook.created_at.isoformat()
            },
            "webhook_secret": webhook.secret,
            "verification_info": {
                "signature_header": "X-StableYield-Signature",
                "event_header": "X-StableYield-Event",
                "timestamp_header": "X-StableYield-Timestamp"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating webhook: {e}")
        raise HTTPException(status_code=500, detail="Failed to create webhook")

@router.get("/enterprise/webhooks")
async def list_webhooks() -> Dict[str, Any]:
    """List all registered webhooks"""
    try:
        gateway_service = get_api_gateway_service()
        
        if not gateway_service:
            raise HTTPException(status_code=503, detail="API Gateway service not running")
        
        webhooks_info = []
        for webhook in gateway_service.webhooks.values():
            webhooks_info.append({
                "webhook_id": webhook.webhook_id,
                "client_id": webhook.client_id,
                "url": webhook.url,
                "events": webhook.events,
                "is_active": webhook.is_active,
                "created_at": webhook.created_at.isoformat(),
                "last_triggered": webhook.last_triggered.isoformat() if webhook.last_triggered else None
            })
        
        # Group by client
        by_client = {}
        for webhook_info in webhooks_info:
            client_id = webhook_info["client_id"]
            if client_id not in by_client:
                by_client[client_id] = 0
            by_client[client_id] += 1
        
        return {
            "webhooks": webhooks_info,
            "total_webhooks": len(webhooks_info),
            "active_webhooks": len([w for w in webhooks_info if w["is_active"]]),
            "webhooks_by_client": by_client,
            "webhook_queue_size": gateway_service.webhook_queue.qsize()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing webhooks: {e}")
        raise HTTPException(status_code=500, detail="Failed to list webhooks")

@router.post("/enterprise/webhooks/test/{webhook_id}")
async def test_webhook(webhook_id: str) -> Dict[str, Any]:
    """Test a webhook by sending a test event"""
    try:
        gateway_service = get_api_gateway_service()
        
        if not gateway_service:
            raise HTTPException(status_code=503, detail="API Gateway service not running")
        
        # Check if webhook exists
        if webhook_id not in gateway_service.webhooks:
            raise HTTPException(status_code=404, detail="Webhook not found")
        
        webhook = gateway_service.webhooks[webhook_id]
        
        # Send test event
        test_data = {
            "test_event": True,
            "webhook_id": webhook_id,
            "timestamp": datetime.utcnow().isoformat(),
            "message": "This is a test webhook delivery from StableYield Enterprise API"
        }
        
        await gateway_service.trigger_webhook("test_event", test_data)
        
        return {
            "message": "Test webhook queued for delivery",
            "webhook_id": webhook_id,
            "url": webhook.url,
            "test_data": test_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing webhook: {e}")
        raise HTTPException(status_code=500, detail="Failed to test webhook")

# External Integrations
@router.post("/enterprise/integrations")
async def create_external_integration(request: CreateIntegrationRequest) -> Dict[str, Any]:
    """Add a new external API integration"""
    try:
        gateway_service = get_api_gateway_service()
        
        if not gateway_service:
            raise HTTPException(status_code=503, detail="API Gateway service not running")
        
        # Validate provider
        supported_providers = ["bloomberg", "refinitiv", "coinapi", "cryptocompare", "custom"]
        if request.provider not in supported_providers:
            raise HTTPException(
                status_code=400, 
                detail=f"Provider must be one of: {supported_providers}"
            )
        
        # Create integration
        integration = await gateway_service.add_external_integration(
            request.provider, request.api_key, request.endpoint_url, request.rate_limit
        )
        
        return {
            "integration": {
                "integration_id": integration.integration_id,
                "provider": integration.provider,
                "endpoint_url": integration.endpoint_url,
                "rate_limit": integration.rate_limit,
                "is_active": integration.is_active
            },
            "usage_info": {
                "authentication": "Bearer token authentication",
                "rate_limit": f"{integration.rate_limit} requests per minute",
                "user_agent": "StableYield-Enterprise/1.0"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating external integration: {e}")
        raise HTTPException(status_code=500, detail="Failed to create external integration")

@router.get("/enterprise/integrations")
async def list_external_integrations() -> Dict[str, Any]:
    """List all external API integrations"""
    try:
        gateway_service = get_api_gateway_service()
        
        if not gateway_service:
            raise HTTPException(status_code=503, detail="API Gateway service not running")
        
        integrations_info = []
        for integration in gateway_service.external_integrations.values():
            integrations_info.append({
                "integration_id": integration.integration_id,
                "provider": integration.provider,
                "endpoint_url": integration.endpoint_url,
                "rate_limit": integration.rate_limit,
                "is_active": integration.is_active,
                "last_sync": integration.last_sync.isoformat() if integration.last_sync else None
            })
        
        # Group by provider
        by_provider = {}
        for integration_info in integrations_info:
            provider = integration_info["provider"]
            if provider not in by_provider:
                by_provider[provider] = 0
            by_provider[provider] += 1
        
        return {
            "integrations": integrations_info,
            "total_integrations": len(integrations_info),
            "active_integrations": len([i for i in integrations_info if i["is_active"]]),
            "integrations_by_provider": by_provider
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing external integrations: {e}")
        raise HTTPException(status_code=500, detail="Failed to list external integrations")

@router.post("/enterprise/integrations/call")
async def call_external_api(request: ExternalAPICallRequest) -> Dict[str, Any]:
    """Make an authenticated call to an external API"""
    try:
        gateway_service = get_api_gateway_service()
        
        if not gateway_service:
            raise HTTPException(status_code=503, detail="API Gateway service not running")
        
        # Make external API call
        result = await gateway_service.call_external_api(
            request.integration_id, request.endpoint, request.params
        )
        
        return {
            "result": result,
            "integration_id": request.integration_id,
            "endpoint": request.endpoint,
            "call_timestamp": datetime.utcnow().isoformat()
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calling external API: {e}")
        raise HTTPException(status_code=500, detail="Failed to call external API")

# JWT Token Management
@router.post("/enterprise/auth/token")
async def create_jwt_token(
    client_id: str = Query(description="Client ID"),
    permissions: List[str] = Query(default=["read"], description="List of permissions")
) -> Dict[str, Any]:
    """Create a JWT token for a client"""
    try:
        gateway_service = get_api_gateway_service()
        
        if not gateway_service:
            raise HTTPException(status_code=503, detail="API Gateway service not running")
        
        # Create JWT token
        token = gateway_service.create_jwt_token(client_id, permissions)
        
        return {
            "access_token": token,
            "token_type": "Bearer",
            "expires_in": gateway_service.jwt_expiry_hours * 3600,  # seconds
            "permissions": permissions,
            "client_id": client_id,
            "issued_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating JWT token: {e}")
        raise HTTPException(status_code=500, detail="Failed to create JWT token")

@router.post("/enterprise/auth/verify")
async def verify_jwt_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Verify a JWT token"""
    try:
        gateway_service = get_api_gateway_service()
        
        if not gateway_service:
            raise HTTPException(status_code=503, detail="API Gateway service not running")
        
        # Verify token
        payload = gateway_service.verify_jwt_token(credentials.credentials)
        
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        return {
            "valid": True,
            "client_id": payload.get("client_id"),
            "permissions": payload.get("permissions", []),
            "issued_at": payload.get("iat"),
            "expires_at": payload.get("exp"),
            "verified_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying JWT token: {e}")
        raise HTTPException(status_code=500, detail="Failed to verify JWT token")

# Monitoring & Analytics
@router.get("/enterprise/metrics")
async def get_enterprise_metrics() -> Dict[str, Any]:
    """Get enterprise API Gateway metrics"""
    try:
        gateway_service = get_api_gateway_service()
        
        if not gateway_service:
            raise HTTPException(status_code=503, detail="API Gateway service not running")
        
        # Get current metrics
        metrics = gateway_service.api_metrics.copy()
        
        # Calculate additional metrics
        total_requests = metrics["total_requests"]
        successful_requests = metrics["successful_requests"]
        failed_requests = metrics["failed_requests"]
        rate_limited_requests = metrics["rate_limited_requests"]
        
        success_rate = (successful_requests / max(1, total_requests)) * 100
        failure_rate = (failed_requests / max(1, total_requests)) * 100
        rate_limit_rate = (rate_limited_requests / max(1, total_requests)) * 100
        
        return {
            "raw_metrics": metrics,
            "calculated_metrics": {
                "success_rate_percentage": success_rate,
                "failure_rate_percentage": failure_rate,
                "rate_limit_rate_percentage": rate_limit_rate,
                "total_requests": total_requests
            },
            "service_health": {
                "webhook_queue_size": gateway_service.webhook_queue.qsize(),
                "active_rate_limit_buckets": len(gateway_service.rate_limit_buckets),
                "active_api_keys": len([k for k in gateway_service.api_keys.values() if k.is_active]),
                "active_webhooks": len([w for w in gateway_service.webhooks.values() if w.is_active]),
                "active_integrations": len([i for i in gateway_service.external_integrations.values() if i.is_active])
            },
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting enterprise metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get enterprise metrics")

@router.get("/enterprise/health")
async def get_enterprise_health() -> Dict[str, Any]:
    """Get detailed enterprise service health check"""
    try:
        gateway_service = get_api_gateway_service()
        
        if not gateway_service:
            return {
                "status": "unhealthy",
                "message": "API Gateway service not running",
                "components": {}
            }
        
        # Check health of different components
        components = {
            "api_gateway": {
                "status": "healthy" if gateway_service.is_running else "unhealthy",
                "uptime": "running" if gateway_service.is_running else "stopped"
            },
            "webhook_system": {
                "status": "healthy",
                "queue_size": gateway_service.webhook_queue.qsize(),
                "registered_webhooks": len(gateway_service.webhooks)
            },
            "rate_limiting": {
                "status": "healthy",
                "active_buckets": len(gateway_service.rate_limit_buckets),
                "configuration": "multi-tier"
            },
            "external_integrations": {
                "status": "healthy",
                "total_integrations": len(gateway_service.external_integrations),
                "active_integrations": len([i for i in gateway_service.external_integrations.values() if i.is_active])
            },
            "authentication": {
                "status": "healthy",
                "api_keys_total": len(gateway_service.api_keys),
                "jwt_enabled": True
            }
        }
        
        # Overall status
        unhealthy_components = [name for name, comp in components.items() if comp.get("status") != "healthy"]
        overall_status = "unhealthy" if unhealthy_components else "healthy"
        
        return {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "components": components,
            "unhealthy_components": unhealthy_components,
            "service_version": "1.0.0",
            "environment": "production"
        }
        
    except Exception as e:
        logger.error(f"Error getting enterprise health: {e}")
        return {
            "status": "unhealthy", 
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@router.get("/enterprise/summary")
async def get_enterprise_summary() -> Dict[str, Any]:
    """Get comprehensive enterprise service summary"""
    try:
        gateway_service = get_api_gateway_service()
        
        if not gateway_service:
            return {
                "message": "Enterprise API Gateway service not running",
                "service_status": "stopped",
                "capabilities": []
            }
        
        # Get comprehensive status
        status = gateway_service.get_gateway_status()
        
        return {
            "service_status": "running" if status["service_running"] else "stopped",
            "enterprise_features": {
                "api_key_management": {
                    "total_keys": status["api_keys"]["total"],
                    "active_keys": status["api_keys"]["active"],
                    "tiers_supported": ["basic", "premium", "enterprise"]
                },
                "webhook_system": {
                    "total_webhooks": status["webhooks"]["total"],
                    "active_webhooks": status["webhooks"]["active"],
                    "queue_size": status["webhooks"]["queue_size"],
                    "events_supported": ["yield_update", "anomaly_alert", "index_update", "risk_alert"]
                },
                "external_integrations": {
                    "total_integrations": status["external_integrations"]["total"],
                    "active_integrations": status["external_integrations"]["active"],
                    "providers_supported": ["bloomberg", "refinitiv", "coinapi", "cryptocompare", "custom"]
                },
                "rate_limiting": {
                    "active_buckets": status["rate_limiting"]["active_buckets"],
                    "tiers": status["rate_limiting"]["configuration"]
                }
            },
            "performance_metrics": status["metrics"],
            "api_endpoints": [
                "POST /api/enterprise/api-keys (Create API keys)",
                "POST /api/enterprise/webhooks (Register webhooks)",
                "POST /api/enterprise/integrations (Add external integrations)",
                "POST /api/enterprise/auth/token (JWT token creation)",
                "GET /api/enterprise/metrics (Performance metrics)",
                "GET /api/enterprise/health (Service health check)"
            ],
            "security_features": [
                "Multi-tier API key authentication",
                "JWT token-based authentication",
                "Rate limiting with burst protection",
                "Webhook signature verification",
                "External API authentication management"
            ],
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting enterprise summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to get enterprise summary")