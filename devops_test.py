#!/usr/bin/env python3
"""
DevOps & Production Deployment System (STEP 10) Test Suite
Focused testing of the new DevOps endpoints
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
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://yield-index-dash.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class DevOpsTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        
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
    
    async def test_devops_status(self):
        """Test GET /api/devops/status endpoint"""
        try:
            async with self.session.get(f"{API_BASE}/devops/status") as response:
                if response.status == 200:
                    data = await response.json()
                    required_fields = ['service_running', 'current_deployment', 'system_metrics', 'alerts', 'backups']
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if not missing_fields:
                        service_running = data['service_running']
                        alerts_total = data['alerts']['total_rules']
                        backups_total = data['backups']['total_backups']
                        
                        self.log_test("DevOps Status", True, 
                                    f"Service running: {service_running}, Alert rules: {alerts_total}, Backups: {backups_total}")
                    else:
                        self.log_test("DevOps Status", False, f"Missing fields: {missing_fields}")
                else:
                    self.log_test("DevOps Status", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("DevOps Status", False, f"Exception: {str(e)}")
    
    async def test_devops_start(self):
        """Test POST /api/devops/start endpoint"""
        try:
            async with self.session.post(f"{API_BASE}/devops/start") as response:
                if response.status == 200:
                    data = await response.json()
                    if 'message' in data and 'capabilities' in data and 'infrastructure_components' in data:
                        capabilities = data['capabilities']
                        components = data['infrastructure_components']
                        
                        if isinstance(capabilities, list) and len(capabilities) >= 5:
                            self.log_test("DevOps Start", True, 
                                        f"Started with {len(capabilities)} capabilities, {len(components)} infrastructure components")
                        else:
                            self.log_test("DevOps Start", False, f"Expected 5+ capabilities, got: {capabilities}")
                    else:
                        self.log_test("DevOps Start", False, f"Invalid response structure: {data}")
                else:
                    self.log_test("DevOps Start", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("DevOps Start", False, f"Exception: {str(e)}")
    
    async def test_devops_deploy(self):
        """Test POST /api/devops/deploy endpoint"""
        try:
            payload = {
                "version": "1.0.0",
                "environment": "production",
                "services": ["backend", "frontend", "database"]
            }
            
            async with self.session.post(f"{API_BASE}/devops/deploy", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'deployment' in data and 'status' in data:
                        deployment = data['deployment']
                        status = data['status']
                        
                        required_deployment_fields = ['build_number', 'version', 'environment', 'services', 'deployment_time']
                        missing_fields = [field for field in required_deployment_fields if field not in deployment]
                        
                        if not missing_fields and status == 'completed':
                            self.log_test("DevOps Deploy", True, 
                                        f"Deployed v{deployment['version']} to {deployment['environment']}, build #{deployment['build_number']}")
                        else:
                            self.log_test("DevOps Deploy", False, f"Missing fields: {missing_fields} or status not completed: {status}")
                    else:
                        self.log_test("DevOps Deploy", False, f"Invalid response structure: {data}")
                elif response.status == 503:
                    self.log_test("DevOps Deploy", False, "DevOps service not running (expected if not started)")
                else:
                    self.log_test("DevOps Deploy", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("DevOps Deploy", False, f"Exception: {str(e)}")
    
    async def test_devops_deployments(self):
        """Test GET /api/devops/deployments endpoint"""
        try:
            async with self.session.get(f"{API_BASE}/devops/deployments") as response:
                if response.status == 200:
                    data = await response.json()
                    required_fields = ['deployments', 'total_deployments', 'current_deployment', 'environments']
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if not missing_fields:
                        deployments = data['deployments']
                        total = data['total_deployments']
                        current = data['current_deployment']
                        environments = data['environments']
                        
                        self.log_test("DevOps Deployments", True, 
                                    f"Found {total} deployments, current: {current}, environments: {list(environments.keys())}")
                    else:
                        self.log_test("DevOps Deployments", False, f"Missing fields: {missing_fields}")
                elif response.status == 503:
                    self.log_test("DevOps Deployments", False, "DevOps service not running (expected if not started)")
                else:
                    self.log_test("DevOps Deployments", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("DevOps Deployments", False, f"Exception: {str(e)}")
    
    async def test_devops_metrics(self):
        """Test GET /api/devops/metrics endpoint"""
        try:
            async with self.session.get(f"{API_BASE}/devops/metrics?hours=1") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if 'metrics' in data or 'message' in data:
                        if 'metrics' in data and data['metrics']:
                            metrics = data['metrics']
                            summary = data.get('summary', {})
                            self.log_test("DevOps Metrics", True, 
                                        f"Retrieved {len(metrics)} data points, avg CPU: {summary.get('average_metrics', {}).get('cpu_usage', 0):.1f}%")
                        else:
                            # No metrics available yet (expected for new service)
                            message = data.get('message', 'No metrics data')
                            self.log_test("DevOps Metrics", True, f"Service ready: {message}")
                    else:
                        self.log_test("DevOps Metrics", False, f"Invalid response structure: {data}")
                elif response.status == 503:
                    self.log_test("DevOps Metrics", False, "DevOps service not running (expected if not started)")
                else:
                    self.log_test("DevOps Metrics", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("DevOps Metrics", False, f"Exception: {str(e)}")
    
    async def test_devops_alerts(self):
        """Test GET /api/devops/alerts endpoint"""
        try:
            async with self.session.get(f"{API_BASE}/devops/alerts") as response:
                if response.status == 200:
                    data = await response.json()
                    required_fields = ['alert_rules', 'active_alerts', 'total_rules', 'total_active_alerts', 'alerts_by_severity']
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if not missing_fields:
                        alert_rules = data['alert_rules']
                        active_alerts = data['active_alerts']
                        total_rules = data['total_rules']
                        total_active = data['total_active_alerts']
                        by_severity = data['alerts_by_severity']
                        
                        self.log_test("DevOps Alerts", True, 
                                    f"Rules: {total_rules}, Active alerts: {total_active}, Severity breakdown: {by_severity}")
                    else:
                        self.log_test("DevOps Alerts", False, f"Missing fields: {missing_fields}")
                elif response.status == 503:
                    self.log_test("DevOps Alerts", False, "DevOps service not running (expected if not started)")
                else:
                    self.log_test("DevOps Alerts", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("DevOps Alerts", False, f"Exception: {str(e)}")
    
    async def test_devops_create_alert_rule(self):
        """Test POST /api/devops/alerts/rules endpoint"""
        try:
            payload = {
                "rule_id": f"test_cpu_alert_{uuid.uuid4().hex[:8]}",
                "metric": "cpu_usage",
                "threshold": 80.0,
                "operator": "gt",
                "severity": "warning",
                "notification_channels": ["email", "slack"]
            }
            
            async with self.session.post(f"{API_BASE}/devops/alerts/rules", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'message' in data and 'alert_rule' in data:
                        alert_rule = data['alert_rule']
                        rule_id = alert_rule.get('rule_id')
                        metric = alert_rule.get('metric')
                        threshold = alert_rule.get('threshold')
                        
                        if rule_id and metric and threshold:
                            self.log_test("DevOps Create Alert Rule", True, 
                                        f"Created rule '{rule_id}' for {metric} > {threshold}")
                        else:
                            self.log_test("DevOps Create Alert Rule", False, f"Incomplete alert rule data: {alert_rule}")
                    else:
                        self.log_test("DevOps Create Alert Rule", False, f"Invalid response structure: {data}")
                elif response.status == 503:
                    self.log_test("DevOps Create Alert Rule", False, "DevOps service not running (expected if not started)")
                else:
                    self.log_test("DevOps Create Alert Rule", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("DevOps Create Alert Rule", False, f"Exception: {str(e)}")
    
    async def test_devops_backups(self):
        """Test GET /api/devops/backups endpoint"""
        try:
            async with self.session.get(f"{API_BASE}/devops/backups") as response:
                if response.status == 200:
                    data = await response.json()
                    required_fields = ['backups', 'total_backups', 'successful_backups', 'failed_backups', 'backups_by_type', 'total_storage']
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if not missing_fields:
                        backups = data['backups']
                        total = data['total_backups']
                        successful = data['successful_backups']
                        failed = data['failed_backups']
                        by_type = data['backups_by_type']
                        storage = data['total_storage']
                        
                        self.log_test("DevOps Backups", True, 
                                    f"Total: {total}, Successful: {successful}, Failed: {failed}, Storage: {storage['size_gb']}GB, Types: {list(by_type.keys())}")
                    else:
                        self.log_test("DevOps Backups", False, f"Missing fields: {missing_fields}")
                elif response.status == 503:
                    self.log_test("DevOps Backups", False, "DevOps service not running (expected if not started)")
                else:
                    self.log_test("DevOps Backups", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("DevOps Backups", False, f"Exception: {str(e)}")
    
    async def test_devops_create_backup(self):
        """Test POST /api/devops/backups/database endpoint"""
        try:
            async with self.session.post(f"{API_BASE}/devops/backups/database") as response:
                if response.status == 200:
                    data = await response.json()
                    if 'message' in data and 'backup' in data:
                        backup = data['backup']
                        message = data['message']
                        
                        if backup and 'backup_id' in backup and 'backup_type' in backup:
                            backup_id = backup['backup_id']
                            backup_type = backup['backup_type']
                            size_mb = backup.get('size_mb', 0)
                            
                            self.log_test("DevOps Create Backup", True, 
                                        f"Created {backup_type} backup '{backup_id}', size: {size_mb}MB")
                        else:
                            self.log_test("DevOps Create Backup", False, f"Incomplete backup data: {backup}")
                    else:
                        self.log_test("DevOps Create Backup", False, f"Invalid response structure: {data}")
                elif response.status == 503:
                    self.log_test("DevOps Create Backup", False, "DevOps service not running (expected if not started)")
                else:
                    self.log_test("DevOps Create Backup", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("DevOps Create Backup", False, f"Exception: {str(e)}")
    
    async def test_devops_infrastructure(self):
        """Test GET /api/devops/infrastructure endpoint"""
        try:
            async with self.session.get(f"{API_BASE}/devops/infrastructure") as response:
                if response.status == 200:
                    data = await response.json()
                    required_fields = ['infrastructure_components', 'configuration', 'service_health', 'infrastructure_ready']
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if not missing_fields:
                        components = data['infrastructure_components']
                        config = data['configuration']
                        health = data['service_health']
                        ready = data['infrastructure_ready']
                        
                        docker_files = components.get('docker', {}).get('file_count', 0)
                        k8s_files = components.get('kubernetes', {}).get('manifest_count', 0)
                        monitoring_files = components.get('monitoring', {}).get('config_count', 0)
                        all_ready = ready.get('all_ready', False)
                        
                        self.log_test("DevOps Infrastructure", True, 
                                    f"Docker: {docker_files} files, K8s: {k8s_files} manifests, Monitoring: {monitoring_files} configs, Ready: {all_ready}")
                    else:
                        self.log_test("DevOps Infrastructure", False, f"Missing fields: {missing_fields}")
                elif response.status == 503:
                    self.log_test("DevOps Infrastructure", False, "DevOps service not running (expected if not started)")
                else:
                    self.log_test("DevOps Infrastructure", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("DevOps Infrastructure", False, f"Exception: {str(e)}")
    
    async def test_devops_health(self):
        """Test GET /api/devops/health endpoint"""
        try:
            async with self.session.get(f"{API_BASE}/devops/health") as response:
                if response.status == 200:
                    data = await response.json()
                    required_fields = ['status', 'timestamp', 'components']
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if not missing_fields:
                        status = data['status']
                        components = data['components']
                        unhealthy = data.get('unhealthy_components', [])
                        warning = data.get('warning_components', [])
                        environment = data.get('environment', 'unknown')
                        version = data.get('version', 'unknown')
                        
                        component_count = len(components)
                        healthy_count = len([c for c in components.values() if c.get('status') == 'healthy'])
                        
                        self.log_test("DevOps Health", True, 
                                    f"Status: {status}, Components: {healthy_count}/{component_count} healthy, Env: {environment}, Version: {version}")
                    else:
                        self.log_test("DevOps Health", False, f"Missing fields: {missing_fields}")
                else:
                    self.log_test("DevOps Health", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("DevOps Health", False, f"Exception: {str(e)}")
    
    async def test_devops_summary(self):
        """Test GET /api/devops/summary endpoint"""
        try:
            async with self.session.get(f"{API_BASE}/devops/summary") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if 'service_status' in data:
                        service_status = data['service_status']
                        
                        if service_status == 'running':
                            # Service is running, check for comprehensive data
                            required_fields = ['production_features', 'current_system_status', 'api_endpoints', 'production_capabilities']
                            missing_fields = [field for field in required_fields if field not in data]
                            
                            if not missing_fields:
                                features = data['production_features']
                                system_status = data['current_system_status']
                                endpoints = data['api_endpoints']
                                capabilities = data['production_capabilities']
                                
                                deployment_mgmt = features.get('deployment_management', {})
                                monitoring = features.get('monitoring_system', {})
                                backup = features.get('backup_system', {})
                                
                                self.log_test("DevOps Summary", True, 
                                            f"Service running with {len(capabilities)} capabilities, {len(endpoints)} endpoints, "
                                            f"Deployments: {deployment_mgmt.get('deployment_history', 0)}, "
                                            f"Monitoring: {monitoring.get('metrics_collected', 0)} metrics, "
                                            f"Backups: {backup.get('total_backups', 0)}")
                            else:
                                self.log_test("DevOps Summary", False, f"Service running but missing fields: {missing_fields}")
                        else:
                            # Service not running
                            self.log_test("DevOps Summary", True, f"Service status: {service_status} (expected if not started)")
                    else:
                        self.log_test("DevOps Summary", False, f"Invalid response structure: {data}")
                else:
                    self.log_test("DevOps Summary", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("DevOps Summary", False, f"Exception: {str(e)}")
    
    async def test_devops_stop(self):
        """Test POST /api/devops/stop endpoint"""
        try:
            async with self.session.post(f"{API_BASE}/devops/stop") as response:
                if response.status == 200:
                    data = await response.json()
                    if 'message' in data and 'stopped' in data['message'].lower():
                        self.log_test("DevOps Stop", True, f"Service stopped: {data['message']}")
                    else:
                        self.log_test("DevOps Stop", False, f"Unexpected response: {data}")
                else:
                    self.log_test("DevOps Stop", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("DevOps Stop", False, f"Exception: {str(e)}")

    async def run_devops_tests(self):
        """Run all DevOps tests"""
        print(f"🚀 Starting DevOps & Production Deployment System (STEP 10) Tests")
        print(f"📍 Backend URL: {BACKEND_URL}")
        print(f"📍 API Base: {API_BASE}")
        print("=" * 80)
        
        # Test all 13 DevOps endpoints
        await self.test_devops_status()
        await self.test_devops_start()
        await self.test_devops_deploy()
        await self.test_devops_deployments()
        await self.test_devops_metrics()
        await self.test_devops_alerts()
        await self.test_devops_create_alert_rule()
        await self.test_devops_backups()
        await self.test_devops_create_backup()
        await self.test_devops_infrastructure()
        await self.test_devops_health()
        await self.test_devops_summary()
        await self.test_devops_stop()
        
        # Summary
        print("\n" + "=" * 80)
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"📋 DEVOPS TESTING SUMMARY")
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['details']}")
        
        print(f"\n🎯 DEVOPS ENDPOINTS TESTED:")
        endpoints_tested = [
            "GET /api/devops/status",
            "POST /api/devops/start", 
            "POST /api/devops/deploy",
            "GET /api/devops/deployments",
            "GET /api/devops/metrics",
            "GET /api/devops/alerts",
            "POST /api/devops/alerts/rules",
            "GET /api/devops/backups",
            "POST /api/devops/backups/database",
            "GET /api/devops/infrastructure",
            "GET /api/devops/health",
            "GET /api/devops/summary",
            "POST /api/devops/stop"
        ]
        
        for endpoint in endpoints_tested:
            print(f"  - {endpoint}")

async def main():
    """Main test runner"""
    async with DevOpsTester() as tester:
        await tester.run_devops_tests()

if __name__ == "__main__":
    asyncio.run(main())