#!/usr/bin/env python3
"""
Risk Regime Inversion Alert System Test Suite
Tests only the risk regime endpoints
"""

import asyncio
import aiohttp
import json
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://crypto-yields-1.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class RiskRegimeTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    Details: {details}")
        
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    async def test_regime_health_check(self):
        """Test GET /api/regime/health endpoint"""
        try:
            async with self.session.get(f"{API_BASE}/regime/health") as response:
                if response.status == 200:
                    data = await response.json()
                    required_fields = ['service', 'status', 'methodology_version', 'parameters']
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if not missing_fields:
                        service = data.get('service')
                        status = data.get('status')
                        version = data.get('methodology_version')
                        total_evals = data.get('total_evaluations', 0)
                        
                        if service == 'risk_regime' and status == 'healthy':
                            self.log_test("Risk Regime Health", True, 
                                        f"Service: {status}, Version: {version}, Evaluations: {total_evals}")
                        else:
                            self.log_test("Risk Regime Health", False, f"Invalid service response: {data}")
                    else:
                        self.log_test("Risk Regime Health", False, f"Missing fields: {missing_fields}")
                else:
                    self.log_test("Risk Regime Health", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Risk Regime Health", False, f"Exception: {str(e)}")
    
    async def test_regime_start_service(self):
        """Test POST /api/regime/start endpoint"""
        try:
            async with self.session.post(f"{API_BASE}/regime/start") as response:
                if response.status == 200:
                    data = await response.json()
                    required_fields = ['success', 'message', 'service', 'status', 'features']
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if not missing_fields and data.get('success'):
                        service = data.get('service')
                        status = data.get('status')
                        features = data.get('features', [])
                        
                        if service == 'risk_regime' and status == 'running':
                            self.log_test("Risk Regime Start", True, 
                                        f"Service started: {len(features)} features enabled")
                        else:
                            self.log_test("Risk Regime Start", False, f"Service not running: {data}")
                    else:
                        self.log_test("Risk Regime Start", False, f"Invalid response: {data}")
                else:
                    self.log_test("Risk Regime Start", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Risk Regime Start", False, f"Exception: {str(e)}")
    
    async def test_regime_parameters(self):
        """Test GET /api/regime/parameters endpoint"""
        try:
            async with self.session.get(f"{API_BASE}/regime/parameters") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('success') and 'parameters' in data:
                        params = data['parameters']
                        required_params = ['ema_short', 'ema_long', 'z_enter', 'persist_days', 'cooldown_days']
                        missing_params = [p for p in required_params if p not in params]
                        
                        if not missing_params:
                            ema_short = params['ema_short']
                            ema_long = params['ema_long']
                            z_enter = params['z_enter']
                            
                            self.log_test("Risk Regime Parameters", True, 
                                        f"EMA: {ema_short}/{ema_long}d, Z-threshold: {z_enter}")
                        else:
                            self.log_test("Risk Regime Parameters", False, f"Missing params: {missing_params}")
                    else:
                        self.log_test("Risk Regime Parameters", False, f"Invalid response: {data}")
                else:
                    self.log_test("Risk Regime Parameters", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Risk Regime Parameters", False, f"Exception: {str(e)}")
    
    async def test_regime_test_calculation(self):
        """Test POST /api/regime/test endpoint with sample data"""
        try:
            async with self.session.post(f"{API_BASE}/regime/test") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('success') and data.get('test_data'):
                        eval_result = data.get('evaluation_result', {})
                        if 'state' in eval_result and 'signal' in eval_result:
                            state = eval_result['state']
                            signal = eval_result['signal']
                            syi_excess = signal.get('syi_excess', 0)
                            z_score = signal.get('z_score', 0)
                            
                            self.log_test("Risk Regime Test Calculation", True, 
                                        f"State: {state}, SYI excess: {syi_excess:.4f}, Z-score: {z_score:.2f}")
                        else:
                            self.log_test("Risk Regime Test Calculation", False, f"Missing evaluation data: {eval_result}")
                    else:
                        self.log_test("Risk Regime Test Calculation", False, f"Test failed: {data}")
                else:
                    self.log_test("Risk Regime Test Calculation", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Risk Regime Test Calculation", False, f"Exception: {str(e)}")
    
    async def test_regime_evaluate_with_payload(self):
        """Test POST /api/regime/evaluate endpoint with sample payload"""
        try:
            # Sample payload from review request
            payload = {
                "date": "2025-08-28",
                "syi": 0.0445,
                "tbill_3m": 0.0530,
                "components": [
                    {"symbol": "USDT", "ray": 0.042},
                    {"symbol": "USDC", "ray": 0.045},
                    {"symbol": "DAI", "ray": 0.075},
                    {"symbol": "TUSD", "ray": 0.055},
                    {"symbol": "FRAX", "ray": 0.068}
                ],
                "peg_status": {"max_depeg_bps": 80, "agg_depeg_bps": 120}
            }
            
            async with self.session.post(f"{API_BASE}/regime/evaluate", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    required_fields = ['date', 'state', 'signal', 'methodology_version']
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if not missing_fields:
                        date = data['date']
                        state = data['state']
                        signal = data['signal']
                        alert = data.get('alert')
                        
                        # Validate signal structure
                        signal_fields = ['syi_excess', 'spread', 'z_score', 'slope7', 'breadth_pct']
                        missing_signal = [f for f in signal_fields if f not in signal]
                        
                        if not missing_signal:
                            syi_excess = signal['syi_excess']
                            z_score = signal['z_score']
                            breadth = signal['breadth_pct']
                            
                            alert_info = f", Alert: {alert['type']}" if alert else ""
                            self.log_test("Risk Regime Evaluate", True, 
                                        f"Date: {date}, State: {state}, SYI excess: {syi_excess:.4f}, Z-score: {z_score:.2f}, Breadth: {breadth:.1f}%{alert_info}")
                        else:
                            self.log_test("Risk Regime Evaluate", False, f"Missing signal fields: {missing_signal}")
                    else:
                        self.log_test("Risk Regime Evaluate", False, f"Missing fields: {missing_fields}")
                else:
                    self.log_test("Risk Regime Evaluate", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Risk Regime Evaluate", False, f"Exception: {str(e)}")
    
    async def test_regime_current_state(self):
        """Test GET /api/regime/current endpoint"""
        try:
            async with self.session.get(f"{API_BASE}/regime/current") as response:
                if response.status == 200:
                    data = await response.json()
                    if 'state' in data:
                        state = data.get('state')
                        syi_excess = data.get('syi_excess')
                        z_score = data.get('z_score')
                        
                        if state in ['ON', 'OFF', 'OFF_OVERRIDE', 'NEU']:
                            details = f"State: {state}"
                            if syi_excess is not None:
                                details += f", SYI excess: {syi_excess:.4f}"
                            if z_score is not None:
                                details += f", Z-score: {z_score:.2f}"
                            
                            self.log_test("Risk Regime Current", True, details)
                        else:
                            self.log_test("Risk Regime Current", False, f"Invalid state: {state}")
                    else:
                        self.log_test("Risk Regime Current", False, f"Missing state in response: {data}")
                else:
                    self.log_test("Risk Regime Current", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Risk Regime Current", False, f"Exception: {str(e)}")
    
    async def test_regime_summary(self):
        """Test GET /api/regime/summary endpoint"""
        try:
            async with self.session.get(f"{API_BASE}/regime/summary") as response:
                if response.status == 200:
                    data = await response.json()
                    required_fields = ['success', 'service_info', 'current_state', 'statistics', 'parameters']
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if not missing_fields and data.get('success'):
                        service_info = data['service_info']
                        current_state = data['current_state']
                        statistics = data['statistics']
                        
                        # Validate service info
                        if 'status' in service_info and 'methodology_version' in service_info:
                            status = service_info['status']
                            version = service_info['methodology_version']
                            total_evals = service_info.get('total_evaluations', 0)
                            
                            # Validate statistics
                            if 'total_days' in statistics and 'total_flips' in statistics:
                                total_days = statistics['total_days']
                                total_flips = statistics['total_flips']
                                
                                self.log_test("Risk Regime Summary", True, 
                                            f"Status: {status}, Version: {version}, Evaluations: {total_evals}, Days: {total_days}, Flips: {total_flips}")
                            else:
                                self.log_test("Risk Regime Summary", False, f"Missing statistics fields: {statistics}")
                        else:
                            self.log_test("Risk Regime Summary", False, f"Missing service info fields: {service_info}")
                    else:
                        self.log_test("Risk Regime Summary", False, f"Invalid response: {data}")
                else:
                    self.log_test("Risk Regime Summary", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Risk Regime Summary", False, f"Exception: {str(e)}")
    
    async def run_all_tests(self):
        """Run all risk regime tests"""
        print(f"🚀 Starting Risk Regime Inversion Alert System Tests")
        print(f"📍 Backend URL: {BACKEND_URL}")
        print(f"📍 API Base: {API_BASE}")
        print("=" * 60)
        
        # Risk Regime tests
        print("\n⚠️ Testing Risk Regime Inversion Alert System...")
        await self.test_regime_health_check()
        await self.test_regime_start_service()
        await self.test_regime_parameters()
        await self.test_regime_test_calculation()
        await self.test_regime_evaluate_with_payload()
        await self.test_regime_current_state()
        await self.test_regime_summary()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📋 TEST SUMMARY")
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
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
    async with RiskRegimeTester() as tester:
        await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())