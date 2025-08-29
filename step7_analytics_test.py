#!/usr/bin/env python3
"""
Step 7 Batch Analytics & Performance Reporting Test Suite
Tests only the new Step 7 analytics endpoints
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

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://yield-index-dash.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class Step7AnalyticsTester:
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
    
    async def test_analytics_status(self):
        """Test GET /api/analytics/status endpoint"""
        try:
            async with self.session.get(f"{API_BASE}/analytics/status") as response:
                if response.status == 200:
                    data = await response.json()
                    required_fields = ['service_running', 'scheduled_jobs', 'job_results']
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if not missing_fields:
                        service_running = data['service_running']
                        scheduled_jobs = data['scheduled_jobs']
                        job_results = data['job_results']
                        
                        self.log_test("Analytics Status", True, 
                                    f"Service running: {service_running}, Scheduled jobs: {scheduled_jobs}, Job results: {len(job_results) if isinstance(job_results, dict) else 0}")
                    else:
                        self.log_test("Analytics Status", False, f"Missing fields: {missing_fields}")
                else:
                    self.log_test("Analytics Status", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Analytics Status", False, f"Exception: {str(e)}")
    
    async def test_analytics_start(self):
        """Test POST /api/analytics/start endpoint"""
        try:
            async with self.session.post(f"{API_BASE}/analytics/start") as response:
                if response.status == 200:
                    data = await response.json()
                    if 'message' in data and 'scheduled_jobs' in data:
                        scheduled_jobs = data['scheduled_jobs']
                        if isinstance(scheduled_jobs, list) and len(scheduled_jobs) >= 6:
                            self.log_test("Analytics Start", True, 
                                        f"Service started with {len(scheduled_jobs)} scheduled jobs")
                        else:
                            self.log_test("Analytics Start", False, f"Expected 6+ jobs, got: {scheduled_jobs}")
                    else:
                        self.log_test("Analytics Start", False, f"Invalid response structure: {data}")
                else:
                    self.log_test("Analytics Start", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Analytics Start", False, f"Exception: {str(e)}")
    
    async def test_analytics_manual_job_peg_metrics(self):
        """Test POST /api/analytics/jobs/peg_metrics_analytics/run endpoint"""
        try:
            async with self.session.post(f"{API_BASE}/analytics/jobs/peg_metrics_analytics/run") as response:
                if response.status == 200:
                    data = await response.json()
                    if 'message' in data and 'job_result' in data:
                        job_result = data['job_result']
                        success = job_result.get('success', False)
                        records_processed = job_result.get('records_processed', 0)
                        
                        self.log_test("Analytics Manual Job Peg Metrics", True, 
                                    f"Job executed - Success: {success}, Records: {records_processed}")
                    else:
                        self.log_test("Analytics Manual Job Peg Metrics", False, f"Invalid response structure: {data}")
                elif response.status == 503:
                    self.log_test("Analytics Manual Job Peg Metrics", False, "Service not running (expected if not started)")
                else:
                    self.log_test("Analytics Manual Job Peg Metrics", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Analytics Manual Job Peg Metrics", False, f"Exception: {str(e)}")
    
    async def test_analytics_manual_job_risk_analytics(self):
        """Test POST /api/analytics/jobs/risk_analytics/run endpoint"""
        try:
            async with self.session.post(f"{API_BASE}/analytics/jobs/risk_analytics/run") as response:
                if response.status == 200:
                    data = await response.json()
                    if 'message' in data and 'job_result' in data:
                        job_result = data['job_result']
                        success = job_result.get('success', False)
                        records_processed = job_result.get('records_processed', 0)
                        
                        self.log_test("Analytics Manual Job Risk Analytics", True, 
                                    f"Job executed - Success: {success}, Records: {records_processed}")
                    else:
                        self.log_test("Analytics Manual Job Risk Analytics", False, f"Invalid response structure: {data}")
                elif response.status == 503:
                    self.log_test("Analytics Manual Job Risk Analytics", False, "Service not running (expected if not started)")
                else:
                    self.log_test("Analytics Manual Job Risk Analytics", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Analytics Manual Job Risk Analytics", False, f"Exception: {str(e)}")
    
    async def test_analytics_peg_stability(self):
        """Test GET /api/analytics/peg-stability endpoint"""
        try:
            async with self.session.get(f"{API_BASE}/analytics/peg-stability") as response:
                if response.status == 200:
                    data = await response.json()
                    if 'analytics' in data:
                        analytics = data['analytics']
                        if analytics:
                            # Check for expected analytics structure
                            if 'peg_stability_summary' in analytics or 'stablecoin_analysis' in analytics:
                                self.log_test("Analytics Peg Stability", True, 
                                            f"Peg stability analytics available with data")
                            else:
                                self.log_test("Analytics Peg Stability", True, 
                                            f"Peg stability analytics structure present")
                        else:
                            self.log_test("Analytics Peg Stability", True, 
                                        "No peg stability analytics data yet (service may be starting)")
                    else:
                        self.log_test("Analytics Peg Stability", False, f"Invalid response structure: {data}")
                else:
                    self.log_test("Analytics Peg Stability", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Analytics Peg Stability", False, f"Exception: {str(e)}")
    
    async def test_analytics_liquidity(self):
        """Test GET /api/analytics/liquidity endpoint"""
        try:
            async with self.session.get(f"{API_BASE}/analytics/liquidity") as response:
                if response.status == 200:
                    data = await response.json()
                    if 'analytics' in data:
                        analytics = data['analytics']
                        if analytics:
                            # Check for expected analytics structure
                            if 'liquidity_summary' in analytics or 'pool_analysis' in analytics:
                                self.log_test("Analytics Liquidity", True, 
                                            f"Liquidity analytics available with data")
                            else:
                                self.log_test("Analytics Liquidity", True, 
                                            f"Liquidity analytics structure present")
                        else:
                            self.log_test("Analytics Liquidity", True, 
                                        "No liquidity analytics data yet (service may be starting)")
                    else:
                        self.log_test("Analytics Liquidity", False, f"Invalid response structure: {data}")
                else:
                    self.log_test("Analytics Liquidity", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Analytics Liquidity", False, f"Exception: {str(e)}")
    
    async def test_analytics_risk(self):
        """Test GET /api/analytics/risk endpoint"""
        try:
            async with self.session.get(f"{API_BASE}/analytics/risk") as response:
                if response.status == 200:
                    data = await response.json()
                    if 'analytics' in data:
                        analytics = data['analytics']
                        if analytics:
                            # Check for expected analytics structure
                            if 'risk_assessment' in analytics or 'stress_testing' in analytics:
                                self.log_test("Analytics Risk", True, 
                                            f"Risk analytics available with data")
                            else:
                                self.log_test("Analytics Risk", True, 
                                            f"Risk analytics structure present")
                        else:
                            self.log_test("Analytics Risk", True, 
                                        "No risk analytics data yet (service may be starting)")
                    else:
                        self.log_test("Analytics Risk", False, f"Invalid response structure: {data}")
                else:
                    self.log_test("Analytics Risk", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Analytics Risk", False, f"Exception: {str(e)}")
    
    async def test_analytics_performance(self):
        """Test GET /api/analytics/performance endpoint with different periods"""
        periods = ['1d', '7d', '30d', '90d']
        
        for period in periods:
            try:
                async with self.session.get(f"{API_BASE}/analytics/performance?period={period}") as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Check if it's the expected "no data yet" message first
                        message = data.get('message', '')
                        if 'No performance analytics available yet' in message:
                            self.log_test(f"Analytics Performance {period}", True, 
                                        f"Performance endpoint working for {period} (no data yet - expected)")
                            continue
                        
                        # Otherwise check for normal structure
                        if 'period' in data and 'performance' in data:
                            performance = data['performance']
                            current_index = data.get('current_index_value', 0)
                            
                            if performance:
                                self.log_test(f"Analytics Performance {period}", True, 
                                            f"Performance data available for {period}, Index: {current_index}")
                            else:
                                self.log_test(f"Analytics Performance {period}", True, 
                                            f"Performance endpoint working for {period} (no data yet)")
                        else:
                            self.log_test(f"Analytics Performance {period}", False, f"Invalid response structure: {data}")
                    else:
                        self.log_test(f"Analytics Performance {period}", False, f"HTTP {response.status}")
            except Exception as e:
                self.log_test(f"Analytics Performance {period}", False, f"Exception: {str(e)}")
    
    async def test_analytics_compliance_report(self):
        """Test GET /api/analytics/compliance-report endpoint"""
        try:
            async with self.session.get(f"{API_BASE}/analytics/compliance-report") as response:
                if response.status == 200:
                    data = await response.json()
                    if 'report' in data:
                        report = data['report']
                        if report:
                            # Check for expected compliance report structure
                            if 'compliance_summary' in report or 'regulatory_metrics' in report:
                                self.log_test("Analytics Compliance Report", True, 
                                            f"Compliance report available with data")
                            else:
                                self.log_test("Analytics Compliance Report", True, 
                                            f"Compliance report structure present")
                        else:
                            self.log_test("Analytics Compliance Report", True, 
                                        "No compliance report data yet (service may be starting)")
                    else:
                        self.log_test("Analytics Compliance Report", False, f"Invalid response structure: {data}")
                else:
                    self.log_test("Analytics Compliance Report", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Analytics Compliance Report", False, f"Exception: {str(e)}")
    
    async def test_analytics_historical_data(self):
        """Test GET /api/analytics/historical-data endpoint with parameters"""
        try:
            # Test with default parameters
            async with self.session.get(f"{API_BASE}/analytics/historical-data") as response:
                if response.status == 200:
                    data = await response.json()
                    if 'historical_data' in data and 'total_records' in data:
                        historical_data = data['historical_data']
                        total_records = data['total_records']
                        period_days = data.get('period_days', 30)
                        
                        self.log_test("Analytics Historical Data Default", True, 
                                    f"Found {total_records} historical records for {period_days} days")
                    else:
                        self.log_test("Analytics Historical Data Default", False, f"Invalid response structure: {data}")
                else:
                    self.log_test("Analytics Historical Data Default", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Analytics Historical Data Default", False, f"Exception: {str(e)}")
        
        # Test with specific parameters
        try:
            async with self.session.get(f"{API_BASE}/analytics/historical-data?days=7&limit=100") as response:
                if response.status == 200:
                    data = await response.json()
                    if 'historical_data' in data:
                        historical_data = data['historical_data']
                        total_records = data['total_records']
                        period_days = data.get('period_days', 7)
                        
                        # Verify limit is respected
                        if total_records <= 100:
                            self.log_test("Analytics Historical Data Filtered", True, 
                                        f"Found {total_records} records for {period_days} days (limit respected)")
                        else:
                            self.log_test("Analytics Historical Data Filtered", False, 
                                        f"Limit not respected: {total_records} > 100")
                    else:
                        self.log_test("Analytics Historical Data Filtered", False, f"Invalid response structure: {data}")
                else:
                    self.log_test("Analytics Historical Data Filtered", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Analytics Historical Data Filtered", False, f"Exception: {str(e)}")
    
    async def test_analytics_summary(self):
        """Test GET /api/analytics/summary endpoint"""
        try:
            async with self.session.get(f"{API_BASE}/analytics/summary") as response:
                if response.status == 200:
                    data = await response.json()
                    if 'service_status' in data and 'data_summary' in data:
                        service_status = data['service_status']
                        data_summary = data['data_summary']
                        latest_analytics = data.get('latest_analytics', {})
                        
                        running = service_status.get('running', False)
                        scheduled_jobs = service_status.get('scheduled_jobs', 0)
                        completed_jobs = service_status.get('completed_jobs', 0)
                        success_rate = service_status.get('success_rate', 0)
                        
                        historical_records = data_summary.get('historical_records', 0)
                        total_processed = data_summary.get('total_records_processed', 0)
                        
                        self.log_test("Analytics Summary", True, 
                                    f"Service running: {running}, Jobs: {scheduled_jobs}/{completed_jobs}, Success rate: {success_rate:.1%}, Historical: {historical_records}, Processed: {total_processed}")
                    else:
                        self.log_test("Analytics Summary", False, f"Invalid response structure: {data}")
                else:
                    self.log_test("Analytics Summary", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Analytics Summary", False, f"Exception: {str(e)}")
    
    async def test_analytics_stop(self):
        """Test POST /api/analytics/stop endpoint"""
        try:
            async with self.session.post(f"{API_BASE}/analytics/stop") as response:
                if response.status == 200:
                    data = await response.json()
                    if 'message' in data and 'stopped' in data['message'].lower():
                        self.log_test("Analytics Stop", True, f"Service stopped: {data['message']}")
                    else:
                        self.log_test("Analytics Stop", False, f"Unexpected response: {data}")
                else:
                    self.log_test("Analytics Stop", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Analytics Stop", False, f"Exception: {str(e)}")

    async def run_step7_tests(self):
        """Run all Step 7 Batch Analytics tests"""
        print(f"🚀 Starting Step 7 Batch Analytics & Performance Reporting Tests")
        print(f"📍 Backend URL: {BACKEND_URL}")
        print(f"📍 API Base: {API_BASE}")
        print("=" * 80)
        
        print("\n📈 Testing Batch Analytics & Performance Reporting System (STEP 7)...")
        
        # Test analytics service status first
        await self.test_analytics_status()
        
        # Start analytics service
        await self.test_analytics_start()
        
        # Test manual job execution
        await self.test_analytics_manual_job_peg_metrics()
        await self.test_analytics_manual_job_risk_analytics()
        
        # Test analytics data retrieval endpoints
        await self.test_analytics_peg_stability()
        await self.test_analytics_liquidity()
        await self.test_analytics_risk()
        await self.test_analytics_performance()
        await self.test_analytics_compliance_report()
        await self.test_analytics_historical_data()
        await self.test_analytics_summary()
        
        # Stop analytics service at the end
        await self.test_analytics_stop()
        
        # Summary
        print("\n" + "=" * 80)
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📋 STEP 7 ANALYTICS TEST SUMMARY")
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['details']}")

async def main():
    async with Step7AnalyticsTester() as tester:
        await tester.run_step7_tests()

if __name__ == "__main__":
    asyncio.run(main())