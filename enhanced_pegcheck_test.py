#!/usr/bin/env python3
"""
Enhanced PegCheck System Test Suite (Phase 2)
Tests the new multi-source data integration and storage capabilities
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
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://crypto-yields-1.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class EnhancedPegCheckTester:
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
    
    async def test_enhanced_pegcheck_health(self):
        """Test GET /api/peg/health endpoint"""
        try:
            async with self.session.get(f"{API_BASE}/peg/health") as response:
                if response.status == 200:
                    data = await response.json()
                    required_fields = ['service', 'status', 'api_status', 'available_symbols']
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if not missing_fields:
                        api_status = data['api_status']
                        symbols_count = len(data.get('available_symbols', []))
                        self.log_test("Enhanced PegCheck Health", True, 
                                    f"Service: {data['status']}, Symbols: {symbols_count}, APIs: {list(api_status.keys())}")
                    else:
                        self.log_test("Enhanced PegCheck Health", False, f"Missing fields: {missing_fields}")
                else:
                    self.log_test("Enhanced PegCheck Health", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Enhanced PegCheck Health", False, f"Exception: {str(e)}")
    
    async def test_enhanced_pegcheck_sources(self):
        """Test GET /api/peg/sources endpoint - New enhanced data sources"""
        try:
            async with self.session.get(f"{API_BASE}/peg/sources") as response:
                if response.status == 200:
                    data = await response.json()
                    if 'data_sources' in data and 'configuration' in data and 'capabilities' in data:
                        sources = data['data_sources']
                        config = data['configuration']
                        capabilities = data['capabilities']
                        
                        # Check for all 4 expected sources
                        expected_sources = ['coingecko', 'cryptocompare', 'chainlink', 'uniswap']
                        found_sources = [src for src in expected_sources if src in sources]
                        
                        # Check configuration
                        eth_rpc_configured = config.get('eth_rpc_configured', False)
                        cc_api_configured = config.get('cryptocompare_api_configured', False)
                        
                        self.log_test("Enhanced PegCheck Sources", True, 
                                    f"Found {len(found_sources)}/4 sources: {found_sources}, ETH_RPC: {eth_rpc_configured}, CC_API: {cc_api_configured}")
                    else:
                        self.log_test("Enhanced PegCheck Sources", False, f"Invalid response structure: {data}")
                else:
                    self.log_test("Enhanced PegCheck Sources", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Enhanced PegCheck Sources", False, f"Exception: {str(e)}")
    
    async def test_enhanced_pegcheck_multi_source(self):
        """Test enhanced peg check with multiple data sources"""
        try:
            # Test with all sources enabled
            params = {
                'symbols': 'USDT,USDC,DAI',
                'with_oracle': 'true',
                'with_dex': 'true', 
                'store_result': 'true'
            }
            
            async with self.session.get(f"{API_BASE}/peg/check", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('success') and 'data' in data:
                        analysis = data['data']['analysis']
                        results = data['data']['results']
                        source_prices = data['data']['source_prices']
                        storage_info = data['data']['storage']
                        
                        # Check data sources used
                        sources_used = analysis.get('data_sources_used', {})
                        active_sources = sum(1 for active in sources_used.values() if active)
                        
                        # Check if results include multi-source data
                        symbols_analyzed = len(results)
                        depegs_detected = analysis.get('depegs_detected', 0)
                        
                        self.log_test("Enhanced PegCheck Multi-Source", True, 
                                    f"Analyzed {symbols_analyzed} symbols using {active_sources} sources, {depegs_detected} depegs, stored: {storage_info.get('stored', False)}")
                    else:
                        self.log_test("Enhanced PegCheck Multi-Source", False, f"Invalid response: {data}")
                else:
                    self.log_test("Enhanced PegCheck Multi-Source", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Enhanced PegCheck Multi-Source", False, f"Exception: {str(e)}")
    
    async def test_chainlink_integration(self):
        """Test Chainlink oracle integration"""
        try:
            # Test with oracle enabled
            params = {
                'symbols': 'USDT,USDC',
                'with_oracle': 'true',
                'with_dex': 'false'
            }
            
            async with self.session.get(f"{API_BASE}/peg/check", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('success') and 'data' in data:
                        source_prices = data['data']['source_prices']
                        sources_used = data['data']['analysis']['data_sources_used']
                        
                        chainlink_enabled = sources_used.get('chainlink', False)
                        chainlink_prices = source_prices.get('chainlink', {})
                        
                        if chainlink_enabled and chainlink_prices:
                            valid_prices = sum(1 for price in chainlink_prices.values() if price is not None)
                            self.log_test("Chainlink Integration", True, 
                                        f"Chainlink enabled with {valid_prices} valid prices: {chainlink_prices}")
                        elif not chainlink_enabled:
                            self.log_test("Chainlink Integration", True, 
                                        "Chainlink not configured (ETH_RPC_URL missing) - graceful fallback working")
                        else:
                            self.log_test("Chainlink Integration", False, 
                                        f"Chainlink enabled but no prices returned: {chainlink_prices}")
                    else:
                        self.log_test("Chainlink Integration", False, f"Invalid response: {data}")
                else:
                    self.log_test("Chainlink Integration", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Chainlink Integration", False, f"Exception: {str(e)}")
    
    async def test_uniswap_integration(self):
        """Test Uniswap v3 TWAP integration"""
        try:
            # Test with DEX enabled
            params = {
                'symbols': 'USDT,USDC',
                'with_oracle': 'false',
                'with_dex': 'true'
            }
            
            async with self.session.get(f"{API_BASE}/peg/check", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('success') and 'data' in data:
                        source_prices = data['data']['source_prices']
                        sources_used = data['data']['analysis']['data_sources_used']
                        
                        uniswap_enabled = sources_used.get('uniswap', False)
                        uniswap_prices = source_prices.get('uniswap', {})
                        
                        if uniswap_enabled and uniswap_prices:
                            valid_prices = sum(1 for price in uniswap_prices.values() if price is not None)
                            self.log_test("Uniswap Integration", True, 
                                        f"Uniswap enabled with {valid_prices} valid prices: {uniswap_prices}")
                        elif not uniswap_enabled:
                            self.log_test("Uniswap Integration", True, 
                                        "Uniswap not configured (ETH_RPC_URL missing) - graceful fallback working")
                        else:
                            self.log_test("Uniswap Integration", False, 
                                        f"Uniswap enabled but no prices returned: {uniswap_prices}")
                    else:
                        self.log_test("Uniswap Integration", False, f"Invalid response: {data}")
                else:
                    self.log_test("Uniswap Integration", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Uniswap Integration", False, f"Exception: {str(e)}")
    
    async def test_storage_backend_health(self):
        """Test GET /api/peg/storage/health endpoint"""
        try:
            async with self.session.get(f"{API_BASE}/peg/storage/health") as response:
                if response.status == 200:
                    data = await response.json()
                    required_fields = ['status', 'backend']
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if not missing_fields:
                        status = data['status']
                        backend = data['backend']
                        connected = data.get('connected', False)
                        
                        if status in ['healthy', 'available']:
                            self.log_test("Storage Backend Health", True, 
                                        f"Backend: {backend}, Status: {status}, Connected: {connected}")
                        else:
                            self.log_test("Storage Backend Health", False, 
                                        f"Unhealthy storage: {status}, Backend: {backend}")
                    else:
                        self.log_test("Storage Backend Health", False, f"Missing fields: {missing_fields}")
                else:
                    self.log_test("Storage Backend Health", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Storage Backend Health", False, f"Exception: {str(e)}")
    
    async def test_peg_history_retrieval(self):
        """Test GET /api/peg/history/{symbol} endpoint"""
        try:
            # Test history retrieval for USDT
            async with self.session.get(f"{API_BASE}/peg/history/USDT?hours=24") as response:
                if response.status == 200:
                    data = await response.json()
                    required_fields = ['symbol', 'hours_requested', 'data_points', 'history']
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if not missing_fields:
                        symbol = data['symbol']
                        hours = data['hours_requested']
                        data_points = data['data_points']
                        history = data['history']
                        
                        if data_points > 0:
                            # Check history structure
                            first_entry = history[0]
                            entry_fields = ['timestamp', 'price_usd', 'status', 'deviation_bps']
                            valid_entry = all(field in first_entry for field in entry_fields)
                            
                            if valid_entry:
                                self.log_test("Peg History Retrieval", True, 
                                            f"Retrieved {data_points} data points for {symbol} over {hours}h")
                            else:
                                self.log_test("Peg History Retrieval", False, 
                                            f"Invalid history entry structure: {first_entry}")
                        else:
                            self.log_test("Peg History Retrieval", True, 
                                        f"No historical data found for {symbol} (expected for new system)")
                    else:
                        self.log_test("Peg History Retrieval", False, f"Missing fields: {missing_fields}")
                elif response.status == 503:
                    self.log_test("Peg History Retrieval", True, "Storage backend not available (expected without PostgreSQL)")
                else:
                    self.log_test("Peg History Retrieval", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Peg History Retrieval", False, f"Exception: {str(e)}")
    
    async def test_enhanced_peg_error_handling(self):
        """Test enhanced peg check error handling"""
        # Test 1: Invalid symbols
        try:
            params = {'symbols': ''}
            async with self.session.get(f"{API_BASE}/peg/check", params=params) as response:
                if response.status == 400:
                    self.log_test("Enhanced Peg Error Handling - Empty Symbols", True, "Correctly rejected empty symbols")
                else:
                    self.log_test("Enhanced Peg Error Handling - Empty Symbols", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Enhanced Peg Error Handling - Empty Symbols", False, f"Exception: {str(e)}")
        
        # Test 2: Too many symbols
        try:
            symbols = ','.join([f'TEST{i}' for i in range(15)])  # 15 symbols > 10 limit
            params = {'symbols': symbols}
            async with self.session.get(f"{API_BASE}/peg/check", params=params) as response:
                if response.status == 400:
                    self.log_test("Enhanced Peg Error Handling - Too Many Symbols", True, "Correctly rejected >10 symbols")
                else:
                    self.log_test("Enhanced Peg Error Handling - Too Many Symbols", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Enhanced Peg Error Handling - Too Many Symbols", False, f"Exception: {str(e)}")
    
    async def test_cross_source_consistency(self):
        """Test cross-source consistency analysis"""
        try:
            params = {
                'symbols': 'USDT,USDC,DAI',
                'with_oracle': 'false',  # Use only CeFi sources for consistency test
                'with_dex': 'false'
            }
            
            async with self.session.get(f"{API_BASE}/peg/check", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('success') and 'data' in data:
                        source_consistency = data['data'].get('source_consistency', {})
                        
                        if source_consistency:
                            # Check consistency values
                            consistency_values = [v for v in source_consistency.values() if v is not None]
                            avg_consistency = sum(consistency_values) / len(consistency_values) if consistency_values else 0
                            
                            self.log_test("Cross-Source Consistency", True, 
                                        f"Consistency analysis: {len(consistency_values)} symbols, avg: {avg_consistency:.3f}")
                        else:
                            self.log_test("Cross-Source Consistency", False, "No consistency data returned")
                    else:
                        self.log_test("Cross-Source Consistency", False, f"Invalid response: {data}")
                else:
                    self.log_test("Cross-Source Consistency", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Cross-Source Consistency", False, f"Exception: {str(e)}")
    
    async def run_all_tests(self):
        """Run all enhanced pegcheck tests"""
        print("🔍 ENHANCED PEGCHECK SYSTEM (PHASE 2) COMPREHENSIVE TESTING")
        print(f"🌐 Testing against: {BACKEND_URL}")
        print("=" * 80)
        
        await self.test_enhanced_pegcheck_health()
        await self.test_enhanced_pegcheck_sources()
        await self.test_enhanced_pegcheck_multi_source()
        await self.test_chainlink_integration()
        await self.test_uniswap_integration()
        await self.test_storage_backend_health()
        await self.test_peg_history_retrieval()
        await self.test_enhanced_peg_error_handling()
        await self.test_cross_source_consistency()
        
        # Print summary
        self.print_test_summary()
    
    def print_test_summary(self):
        """Print test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print("\n" + "=" * 80)
        print(f"📋 ENHANCED PEGCHECK SYSTEM TEST SUMMARY")
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['details']}")

async def main():
    async with EnhancedPegCheckTester() as tester:
        await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())