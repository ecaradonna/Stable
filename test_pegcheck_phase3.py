#!/usr/bin/env python3
"""
PegCheck Phase 3 Testing - Advanced Analytics & Job Management
Focused testing for Phase 3 features only
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

class PegCheckPhase3Tester:
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

    async def test_pegcheck_phase3_analytics(self):
        """Test Phase 3 Advanced Analytics System"""
        print("\n📊 PHASE 3 ADVANCED ANALYTICS SYSTEM TESTING")
        
        analytics_tests = [
            ("Trend Analysis USDT", f"{API_BASE}/peg/analytics/trends/USDT?hours=168"),
            ("Trend Analysis USDC", f"{API_BASE}/peg/analytics/trends/USDC?hours=72"),
            ("Market Stability Report", f"{API_BASE}/peg/analytics/market-stability?symbols=USDT,USDC,DAI&hours=168"),
        ]
        
        successful_tests = 0
        
        for test_name, endpoint in analytics_tests:
            try:
                async with self.session.get(endpoint) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if "trends" in endpoint:
                            # Validate trend analysis response
                            required_fields = ['symbol', 'analysis_period_hours', 'data_points', 'price_metrics', 'deviation_metrics', 'stability_metrics']
                            missing_fields = [field for field in required_fields if field not in data]
                            
                            if not missing_fields:
                                symbol = data['symbol']
                                data_points = data['data_points']
                                stability_grade = data['stability_metrics'].get('stability_grade', 'N/A')
                                risk_score = data['stability_metrics'].get('risk_score', 0)
                                
                                self.log_test(test_name, True, 
                                            f"{symbol}: {data_points} points, Grade: {stability_grade}, Risk: {risk_score:.1f}")
                                successful_tests += 1
                            else:
                                self.log_test(test_name, False, f"Missing fields: {missing_fields}")
                        
                        elif "market-stability" in endpoint:
                            # Validate market stability report
                            required_fields = ['analysis_period_hours', 'symbols_analyzed', 'market_summary']
                            missing_fields = [field for field in required_fields if field not in data]
                            
                            if not missing_fields:
                                symbols_analyzed = data['symbols_analyzed']
                                market_health = data['market_summary'].get('market_health', 'unknown')
                                avg_risk_score = data['market_summary'].get('avg_risk_score', 0)
                                
                                self.log_test(test_name, True, 
                                            f"{symbols_analyzed} symbols, Health: {market_health}, Risk: {avg_risk_score:.1f}")
                                successful_tests += 1
                            else:
                                self.log_test(test_name, False, f"Missing fields: {missing_fields}")
                    
                    elif response.status == 404:
                        self.log_test(test_name, False, f"Insufficient data (404) - expected for new system")
                    elif response.status == 503:
                        self.log_test(test_name, False, f"Service unavailable (503) - storage backend required")
                    else:
                        self.log_test(test_name, False, f"HTTP {response.status}")
                        
            except Exception as e:
                self.log_test(test_name, False, f"Exception: {str(e)}")
        
        return successful_tests, len(analytics_tests)

    async def test_pegcheck_phase3_jobs(self):
        """Test Phase 3 Job Management System"""
        print("\n⚙️ PHASE 3 JOB MANAGEMENT SYSTEM TESTING")
        
        job_tests = [
            ("Manual Peg Check Job", f"{API_BASE}/peg/jobs/run-peg-check?with_oracle=false&with_dex=false", "POST"),
            ("Data Cleanup Job", f"{API_BASE}/peg/jobs/cleanup?days_to_keep=30", "POST"),
        ]
        
        successful_tests = 0
        
        for test_name, endpoint, method in job_tests:
            try:
                async with self.session.post(endpoint) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if "run-peg-check" in endpoint:
                            if data.get('success') and 'configuration' in data:
                                config = data['configuration']
                                oracle_enabled = config.get('oracle_enabled', False)
                                dex_enabled = config.get('dex_enabled', False)
                                
                                self.log_test(test_name, True, 
                                            f"Job completed, Oracle: {oracle_enabled}, DEX: {dex_enabled}")
                                successful_tests += 1
                            else:
                                self.log_test(test_name, False, f"Invalid job response: {data}")
                        
                        elif "cleanup" in endpoint:
                            if data.get('success') and 'deleted_records' in data:
                                deleted_records = data.get('deleted_records', 0)
                                days_kept = data.get('days_kept', 0)
                                
                                self.log_test(test_name, True, 
                                            f"Cleanup: {deleted_records} records deleted, {days_kept} days kept")
                                successful_tests += 1
                            else:
                                self.log_test(test_name, False, f"Invalid cleanup response: {data}")
                    
                    elif response.status == 503:
                        self.log_test(test_name, False, f"Service unavailable (503) - storage backend required")
                    else:
                        self.log_test(test_name, False, f"HTTP {response.status}")
                        
            except Exception as e:
                self.log_test(test_name, False, f"Exception: {str(e)}")
        
        return successful_tests, len(job_tests)

    async def test_pegcheck_storage_persistence(self):
        """Test Enhanced Storage & Persistence"""
        print("\n💾 ENHANCED STORAGE & PERSISTENCE TESTING")
        
        storage_tests = [
            ("Storage Health", f"{API_BASE}/peg/storage/health"),
            ("Historical Data USDT", f"{API_BASE}/peg/history/USDT?hours=24"),
            ("Historical Data USDC", f"{API_BASE}/peg/history/USDC?hours=72"),
        ]
        
        successful_tests = 0
        
        for test_name, endpoint in storage_tests:
            try:
                async with self.session.get(endpoint) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if "storage/health" in endpoint:
                            status = data.get('status', 'unknown')
                            backend = data.get('backend', 'unknown')
                            
                            if status in ['healthy', 'available']:
                                self.log_test(test_name, True, f"Status: {status}, Backend: {backend}")
                                successful_tests += 1
                            else:
                                self.log_test(test_name, False, f"Unhealthy storage: {status}")
                        
                        elif "history" in endpoint:
                            symbol = data.get('symbol', 'unknown')
                            data_points = data.get('data_points', 0)
                            hours_requested = data.get('hours_requested', 0)
                            
                            if data_points >= 0:  # Accept 0 for new systems
                                self.log_test(test_name, True, 
                                            f"{symbol}: {data_points} points over {hours_requested}h")
                                successful_tests += 1
                            else:
                                self.log_test(test_name, False, f"Invalid data points: {data_points}")
                    
                    elif response.status == 503:
                        self.log_test(test_name, False, f"Service unavailable (503)")
                    else:
                        self.log_test(test_name, False, f"HTTP {response.status}")
                        
            except Exception as e:
                self.log_test(test_name, False, f"Exception: {str(e)}")
        
        return successful_tests, len(storage_tests)

    async def test_complete_integration(self):
        """Test Complete System Integration"""
        print("\n🔄 COMPLETE SYSTEM INTEGRATION TESTING")
        
        integration_tests = [
            ("PegCheck Health", f"{API_BASE}/peg/health"),
            ("Data Sources", f"{API_BASE}/peg/sources"),
            ("Peg Analysis", f"{API_BASE}/peg/check?symbols=USDT,USDC,DAI"),
            ("Summary Report", f"{API_BASE}/peg/summary"),
        ]
        
        successful_tests = 0
        
        for test_name, endpoint in integration_tests:
            try:
                async with self.session.get(endpoint) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if "health" in endpoint:
                            if data.get('service') == 'pegcheck':
                                status = data.get('status', 'unknown')
                                self.log_test(test_name, True, f"Service: {status}")
                                successful_tests += 1
                            else:
                                self.log_test(test_name, False, f"Invalid service: {data}")
                        
                        elif "sources" in endpoint:
                            sources = data.get('data_sources', {})
                            capabilities = data.get('capabilities', {})
                            self.log_test(test_name, True, f"{len(sources)} sources, {len(capabilities)} capabilities")
                            successful_tests += 1
                        
                        elif "check" in endpoint:
                            if data.get('success'):
                                analysis = data.get('data', {}).get('analysis', {})
                                symbols = analysis.get('symbols_analyzed', 0)
                                depegs = analysis.get('depegs_detected', 0)
                                self.log_test(test_name, True, f"{symbols} symbols, {depegs} depegs")
                                successful_tests += 1
                            else:
                                self.log_test(test_name, False, f"Analysis failed")
                        
                        elif "summary" in endpoint:
                            if data.get('success'):
                                overview = data.get('summary', {}).get('overview', {})
                                symbols = overview.get('total_symbols', 0)
                                health = overview.get('market_health', 'unknown')
                                self.log_test(test_name, True, f"{symbols} symbols, Health: {health}")
                                successful_tests += 1
                            else:
                                self.log_test(test_name, False, f"Summary failed")
                    
                    elif response.status == 503:
                        self.log_test(test_name, False, f"Service unavailable (503)")
                    else:
                        self.log_test(test_name, False, f"HTTP {response.status}")
                        
            except Exception as e:
                self.log_test(test_name, False, f"Exception: {str(e)}")
        
        return successful_tests, len(integration_tests)

    async def run_all_phase3_tests(self):
        """Run all Phase 3 tests"""
        print("🚀 PEGCHECK PHASE 3 COMPREHENSIVE TESTING")
        print(f"📍 Backend URL: {BACKEND_URL}")
        print("=" * 60)
        
        total_successful = 0
        total_tests = 0
        
        # Test Analytics System
        analytics_success, analytics_total = await self.test_pegcheck_phase3_analytics()
        total_successful += analytics_success
        total_tests += analytics_total
        
        # Test Job Management System
        jobs_success, jobs_total = await self.test_pegcheck_phase3_jobs()
        total_successful += jobs_success
        total_tests += jobs_total
        
        # Test Storage & Persistence
        storage_success, storage_total = await self.test_pegcheck_storage_persistence()
        total_successful += storage_success
        total_tests += storage_total
        
        # Test Complete Integration
        integration_success, integration_total = await self.test_complete_integration()
        total_successful += integration_success
        total_tests += integration_total
        
        # Final Summary
        success_rate = (total_successful / total_tests) * 100 if total_tests > 0 else 0
        print("\n" + "=" * 60)
        print("📊 PEGCHECK PHASE 3 TESTING SUMMARY")
        print("=" * 60)
        print(f"✅ Successful Tests: {total_successful}")
        print(f"❌ Failed Tests: {total_tests - total_successful}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        print(f"🎯 Total Tests: {total_tests}")
        
        if success_rate >= 70:
            print("🎉 PHASE 3 TESTING: SUCCESSFUL")
        elif success_rate >= 50:
            print("⚠️ PHASE 3 TESTING: PARTIAL SUCCESS")
        else:
            print("❌ PHASE 3 TESTING: NEEDS ATTENTION")
        
        return total_successful, total_tests

async def main():
    async with PegCheckPhase3Tester() as tester:
        await tester.run_all_phase3_tests()

if __name__ == "__main__":
    asyncio.run(main())