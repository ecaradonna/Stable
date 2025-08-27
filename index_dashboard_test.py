#!/usr/bin/env python3
"""
StableYield Index Dashboard Backend Test Suite
Focus on testing Index Dashboard endpoints for SYI Macro Analysis
"""

import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment - use production URL for testing
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://stablecoin-yield-hub.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class IndexDashboardTester:
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
    
    async def test_index_current(self):
        """Test GET /api/index/current endpoint"""
        try:
            async with self.session.get(f"{API_BASE}/index/current") as response:
                if response.status == 200:
                    data = await response.json()
                    required_fields = ['value', 'timestamp', 'constituents']
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if not missing_fields:
                        value = data.get('value', 0)
                        constituents_count = len(data.get('constituents', []))
                        self.log_test("Index Current Data", True, 
                                    f"Index value: {value:.4f}, Constituents: {constituents_count}")
                    else:
                        self.log_test("Index Current Data", False, f"Missing fields: {missing_fields}")
                elif response.status == 404:
                    self.log_test("Index Current Data", False, "No index data available - scheduler may not be running")
                else:
                    self.log_test("Index Current Data", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Index Current Data", False, f"Exception: {str(e)}")
    
    async def test_index_constituents(self):
        """Test GET /api/index/constituents endpoint"""
        try:
            async with self.session.get(f"{API_BASE}/index/constituents") as response:
                if response.status == 200:
                    data = await response.json()
                    required_fields = ['index_value', 'timestamp', 'constituents', 'total_constituents']
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if not missing_fields:
                        constituents = data.get('constituents', [])
                        total = data.get('total_constituents', 0)
                        
                        # Check constituent structure
                        if constituents and len(constituents) > 0:
                            first_constituent = constituents[0]
                            constituent_fields = ['symbol', 'name', 'weight', 'raw_apy', 'ray']
                            missing_constituent_fields = [field for field in constituent_fields if field not in first_constituent]
                            
                            if not missing_constituent_fields:
                                self.log_test("Index Constituents", True, 
                                            f"Found {total} constituents with complete data")
                            else:
                                self.log_test("Index Constituents", False, 
                                            f"Constituent missing fields: {missing_constituent_fields}")
                        else:
                            self.log_test("Index Constituents", False, "No constituents data available")
                    else:
                        self.log_test("Index Constituents", False, f"Missing fields: {missing_fields}")
                elif response.status == 404:
                    self.log_test("Index Constituents", False, "No index data available")
                else:
                    self.log_test("Index Constituents", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Index Constituents", False, f"Exception: {str(e)}")
    
    async def test_index_statistics(self):
        """Test GET /api/index/statistics endpoint"""
        try:
            # Test with 7 days as requested in review
            async with self.session.get(f"{API_BASE}/index/statistics?days=7") as response:
                if response.status == 200:
                    data = await response.json()
                    # Statistics structure may vary, check for basic fields
                    if isinstance(data, dict) and len(data) > 0:
                        self.log_test("Index Statistics (7d)", True, 
                                    f"Statistics available with {len(data)} metrics")
                    else:
                        self.log_test("Index Statistics (7d)", False, f"Empty or invalid statistics: {data}")
                else:
                    self.log_test("Index Statistics (7d)", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Index Statistics (7d)", False, f"Exception: {str(e)}")
        
        # Test with 30 days default
        try:
            async with self.session.get(f"{API_BASE}/index/statistics") as response:
                if response.status == 200:
                    data = await response.json()
                    if isinstance(data, dict) and len(data) > 0:
                        self.log_test("Index Statistics (30d)", True, 
                                    f"Default statistics available")
                    else:
                        self.log_test("Index Statistics (30d)", False, f"Empty statistics")
                else:
                    self.log_test("Index Statistics (30d)", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Index Statistics (30d)", False, f"Exception: {str(e)}")
    
    async def test_index_history(self):
        """Test GET /api/index/history endpoint for macro analysis charts"""
        try:
            # Test different time periods for macro analysis
            time_periods = [7, 30, 90, 365]
            
            for days in time_periods:
                try:
                    # Calculate start date
                    start_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
                    
                    async with self.session.get(f"{API_BASE}/index/history?start_date={start_date}&limit=1000") as response:
                        if response.status == 200:
                            data = await response.json()
                            if isinstance(data, list):
                                self.log_test(f"Index History ({days}d)", True, 
                                            f"Retrieved {len(data)} historical data points")
                            else:
                                self.log_test(f"Index History ({days}d)", False, f"Invalid response format: {type(data)}")
                        else:
                            self.log_test(f"Index History ({days}d)", False, f"HTTP {response.status}")
                except Exception as e:
                    self.log_test(f"Index History ({days}d)", False, f"Exception: {str(e)}")
        except Exception as e:
            self.log_test("Index History", False, f"Exception: {str(e)}")
    
    async def test_index_live_ticker(self):
        """Test GET /api/index/live endpoint"""
        try:
            async with self.session.get(f"{API_BASE}/index/live") as response:
                if response.status == 200:
                    data = await response.json()
                    required_fields = ['value', 'timestamp', 'status', 'constituents_count']
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if not missing_fields:
                        value = data.get('value', 0)
                        status = data.get('status', 'unknown')
                        constituents = data.get('constituents_count', 0)
                        last_update = data.get('last_update_seconds', 0)
                        
                        self.log_test("Index Live Ticker", True, 
                                    f"Value: {value:.4f}, Status: {status}, Constituents: {constituents}, Last update: {last_update}s ago")
                    else:
                        self.log_test("Index Live Ticker", False, f"Missing fields: {missing_fields}")
                else:
                    self.log_test("Index Live Ticker", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Index Live Ticker", False, f"Exception: {str(e)}")
    
    async def test_syi_macro_analysis_data(self):
        """Test endpoints that support SYI Macro Analysis Chart (RPL, SSI, Treasury data)"""
        print("\n📊 Testing SYI Macro Analysis Data Endpoints...")
        
        # Test RAY (Risk-Adjusted Yield) endpoints for RPL data
        try:
            async with self.session.get(f"{API_BASE}/ray/syi/current") as response:
                if response.status == 200:
                    data = await response.json()
                    if 'syi_value' in data or 'risk_premium' in data:
                        self.log_test("SYI RAY Data (RPL)", True, 
                                    f"RAY data available for RPL calculations")
                    else:
                        self.log_test("SYI RAY Data (RPL)", False, f"No RAY/RPL data in response: {data}")
                else:
                    self.log_test("SYI RAY Data (RPL)", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("SYI RAY Data (RPL)", False, f"Exception: {str(e)}")
        
        # Test peg stability data for SSI (Stablecoin Stress Index)
        try:
            async with self.session.get(f"{API_BASE}/v1/peg-stability/ranking") as response:
                if response.status == 200:
                    data = await response.json()
                    if 'rankings' in data or 'stress_index' in data:
                        self.log_test("Peg Stability Data (SSI)", True, 
                                    f"Peg stability data available for SSI calculations")
                    else:
                        self.log_test("Peg Stability Data (SSI)", False, f"No peg stability data: {data}")
                else:
                    self.log_test("Peg Stability Data (SSI)", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Peg Stability Data (SSI)", False, f"Exception: {str(e)}")
        
        # Test market intelligence endpoints for treasury data
        try:
            async with self.session.get(f"{API_BASE}/v1/market-intelligence/summary") as response:
                if response.status == 200:
                    data = await response.json()
                    if 'treasury_rates' in data or 'risk_free_rate' in data:
                        self.log_test("Treasury Bills Data", True, 
                                    f"Treasury data available for macro analysis")
                    else:
                        self.log_test("Treasury Bills Data", False, f"No treasury data: {data}")
                else:
                    self.log_test("Treasury Bills Data", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Treasury Bills Data", False, f"Exception: {str(e)}")
    
    async def test_performance_metrics(self):
        """Test response times and performance"""
        print("\n⚡ Testing Performance Metrics...")
        
        # Test critical endpoints for response time
        endpoints_to_test = [
            ("/api/index/current", "Index Current"),
            ("/api/index/constituents", "Index Constituents"),
            ("/api/index/statistics?days=7", "Index Statistics"),
            ("/api/index/live", "Index Live Ticker"),
            ("/api/yields/", "Yields Data"),
            ("/api/health", "Health Check")
        ]
        
        for endpoint, name in endpoints_to_test:
            try:
                start_time = datetime.utcnow()
                async with self.session.get(f"{BACKEND_URL}{endpoint}") as response:
                    end_time = datetime.utcnow()
                    response_time = (end_time - start_time).total_seconds() * 1000  # ms
                    
                    if response.status == 200:
                        if response_time < 1000:  # Under 1 second
                            self.log_test(f"Performance {name}", True, 
                                        f"Response time: {response_time:.0f}ms")
                        else:
                            self.log_test(f"Performance {name}", False, 
                                        f"Slow response: {response_time:.0f}ms")
                    else:
                        self.log_test(f"Performance {name}", False, 
                                    f"HTTP {response.status} in {response_time:.0f}ms")
            except Exception as e:
                self.log_test(f"Performance {name}", False, f"Exception: {str(e)}")
    
    async def test_error_handling(self):
        """Test proper error responses and fallback behavior"""
        print("\n🛡️ Testing Error Handling...")
        
        # Test invalid index history parameters
        try:
            async with self.session.get(f"{API_BASE}/index/history?days=-1") as response:
                if response.status in [400, 422]:
                    self.log_test("Error Handling Invalid Days", True, 
                                f"Correctly rejected invalid days parameter")
                else:
                    self.log_test("Error Handling Invalid Days", False, 
                                f"Should reject invalid days but got HTTP {response.status}")
        except Exception as e:
            self.log_test("Error Handling Invalid Days", False, f"Exception: {str(e)}")
        
        # Test non-existent endpoints
        try:
            async with self.session.get(f"{API_BASE}/index/nonexistent") as response:
                if response.status == 404:
                    self.log_test("Error Handling 404", True, 
                                "Correctly returns 404 for non-existent endpoints")
                else:
                    self.log_test("Error Handling 404", False, 
                                f"Expected 404 but got HTTP {response.status}")
        except Exception as e:
            self.log_test("Error Handling 404", False, f"Exception: {str(e)}")
        
        # Test malformed requests
        try:
            async with self.session.get(f"{API_BASE}/index/statistics?days=invalid") as response:
                if response.status in [400, 422]:
                    self.log_test("Error Handling Malformed Request", True, 
                                "Correctly handles malformed parameters")
                else:
                    self.log_test("Error Handling Malformed Request", False, 
                                f"Should handle malformed params but got HTTP {response.status}")
        except Exception as e:
            self.log_test("Error Handling Malformed Request", False, f"Exception: {str(e)}")

    async def run_all_tests(self):
        """Run all Index Dashboard tests"""
        print("🚀 Starting StableYield Index Dashboard Backend Tests...")
        print(f"🔗 Testing backend: {BACKEND_URL}")
        print("=" * 80)
        
        # Core Index Dashboard Endpoints
        print("\n📊 CORE INDEX DASHBOARD ENDPOINTS")
        await self.test_index_current()
        await self.test_index_constituents()
        await self.test_index_statistics()
        await self.test_index_history()
        await self.test_index_live_ticker()
        
        # SYI Macro Analysis Data
        await self.test_syi_macro_analysis_data()
        
        # Performance Testing
        await self.test_performance_metrics()
        
        # Error Handling
        await self.test_error_handling()
        
        # Summary
        print("\n" + "=" * 80)
        print("📋 TEST SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"✅ Passed: {passed}/{total} ({success_rate:.1f}%)")
        
        if passed < total:
            print(f"❌ Failed: {total - passed}")
            print("\nFailed Tests:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['details']}")
        
        return success_rate >= 80  # Consider 80%+ success rate as passing

async def main():
    """Main test runner"""
    async with IndexDashboardTester() as tester:
        success = await tester.run_all_tests()
        return success

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)