#!/usr/bin/env python3
"""
StableYield Enterprise Integration & API Gateway Test Suite (STEP 9)
Tests all enterprise endpoints comprehensively
"""

import asyncio
import aiohttp
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment - use production URL for testing
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://stableyield-trade.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class EnterpriseAPITester:
    def __init__(self):
        self.session = None
        self.test_results = []
        
        # Store test data for enterprise tests
        self.test_api_key = None
        self.test_key_id = None
        self.test_webhook_id = None
        self.test_integration_id = None
        self.test_jwt_token = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    Details: {details}")
        if response_data and not success:
            print(f"    Response: {response_data}")
        
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    async def test_enterprise_status(self):
        """Test GET /api/enterprise/status endpoint"""
        try:
            async with self.session.get(f"{API_BASE}/enterprise/status") as response:
                if response.status == 200:
                    data = await response.json()
                    required_fields = ['service_running', 'api_keys', 'webhooks', 'external_integrations']
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if not missing_fields:
                        service_running = data['service_running']
                        api_keys_total = data['api_keys']['total']
                        webhooks_total = data['webhooks']['total']
                        integrations_total = data['external_integrations']['total']
                        
                        self.log_test("Enterprise Status", True, 
                                    f"Service running: {service_running}, API keys: {api_keys_total}, Webhooks: {webhooks_total}, Integrations: {integrations_total}")
                    else:
                        self.log_test("Enterprise Status", False, f"Missing fields: {missing_fields}")
                else:
                    self.log_test("Enterprise Status", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Enterprise Status", False, f"Exception: {str(e)}")
    
    async def test_enterprise_start(self):
        """Test POST /api/enterprise/start endpoint"""
        try:
            async with self.session.post(f"{API_BASE}/enterprise/start") as response:
                if response.status == 200:
                    data = await response.json()
                    if 'message' in data and 'features' in data and 'rate_limits' in data:
                        features = data['features']
                        rate_limits = data['rate_limits']
                        
                        if isinstance(features, list) and len(features) >= 5:
                            self.log_test("Enterprise Start", True, 
                                        f"Started with {len(features)} features, rate limits: {list(rate_limits.keys())}")
                        else:
                            self.log_test("Enterprise Start", False, f"Expected 5+ features, got: {features}")
                    else:
                        self.log_test("Enterprise Start", False, f"Invalid response structure: {data}")
                else:
                    self.log_test("Enterprise Start", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Enterprise Start", False, f"Exception: {str(e)}")
    
    async def test_enterprise_create_api_key(self):
        """Test POST /api/enterprise/api-keys endpoint"""
        try:
            payload = {
                "client_name": f"test_client_{uuid.uuid4().hex[:8]}",
                "tier": "basic"
            }
            
            async with self.session.post(f"{API_BASE}/enterprise/api-keys", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'api_key' in data and 'usage_instructions' in data:
                        api_key_info = data['api_key']
                        usage_info = data['usage_instructions']
                        
                        required_key_fields = ['key_id', 'api_key', 'client_name', 'tier', 'rate_limit_per_minute']
                        missing_key_fields = [field for field in required_key_fields if field not in api_key_info]
                        
                        if not missing_key_fields:
                            self.test_api_key = api_key_info['api_key']  # Store for other tests
                            self.test_key_id = api_key_info['key_id']
                            self.log_test("Enterprise Create API Key", True, 
                                        f"Created {api_key_info['tier']} key for {api_key_info['client_name']}, rate limit: {api_key_info['rate_limit_per_minute']}/min")
                        else:
                            self.log_test("Enterprise Create API Key", False, f"Missing key fields: {missing_key_fields}")
                    else:
                        self.log_test("Enterprise Create API Key", False, f"Invalid response structure: {data}")
                else:
                    self.log_test("Enterprise Create API Key", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Enterprise Create API Key", False, f"Exception: {str(e)}")
    
    async def test_enterprise_list_api_keys(self):
        """Test GET /api/enterprise/api-keys endpoint"""
        try:
            async with self.session.get(f"{API_BASE}/enterprise/api-keys") as response:
                if response.status == 200:
                    data = await response.json()
                    if 'api_keys' in data and 'total_keys' in data and 'distribution_by_tier' in data:
                        api_keys = data['api_keys']
                        total_keys = data['total_keys']
                        active_keys = data['active_keys']
                        distribution = data['distribution_by_tier']
                        
                        self.log_test("Enterprise List API Keys", True, 
                                    f"Found {total_keys} keys ({active_keys} active), distribution: {distribution}")
                    else:
                        self.log_test("Enterprise List API Keys", False, f"Invalid response structure: {data}")
                else:
                    self.log_test("Enterprise List API Keys", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Enterprise List API Keys", False, f"Exception: {str(e)}")
    
    async def test_enterprise_create_webhook(self):
        """Test POST /api/enterprise/webhooks endpoint"""
        try:
            payload = {
                "client_id": f"test_client_{uuid.uuid4().hex[:8]}",
                "url": "https://webhook.site/test-stableyield",
                "events": ["yield_update", "anomaly_alert"],
                "secret": "test_webhook_secret"
            }
            
            async with self.session.post(f"{API_BASE}/enterprise/webhooks", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'webhook' in data and 'webhook_secret' in data and 'verification_info' in data:
                        webhook_info = data['webhook']
                        verification_info = data['verification_info']
                        
                        required_webhook_fields = ['webhook_id', 'client_id', 'url', 'events', 'is_active']
                        missing_webhook_fields = [field for field in required_webhook_fields if field not in webhook_info]
                        
                        if not missing_webhook_fields:
                            self.test_webhook_id = webhook_info['webhook_id']  # Store for other tests
                            self.log_test("Enterprise Create Webhook", True, 
                                        f"Created webhook for {webhook_info['client_id']}, events: {len(webhook_info['events'])}")
                        else:
                            self.log_test("Enterprise Create Webhook", False, f"Missing webhook fields: {missing_webhook_fields}")
                    else:
                        self.log_test("Enterprise Create Webhook", False, f"Invalid response structure: {data}")
                else:
                    self.log_test("Enterprise Create Webhook", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Enterprise Create Webhook", False, f"Exception: {str(e)}")
    
    async def test_enterprise_list_webhooks(self):
        """Test GET /api/enterprise/webhooks endpoint"""
        try:
            async with self.session.get(f"{API_BASE}/enterprise/webhooks") as response:
                if response.status == 200:
                    data = await response.json()
                    if 'webhooks' in data and 'total_webhooks' in data and 'webhooks_by_client' in data:
                        webhooks = data['webhooks']
                        total_webhooks = data['total_webhooks']
                        active_webhooks = data['active_webhooks']
                        queue_size = data.get('webhook_queue_size', 0)
                        
                        self.log_test("Enterprise List Webhooks", True, 
                                    f"Found {total_webhooks} webhooks ({active_webhooks} active), queue size: {queue_size}")
                    else:
                        self.log_test("Enterprise List Webhooks", False, f"Invalid response structure: {data}")
                else:
                    self.log_test("Enterprise List Webhooks", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Enterprise List Webhooks", False, f"Exception: {str(e)}")
    
    async def test_enterprise_create_integration(self):
        """Test POST /api/enterprise/integrations endpoint"""
        try:
            payload = {
                "provider": "custom",
                "api_key": "test_integration_key",
                "endpoint_url": "https://api.example.com/v1",
                "rate_limit": 100
            }
            
            async with self.session.post(f"{API_BASE}/enterprise/integrations", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'integration' in data and 'usage_info' in data:
                        integration_info = data['integration']
                        usage_info = data['usage_info']
                        
                        required_integration_fields = ['integration_id', 'provider', 'endpoint_url', 'rate_limit', 'is_active']
                        missing_integration_fields = [field for field in required_integration_fields if field not in integration_info]
                        
                        if not missing_integration_fields:
                            self.test_integration_id = integration_info['integration_id']  # Store for other tests
                            self.log_test("Enterprise Create Integration", True, 
                                        f"Created {integration_info['provider']} integration, rate limit: {integration_info['rate_limit']}/min")
                        else:
                            self.log_test("Enterprise Create Integration", False, f"Missing integration fields: {missing_integration_fields}")
                    else:
                        self.log_test("Enterprise Create Integration", False, f"Invalid response structure: {data}")
                else:
                    self.log_test("Enterprise Create Integration", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Enterprise Create Integration", False, f"Exception: {str(e)}")
    
    async def test_enterprise_list_integrations(self):
        """Test GET /api/enterprise/integrations endpoint"""
        try:
            async with self.session.get(f"{API_BASE}/enterprise/integrations") as response:
                if response.status == 200:
                    data = await response.json()
                    if 'integrations' in data and 'total_integrations' in data and 'integrations_by_provider' in data:
                        integrations = data['integrations']
                        total_integrations = data['total_integrations']
                        active_integrations = data['active_integrations']
                        by_provider = data['integrations_by_provider']
                        
                        self.log_test("Enterprise List Integrations", True, 
                                    f"Found {total_integrations} integrations ({active_integrations} active), providers: {list(by_provider.keys())}")
                    else:
                        self.log_test("Enterprise List Integrations", False, f"Invalid response structure: {data}")
                else:
                    self.log_test("Enterprise List Integrations", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Enterprise List Integrations", False, f"Exception: {str(e)}")
    
    async def test_enterprise_create_jwt_token(self):
        """Test POST /api/enterprise/auth/token endpoint"""
        try:
            params = {
                "client_id": "test_client",
                "permissions": ["read", "write"]
            }
            
            async with self.session.post(f"{API_BASE}/enterprise/auth/token", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'access_token' in data and 'token_type' in data and 'expires_in' in data:
                        access_token = data['access_token']
                        token_type = data['token_type']
                        expires_in = data['expires_in']
                        permissions = data.get('permissions', [])
                        
                        if access_token and token_type == "Bearer" and expires_in > 0:
                            self.test_jwt_token = access_token  # Store for verification test
                            self.log_test("Enterprise Create JWT Token", True, 
                                        f"Created {token_type} token, expires in {expires_in}s, permissions: {permissions}")
                        else:
                            self.log_test("Enterprise Create JWT Token", False, f"Invalid token data: {data}")
                    else:
                        self.log_test("Enterprise Create JWT Token", False, f"Invalid response structure: {data}")
                else:
                    self.log_test("Enterprise Create JWT Token", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Enterprise Create JWT Token", False, f"Exception: {str(e)}")
    
    async def test_enterprise_metrics(self):
        """Test GET /api/enterprise/metrics endpoint"""
        try:
            async with self.session.get(f"{API_BASE}/enterprise/metrics") as response:
                if response.status == 200:
                    data = await response.json()
                    if 'raw_metrics' in data and 'calculated_metrics' in data and 'service_health' in data:
                        raw_metrics = data['raw_metrics']
                        calculated_metrics = data['calculated_metrics']
                        service_health = data['service_health']
                        
                        total_requests = calculated_metrics.get('total_requests', 0)
                        success_rate = calculated_metrics.get('success_rate_percentage', 0)
                        active_api_keys = service_health.get('active_api_keys', 0)
                        
                        self.log_test("Enterprise Metrics", True, 
                                    f"Total requests: {total_requests}, success rate: {success_rate:.1f}%, active API keys: {active_api_keys}")
                    else:
                        self.log_test("Enterprise Metrics", False, f"Invalid response structure: {data}")
                else:
                    self.log_test("Enterprise Metrics", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Enterprise Metrics", False, f"Exception: {str(e)}")
    
    async def test_enterprise_health(self):
        """Test GET /api/enterprise/health endpoint"""
        try:
            async with self.session.get(f"{API_BASE}/enterprise/health") as response:
                if response.status == 200:
                    data = await response.json()
                    if 'status' in data and 'components' in data:
                        status = data['status']
                        components = data['components']
                        unhealthy_components = data.get('unhealthy_components', [])
                        
                        healthy_count = len([comp for comp in components.values() if comp.get('status') == 'healthy'])
                        total_components = len(components)
                        
                        if status == 'healthy' and len(unhealthy_components) == 0:
                            self.log_test("Enterprise Health", True, 
                                        f"All {total_components} components healthy: {list(components.keys())}")
                        else:
                            self.log_test("Enterprise Health", True, 
                                        f"Status: {status}, {healthy_count}/{total_components} components healthy, unhealthy: {unhealthy_components}")
                    else:
                        self.log_test("Enterprise Health", False, f"Invalid response structure: {data}")
                else:
                    self.log_test("Enterprise Health", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Enterprise Health", False, f"Exception: {str(e)}")
    
    async def test_enterprise_summary(self):
        """Test GET /api/enterprise/summary endpoint"""
        try:
            async with self.session.get(f"{API_BASE}/enterprise/summary") as response:
                if response.status == 200:
                    data = await response.json()
                    if 'service_status' in data and 'enterprise_features' in data:
                        service_status = data['service_status']
                        enterprise_features = data['enterprise_features']
                        api_endpoints = data.get('api_endpoints', [])
                        security_features = data.get('security_features', [])
                        
                        # Check enterprise features
                        expected_features = ['api_key_management', 'webhook_system', 'external_integrations', 'rate_limiting']
                        found_features = [feature for feature in expected_features if feature in enterprise_features]
                        
                        if len(found_features) >= 4:
                            self.log_test("Enterprise Summary", True, 
                                        f"Service: {service_status}, {len(found_features)} features, {len(api_endpoints)} endpoints, {len(security_features)} security features")
                        else:
                            self.log_test("Enterprise Summary", False, 
                                        f"Missing expected features. Found: {found_features}, Expected: {expected_features}")
                    else:
                        self.log_test("Enterprise Summary", False, f"Invalid response structure: {data}")
                else:
                    self.log_test("Enterprise Summary", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Enterprise Summary", False, f"Exception: {str(e)}")
    
    async def test_enterprise_stop(self):
        """Test POST /api/enterprise/stop endpoint"""
        try:
            async with self.session.post(f"{API_BASE}/enterprise/stop") as response:
                if response.status == 200:
                    data = await response.json()
                    if 'message' in data and 'stopped' in data['message'].lower():
                        self.log_test("Enterprise Stop", True, f"Service stopped: {data['message']}")
                    else:
                        self.log_test("Enterprise Stop", False, f"Unexpected response: {data}")
                else:
                    self.log_test("Enterprise Stop", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Enterprise Stop", False, f"Exception: {str(e)}")
    
    async def run_all_enterprise_tests(self):
        """Run all enterprise tests"""
        print(f"🏢 Starting StableYield Enterprise Integration & API Gateway Tests (STEP 9)")
        print(f"📍 Backend URL: {BACKEND_URL}")
        print(f"📍 API Base: {API_BASE}")
        print("=" * 80)
        
        # Test all 13 enterprise endpoints
        await self.test_enterprise_status()
        await self.test_enterprise_start()
        await self.test_enterprise_create_api_key()
        await self.test_enterprise_list_api_keys()
        await self.test_enterprise_create_webhook()
        await self.test_enterprise_list_webhooks()
        await self.test_enterprise_create_integration()
        await self.test_enterprise_list_integrations()
        await self.test_enterprise_create_jwt_token()
        await self.test_enterprise_metrics()
        await self.test_enterprise_health()
        await self.test_enterprise_summary()
        await self.test_enterprise_stop()
        
        # Summary
        print("\n" + "=" * 80)
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"📋 ENTERPRISE INTEGRATION & API GATEWAY TEST SUMMARY (STEP 9)")
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['details']}")
        
        print(f"\n🎯 CRITICAL ENTERPRISE FEATURES:")
        critical_features = [
            "Enterprise Status", "Enterprise Start", "Enterprise Create API Key", 
            "Enterprise Create Webhook", "Enterprise Create Integration", 
            "Enterprise Create JWT Token", "Enterprise Health", "Enterprise Summary"
        ]
        
        critical_failures = []
        for result in self.test_results:
            if not result['success'] and result['test'] in critical_features:
                critical_failures.append(result['test'])
        
        if critical_failures:
            for failure in critical_failures:
                print(f"  ❌ {failure}")
        else:
            print("  ✅ All critical enterprise features working!")

async def main():
    """Main test runner"""
    async with EnterpriseAPITester() as tester:
        await tester.run_all_enterprise_tests()

if __name__ == "__main__":
    asyncio.run(main())