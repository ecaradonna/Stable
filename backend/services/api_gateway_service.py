"""
API Gateway & Enterprise Integration Service (STEP 9)
Advanced API management, rate limiting, authentication, and enterprise integrations
"""

import asyncio
import logging
import jwt
import hashlib
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import json
from pathlib import Path
from fastapi import HTTPException, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import aiohttp
import uuid

logger = logging.getLogger(__name__)

@dataclass
class APIKey:
    key_id: str
    api_key: str
    client_name: str
    tier: str  # "basic", "premium", "enterprise"
    rate_limit_per_minute: int
    allowed_endpoints: List[str]
    created_at: datetime
    last_used: Optional[datetime] = None
    is_active: bool = True

@dataclass
class RateLimitBucket:
    client_id: str
    endpoint: str
    requests_count: int
    window_start: datetime
    tier: str

@dataclass
class WebhookConfig:
    webhook_id: str
    client_id: str
    url: str
    events: List[str]  # ["yield_update", "anomaly_alert", "index_update"]
    secret: str
    is_active: bool
    created_at: datetime
    last_triggered: Optional[datetime] = None

@dataclass
class ExternalIntegration:
    integration_id: str
    provider: str  # "bloomberg", "refinitiv", "coinapi", "custom"
    api_key: str
    endpoint_url: str
    rate_limit: int
    is_active: bool
    last_sync: Optional[datetime] = None

class APIGatewayService:
    """Enterprise API Gateway with rate limiting, authentication, and integrations"""
    
    def __init__(self):
        # API Key management
        self.api_keys: Dict[str, APIKey] = {}
        
        # Rate limiting
        self.rate_limit_buckets: Dict[str, RateLimitBucket] = {}
        self.request_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # Webhook management
        self.webhooks: Dict[str, WebhookConfig] = {}
        self.webhook_queue = asyncio.Queue()
        
        # External integrations
        self.external_integrations: Dict[str, ExternalIntegration] = {}
        
        # JWT configuration
        self.jwt_secret = "stableyield_enterprise_secret_2025"
        self.jwt_algorithm = "HS256"
        self.jwt_expiry_hours = 24
        
        # Configuration
        self.config = {
            "rate_limiting": {
                "basic": {"requests_per_minute": 100, "burst_limit": 150},
                "premium": {"requests_per_minute": 500, "burst_limit": 750},
                "enterprise": {"requests_per_minute": 2000, "burst_limit": 3000}
            },
            "webhook": {
                "retry_attempts": 3,
                "timeout_seconds": 30,
                "retry_delay_seconds": 5
            },
            "monitoring": {
                "health_check_interval": 30,
                "metrics_retention_hours": 48
            }
        }
        
        # Monitoring
        self.api_metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "rate_limited_requests": 0,
            "webhook_deliveries": 0,
            "external_api_calls": 0
        }
        
        # Data storage
        self.data_dir = Path("/app/data/enterprise")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.is_running = False
        self.background_tasks = []
    
    async def start(self):
        """Start the API Gateway service"""
        if self.is_running:
            return
        
        self.is_running = True
        logger.info("🚀 Starting API Gateway Service...")
        
        # Load existing data
        await self._load_api_keys()
        await self._load_webhooks()
        await self._load_external_integrations()
        
        # Start background tasks
        self.background_tasks = [
            asyncio.create_task(self._webhook_processor()),
            asyncio.create_task(self._health_monitor()),
            asyncio.create_task(self._metrics_collector()),
            asyncio.create_task(self._rate_limit_cleaner())
        ]
        
        logger.info("✅ API Gateway Service started")
    
    async def stop(self):
        """Stop the API Gateway service"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()
        
        await asyncio.gather(*self.background_tasks, return_exceptions=True)
        
        # Save data
        await self._save_api_keys()
        await self._save_webhooks()
        await self._save_external_integrations()
        
        logger.info("🛑 API Gateway Service stopped")
    
    # Authentication & Authorization
    async def create_api_key(self, client_name: str, tier: str = "basic") -> APIKey:
        """Create a new API key for a client"""
        key_id = str(uuid.uuid4())
        api_key = self._generate_api_key()
        
        # Determine rate limits based on tier
        rate_limits = self.config["rate_limiting"][tier]
        
        # Default allowed endpoints based on tier
        if tier == "basic":
            allowed_endpoints = ["/api/yields", "/api/index/live", "/api/health"]
        elif tier == "premium":
            allowed_endpoints = [
                "/api/yields", "/api/index/live", "/api/health",
                "/api/ray/methodology", "/api/syi/composition",
                "/api/analytics/summary"
            ]
        else:  # enterprise
            allowed_endpoints = ["*"]  # All endpoints
        
        api_key_obj = APIKey(
            key_id=key_id,
            api_key=api_key,
            client_name=client_name,
            tier=tier,
            rate_limit_per_minute=rate_limits["requests_per_minute"],
            allowed_endpoints=allowed_endpoints,
            created_at=datetime.utcnow(),
            is_active=True
        )
        
        self.api_keys[api_key] = api_key_obj
        await self._save_api_keys()
        
        logger.info(f"🔑 Created API key for {client_name} (tier: {tier})")
        return api_key_obj
    
    def _generate_api_key(self) -> str:
        """Generate a secure API key"""
        timestamp = str(int(time.time()))
        random_data = str(uuid.uuid4())
        combined = f"stableyield_{timestamp}_{random_data}"
        
        hash_obj = hashlib.sha256(combined.encode())
        return f"sy_{hash_obj.hexdigest()[:32]}"
    
    async def validate_api_key(self, api_key: str) -> Optional[APIKey]:
        """Validate an API key"""
        if api_key not in self.api_keys:
            return None
        
        key_obj = self.api_keys[api_key]
        if not key_obj.is_active:
            return None
        
        # Update last used timestamp
        key_obj.last_used = datetime.utcnow()
        
        return key_obj
    
    async def check_endpoint_permission(self, api_key_obj: APIKey, endpoint: str) -> bool:
        """Check if API key has permission for endpoint"""
        if "*" in api_key_obj.allowed_endpoints:
            return True
        
        # Check exact match first
        if endpoint in api_key_obj.allowed_endpoints:
            return True
        
        # Check prefix matches
        for allowed in api_key_obj.allowed_endpoints:
            if endpoint.startswith(allowed):
                return True
        
        return False
    
    # Rate Limiting
    async def check_rate_limit(self, client_id: str, endpoint: str, tier: str) -> Tuple[bool, Dict[str, Any]]:
        """Check if request is within rate limits"""
        bucket_key = f"{client_id}_{endpoint}"
        current_time = datetime.utcnow()
        
        # Get or create rate limit bucket
        if bucket_key not in self.rate_limit_buckets:
            self.rate_limit_buckets[bucket_key] = RateLimitBucket(
                client_id=client_id,
                endpoint=endpoint,
                requests_count=0,
                window_start=current_time,
                tier=tier
            )
        
        bucket = self.rate_limit_buckets[bucket_key]
        
        # Check if we need to reset the window (1 minute windows)
        if (current_time - bucket.window_start).total_seconds() >= 60:
            bucket.requests_count = 0
            bucket.window_start = current_time
        
        # Get rate limit for tier
        rate_config = self.config["rate_limiting"][tier]
        rate_limit = rate_config["requests_per_minute"]
        burst_limit = rate_config["burst_limit"]
        
        # Check limits
        if bucket.requests_count >= burst_limit:
            # Hard limit exceeded
            return False, {
                "allowed": False,
                "rate_limit": rate_limit,
                "requests_remaining": 0,
                "reset_time": (bucket.window_start + timedelta(minutes=1)).isoformat(),
                "retry_after": 60 - (current_time - bucket.window_start).total_seconds()
            }
        
        # Increment counter
        bucket.requests_count += 1
        
        # Update metrics
        self.api_metrics["total_requests"] += 1
        
        return True, {
            "allowed": True,
            "rate_limit": rate_limit,
            "requests_remaining": max(0, rate_limit - bucket.requests_count),
            "reset_time": (bucket.window_start + timedelta(minutes=1)).isoformat(),
            "burst_remaining": max(0, burst_limit - bucket.requests_count)
        }
    
    # Webhook System
    async def register_webhook(self, client_id: str, url: str, events: List[str], secret: Optional[str] = None) -> WebhookConfig:
        """Register a webhook for a client"""
        webhook_id = str(uuid.uuid4())
        
        if not secret:
            secret = self._generate_webhook_secret()
        
        webhook = WebhookConfig(
            webhook_id=webhook_id,
            client_id=client_id,
            url=url,
            events=events,
            secret=secret,
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        self.webhooks[webhook_id] = webhook
        await self._save_webhooks()
        
        logger.info(f"🔗 Registered webhook for client {client_id}: {url}")
        return webhook
    
    def _generate_webhook_secret(self) -> str:
        """Generate a webhook secret"""
        return f"whsec_{uuid.uuid4().hex[:32]}"
    
    async def trigger_webhook(self, event: str, data: Dict[str, Any]):
        """Trigger webhooks for an event"""
        # Find webhooks that listen for this event
        relevant_webhooks = [
            webhook for webhook in self.webhooks.values()
            if webhook.is_active and event in webhook.events
        ]
        
        for webhook in relevant_webhooks:
            # Add to webhook queue for processing
            await self.webhook_queue.put({
                "webhook": webhook,
                "event": event,
                "data": data,
                "timestamp": datetime.utcnow().isoformat()
            })
    
    async def _webhook_processor(self):
        """Background task to process webhook deliveries"""
        while self.is_running:
            try:
                # Get webhook from queue (wait up to 1 second)
                try:
                    webhook_delivery = await asyncio.wait_for(self.webhook_queue.get(), timeout=1.0)
                except asyncio.TimeoutError:
                    continue
                
                await self._deliver_webhook(webhook_delivery)
                
            except Exception as e:
                logger.error(f"❌ Error in webhook processor: {e}")
    
    async def _deliver_webhook(self, delivery: Dict[str, Any]):
        """Deliver a webhook with retries"""
        webhook = delivery["webhook"]
        event = delivery["event"]
        data = delivery["data"]
        timestamp = delivery["timestamp"]
        
        # Create webhook payload
        payload = {
            "event": event,
            "timestamp": timestamp,
            "data": data
        }
        
        # Create signature
        signature = self._create_webhook_signature(json.dumps(payload), webhook.secret)
        
        headers = {
            "Content-Type": "application/json",
            "X-StableYield-Event": event,
            "X-StableYield-Signature": signature,
            "X-StableYield-Timestamp": timestamp
        }
        
        # Attempt delivery with retries
        for attempt in range(self.config["webhook"]["retry_attempts"]):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        webhook.url,
                        json=payload,
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=self.config["webhook"]["timeout_seconds"])
                    ) as response:
                        if response.status < 400:
                            # Success
                            webhook.last_triggered = datetime.utcnow()
                            self.api_metrics["webhook_deliveries"] += 1
                            logger.debug(f"✅ Webhook delivered to {webhook.url}")
                            return
                        else:
                            logger.warning(f"⚠️ Webhook delivery failed (attempt {attempt + 1}): HTTP {response.status}")
                
            except Exception as e:
                logger.warning(f"⚠️ Webhook delivery error (attempt {attempt + 1}): {e}")
            
            # Wait before retry (except on last attempt)
            if attempt < self.config["webhook"]["retry_attempts"] - 1:
                await asyncio.sleep(self.config["webhook"]["retry_delay_seconds"])
        
        logger.error(f"❌ Failed to deliver webhook to {webhook.url} after {self.config['webhook']['retry_attempts']} attempts")
    
    def _create_webhook_signature(self, payload: str, secret: str) -> str:
        """Create webhook signature for verification"""
        return hashlib.sha256(f"{secret}{payload}".encode()).hexdigest()
    
    # External Integrations
    async def add_external_integration(self, provider: str, api_key: str, endpoint_url: str, rate_limit: int = 100) -> ExternalIntegration:
        """Add external API integration"""
        integration_id = str(uuid.uuid4())
        
        integration = ExternalIntegration(
            integration_id=integration_id,
            provider=provider,
            api_key=api_key,
            endpoint_url=endpoint_url,
            rate_limit=rate_limit,
            is_active=True
        )
        
        self.external_integrations[integration_id] = integration
        await self._save_external_integrations()
        
        logger.info(f"🔌 Added external integration: {provider}")
        return integration
    
    async def call_external_api(self, integration_id: str, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make authenticated call to external API"""
        if integration_id not in self.external_integrations:
            raise ValueError(f"Integration {integration_id} not found")
        
        integration = self.external_integrations[integration_id]
        if not integration.is_active:
            raise ValueError(f"Integration {integration_id} is not active")
        
        url = f"{integration.endpoint_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        headers = {
            "Authorization": f"Bearer {integration.api_key}",
            "User-Agent": "StableYield-Enterprise/1.0"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        integration.last_sync = datetime.utcnow()
                        self.api_metrics["external_api_calls"] += 1
                        return await response.json()
                    else:
                        raise HTTPException(status_code=response.status, detail=f"External API error: {response.status}")
        
        except Exception as e:
            logger.error(f"❌ External API call failed: {e}")
            raise
    
    # JWT Token Management
    def create_jwt_token(self, client_id: str, permissions: List[str]) -> str:
        """Create JWT token for client"""
        payload = {
            "client_id": client_id,
            "permissions": permissions,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=self.jwt_expiry_hours)
        }
        
        token = jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
        return token
    
    def verify_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid JWT token")
            return None
    
    # Background Tasks
    async def _health_monitor(self):
        """Monitor service health"""
        while self.is_running:
            try:
                # Check various health metrics
                health_status = {
                    "api_gateway": "healthy",
                    "webhook_queue_size": self.webhook_queue.qsize(),
                    "active_api_keys": len([k for k in self.api_keys.values() if k.is_active]),
                    "active_webhooks": len([w for w in self.webhooks.values() if w.is_active]),
                    "active_integrations": len([i for i in self.external_integrations.values() if i.is_active]),
                    "rate_limit_buckets": len(self.rate_limit_buckets),
                    "last_check": datetime.utcnow().isoformat()
                }
                
                # Save health status
                health_file = self.data_dir / "health_status.json"
                with open(health_file, 'w') as f:
                    json.dump(health_status, f, indent=2, default=str)
                
                await asyncio.sleep(self.config["monitoring"]["health_check_interval"])
                
            except Exception as e:
                logger.error(f"❌ Health monitor error: {e}")
                await asyncio.sleep(30)
    
    async def _metrics_collector(self):
        """Collect and aggregate metrics"""
        while self.is_running:
            try:
                # Save current metrics
                metrics_file = self.data_dir / f"metrics_{datetime.utcnow().strftime('%Y%m%d_%H')}.json"
                
                extended_metrics = {
                    **self.api_metrics,
                    "timestamp": datetime.utcnow().isoformat(),
                    "success_rate": (self.api_metrics["successful_requests"] / max(1, self.api_metrics["total_requests"])) * 100,
                    "rate_limit_percentage": (self.api_metrics["rate_limited_requests"] / max(1, self.api_metrics["total_requests"])) * 100
                }
                
                with open(metrics_file, 'w') as f:
                    json.dump(extended_metrics, f, indent=2)
                
                # Clean old metrics files
                await self._clean_old_metrics()
                
                await asyncio.sleep(3600)  # Every hour
                
            except Exception as e:
                logger.error(f"❌ Metrics collector error: {e}")
                await asyncio.sleep(3600)
    
    async def _rate_limit_cleaner(self):
        """Clean expired rate limit buckets"""
        while self.is_running:
            try:
                current_time = datetime.utcnow()
                expired_buckets = []
                
                for bucket_key, bucket in self.rate_limit_buckets.items():
                    if (current_time - bucket.window_start).total_seconds() > 300:  # 5 minutes old
                        expired_buckets.append(bucket_key)
                
                for bucket_key in expired_buckets:
                    del self.rate_limit_buckets[bucket_key]
                
                if expired_buckets:
                    logger.debug(f"🧹 Cleaned {len(expired_buckets)} expired rate limit buckets")
                
                await asyncio.sleep(300)  # Every 5 minutes
                
            except Exception as e:
                logger.error(f"❌ Rate limit cleaner error: {e}")
                await asyncio.sleep(300)
    
    async def _clean_old_metrics(self):
        """Clean old metrics files"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=self.config["monitoring"]["metrics_retention_hours"])
            
            for metrics_file in self.data_dir.glob("metrics_*.json"):
                if metrics_file.stat().st_mtime < cutoff_time.timestamp():
                    metrics_file.unlink()
        except Exception as e:
            logger.error(f"❌ Error cleaning old metrics: {e}")
    
    # Data Persistence
    async def _load_api_keys(self):
        """Load API keys from storage"""
        try:
            api_keys_file = self.data_dir / "api_keys.json"
            if api_keys_file.exists():
                with open(api_keys_file, 'r') as f:
                    data = json.load(f)
                
                for key_data in data:
                    api_key_obj = APIKey(**key_data)
                    api_key_obj.created_at = datetime.fromisoformat(api_key_obj.created_at)
                    if api_key_obj.last_used:
                        api_key_obj.last_used = datetime.fromisoformat(api_key_obj.last_used)
                    
                    self.api_keys[api_key_obj.api_key] = api_key_obj
                
                logger.info(f"📂 Loaded {len(self.api_keys)} API keys")
        except Exception as e:
            logger.error(f"❌ Error loading API keys: {e}")
    
    async def _save_api_keys(self):
        """Save API keys to storage"""
        try:
            api_keys_file = self.data_dir / "api_keys.json"
            data = []
            
            for api_key_obj in self.api_keys.values():
                key_data = asdict(api_key_obj)
                key_data['created_at'] = api_key_obj.created_at.isoformat()
                if api_key_obj.last_used:
                    key_data['last_used'] = api_key_obj.last_used.isoformat()
                data.append(key_data)
            
            with open(api_keys_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"❌ Error saving API keys: {e}")
    
    async def _load_webhooks(self):
        """Load webhooks from storage"""
        try:
            webhooks_file = self.data_dir / "webhooks.json"
            if webhooks_file.exists():
                with open(webhooks_file, 'r') as f:
                    data = json.load(f)
                
                for webhook_data in data:
                    webhook = WebhookConfig(**webhook_data)
                    webhook.created_at = datetime.fromisoformat(webhook.created_at)
                    if webhook.last_triggered:
                        webhook.last_triggered = datetime.fromisoformat(webhook.last_triggered)
                    
                    self.webhooks[webhook.webhook_id] = webhook
                
                logger.info(f"📂 Loaded {len(self.webhooks)} webhooks")
        except Exception as e:
            logger.error(f"❌ Error loading webhooks: {e}")
    
    async def _save_webhooks(self):
        """Save webhooks to storage"""
        try:
            webhooks_file = self.data_dir / "webhooks.json"
            data = []
            
            for webhook in self.webhooks.values():
                webhook_data = asdict(webhook)
                webhook_data['created_at'] = webhook.created_at.isoformat()
                if webhook.last_triggered:
                    webhook_data['last_triggered'] = webhook.last_triggered.isoformat()
                data.append(webhook_data)
            
            with open(webhooks_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"❌ Error saving webhooks: {e}")
    
    async def _load_external_integrations(self):
        """Load external integrations from storage"""
        try:
            integrations_file = self.data_dir / "external_integrations.json"
            if integrations_file.exists():
                with open(integrations_file, 'r') as f:
                    data = json.load(f)
                
                for integration_data in data:
                    integration = ExternalIntegration(**integration_data)
                    if integration.last_sync:
                        integration.last_sync = datetime.fromisoformat(integration.last_sync)
                    
                    self.external_integrations[integration.integration_id] = integration
                
                logger.info(f"📂 Loaded {len(self.external_integrations)} external integrations")
        except Exception as e:
            logger.error(f"❌ Error loading external integrations: {e}")
    
    async def _save_external_integrations(self):
        """Save external integrations to storage"""
        try:
            integrations_file = self.data_dir / "external_integrations.json"
            data = []
            
            for integration in self.external_integrations.values():
                integration_data = asdict(integration)
                if integration.last_sync:
                    integration_data['last_sync'] = integration.last_sync.isoformat()
                data.append(integration_data)
            
            with open(integrations_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"❌ Error saving external integrations: {e}")
    
    # Status and Management
    def get_gateway_status(self) -> Dict[str, Any]:
        """Get API Gateway status"""
        return {
            "service_running": self.is_running,
            "api_keys": {
                "total": len(self.api_keys),
                "active": len([k for k in self.api_keys.values() if k.is_active]),
                "by_tier": {
                    tier: len([k for k in self.api_keys.values() if k.tier == tier])
                    for tier in ["basic", "premium", "enterprise"]
                }
            },
            "webhooks": {
                "total": len(self.webhooks),
                "active": len([w for w in self.webhooks.values() if w.is_active]),
                "queue_size": self.webhook_queue.qsize()
            },
            "external_integrations": {
                "total": len(self.external_integrations),
                "active": len([i for i in self.external_integrations.values() if i.is_active])
            },
            "rate_limiting": {
                "active_buckets": len(self.rate_limit_buckets),
                "configuration": self.config["rate_limiting"]
            },
            "metrics": self.api_metrics,
            "last_updated": datetime.utcnow().isoformat()
        }

# Global API Gateway service instance
api_gateway_service = None

async def start_api_gateway():
    """Start the global API Gateway service"""
    global api_gateway_service
    
    if api_gateway_service is None:
        api_gateway_service = APIGatewayService()
        await api_gateway_service.start()
        logger.info("🚀 API Gateway service started")
    else:
        logger.info("⚠️ API Gateway service already running")

async def stop_api_gateway():
    """Stop the global API Gateway service"""
    global api_gateway_service
    
    if api_gateway_service:
        await api_gateway_service.stop()
        api_gateway_service = None
        logger.info("🛑 API Gateway service stopped")

def get_api_gateway_service() -> Optional[APIGatewayService]:
    """Get the global API Gateway service"""
    return api_gateway_service