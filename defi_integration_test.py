#!/usr/bin/env python3
"""
DeFi Integration Test Suite
Specifically tests DeFi yield data integration via DefiLlama
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
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE = f"{BACKEND_URL}/api"

class DeFiIntegrationTester:
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
    
    async def test_defi_yields_presence(self):
        """Test if GET /api/yields/ returns any DeFi yields (sourceType: 'DeFi')"""
        try:
            async with self.session.get(f"{API_BASE}/yields/") as response:
                if response.status == 200:
                    data = await response.json()
                    if isinstance(data, list) and len(data) > 0:
                        # Look for DeFi yields
                        defi_yields = [item for item in data if item.get('sourceType') == 'DeFi']
                        
                        if defi_yields:
                            defi_sources = [item.get('source') for item in defi_yields]
                            self.log_test("DeFi Yields Presence", True, 
                                        f"Found {len(defi_yields)} DeFi yields from sources: {', '.join(defi_sources)}")
                            return defi_yields
                        else:
                            self.log_test("DeFi Yields Presence", False, 
                                        f"No DeFi yields found. All {len(data)} yields are from other sources")
                            return []
                    else:
                        self.log_test("DeFi Yields Presence", False, f"Empty or invalid response: {data}")
                        return []
                else:
                    self.log_test("DeFi Yields Presence", False, f"HTTP {response.status}")
                    return []
        except Exception as e:
            self.log_test("DeFi Yields Presence", False, f"Exception: {str(e)}")
            return []
    
    async def test_defi_sources_in_individual_endpoints(self):
        """Check if individual stablecoin endpoints show DeFi sources like 'Aave', 'Compound', 'Curve'"""
        test_coins = ['USDT', 'USDC', 'DAI']
        defi_sources_found = []
        expected_defi_sources = ['Aave', 'Compound', 'Curve', 'Convex']
        
        for coin in test_coins:
            try:
                async with self.session.get(f"{API_BASE}/yields/{coin}") as response:
                    if response.status == 200:
                        data = await response.json()
                        source = data.get('source', '')
                        source_type = data.get('sourceType', '')
                        
                        if source_type == 'DeFi':
                            # Check if source is a known DeFi protocol
                            is_defi_protocol = any(protocol.lower() in source.lower() for protocol in expected_defi_sources)
                            if is_defi_protocol:
                                defi_sources_found.append(f"{coin}: {source}")
                                self.log_test(f"DeFi Source {coin}", True, 
                                            f"Found DeFi source: {source} (sourceType: {source_type})")
                            else:
                                self.log_test(f"DeFi Source {coin}", False, 
                                            f"Unknown DeFi source: {source} (sourceType: {source_type})")
                        else:
                            self.log_test(f"DeFi Source {coin}", False, 
                                        f"Not DeFi source: {source} (sourceType: {source_type})")
                    elif response.status == 404:
                        self.log_test(f"DeFi Source {coin}", False, f"Coin not found: {coin}")
                    else:
                        self.log_test(f"DeFi Source {coin}", False, f"HTTP {response.status}")
            except Exception as e:
                self.log_test(f"DeFi Source {coin}", False, f"Exception: {str(e)}")
        
        # Summary test
        if defi_sources_found:
            self.log_test("DeFi Sources Summary", True, 
                        f"Found {len(defi_sources_found)} DeFi sources: {', '.join(defi_sources_found)}")
        else:
            self.log_test("DeFi Sources Summary", False, "No DeFi sources found in individual endpoints")
    
    async def test_non_fallback_yield_values(self):
        """Look for yield values that are different from the fallback data"""
        fallback_values = {
            'USDT': 8.45,
            'USDC': 7.82, 
            'DAI': 6.95
        }
        
        real_data_found = []
        
        try:
            async with self.session.get(f"{API_BASE}/yields/") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    for item in data:
                        coin = item.get('stablecoin')
                        yield_val = item.get('currentYield')
                        source_type = item.get('sourceType')
                        
                        if coin in fallback_values:
                            expected_fallback = fallback_values[coin]
                            # Check if yield is significantly different from fallback (more than 0.1% difference)
                            if abs(yield_val - expected_fallback) > 0.1:
                                real_data_found.append(f"{coin}: {yield_val}% (expected fallback: {expected_fallback}%)")
                                self.log_test(f"Non-Fallback Data {coin}", True, 
                                            f"Real data - Yield: {yield_val}% vs fallback: {expected_fallback}% (sourceType: {source_type})")
                            else:
                                self.log_test(f"Non-Fallback Data {coin}", False, 
                                            f"Fallback data - Yield: {yield_val}% matches expected: {expected_fallback}% (sourceType: {source_type})")
                    
                    if real_data_found:
                        self.log_test("Real Data Summary", True, 
                                    f"Found {len(real_data_found)} coins with real data: {', '.join(real_data_found)}")
                    else:
                        self.log_test("Real Data Summary", False, 
                                    "All yield values match fallback data - no real API data detected")
                else:
                    self.log_test("Non-Fallback Data Check", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Non-Fallback Data Check", False, f"Exception: {str(e)}")
    
    async def test_defi_metadata_presence(self):
        """Test if the yields have realistic DeFi metadata like pool_id, chain, and TVL values"""
        try:
            async with self.session.get(f"{API_BASE}/yields/") as response:
                if response.status == 200:
                    data = await response.json()
                    defi_yields = [item for item in data if item.get('sourceType') == 'DeFi']
                    
                    metadata_found = []
                    
                    for item in defi_yields:
                        coin = item.get('stablecoin')
                        metadata = item.get('metadata', {})
                        
                        # Check for DeFi-specific metadata
                        has_pool_id = 'pool_id' in metadata
                        has_chain = 'chain' in metadata
                        has_tvl = 'tvl' in metadata
                        is_fallback = metadata.get('fallback', False)
                        
                        if has_pool_id and has_chain and has_tvl and not is_fallback:
                            metadata_found.append(f"{coin}: pool_id={metadata.get('pool_id')}, chain={metadata.get('chain')}, tvl=${metadata.get('tvl'):,.0f}")
                            self.log_test(f"DeFi Metadata {coin}", True, 
                                        f"Complete metadata - pool_id: {metadata.get('pool_id')}, chain: {metadata.get('chain')}, TVL: ${metadata.get('tvl'):,.0f}")
                        elif is_fallback:
                            self.log_test(f"DeFi Metadata {coin}", False, 
                                        f"Fallback data detected - metadata: {metadata}")
                        else:
                            missing_fields = []
                            if not has_pool_id: missing_fields.append('pool_id')
                            if not has_chain: missing_fields.append('chain')
                            if not has_tvl: missing_fields.append('tvl')
                            
                            self.log_test(f"DeFi Metadata {coin}", False, 
                                        f"Incomplete metadata - missing: {', '.join(missing_fields)}, available: {list(metadata.keys())}")
                    
                    if metadata_found:
                        self.log_test("DeFi Metadata Summary", True, 
                                    f"Found {len(metadata_found)} DeFi yields with complete metadata")
                    else:
                        self.log_test("DeFi Metadata Summary", False, 
                                    "No DeFi yields found with complete metadata (pool_id, chain, TVL)")
                else:
                    self.log_test("DeFi Metadata Check", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("DeFi Metadata Check", False, f"Exception: {str(e)}")
    
    async def test_specific_defi_protocols(self):
        """Verify if we can get stablecoin yields from actual DeFi protocols like Aave V3, Compound, Curve"""
        target_protocols = ['Aave', 'Compound', 'Curve']
        protocols_found = {}
        
        try:
            async with self.session.get(f"{API_BASE}/yields/") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    for item in data:
                        source = item.get('source', '')
                        source_type = item.get('sourceType', '')
                        coin = item.get('stablecoin')
                        yield_val = item.get('currentYield')
                        
                        if source_type == 'DeFi':
                            for protocol in target_protocols:
                                if protocol.lower() in source.lower():
                                    if protocol not in protocols_found:
                                        protocols_found[protocol] = []
                                    protocols_found[protocol].append(f"{coin}: {yield_val}% from {source}")
                    
                    # Test each protocol
                    for protocol in target_protocols:
                        if protocol in protocols_found:
                            yields_list = protocols_found[protocol]
                            self.log_test(f"Protocol {protocol}", True, 
                                        f"Found {len(yields_list)} yields: {', '.join(yields_list)}")
                        else:
                            self.log_test(f"Protocol {protocol}", False, 
                                        f"No yields found from {protocol}")
                    
                    if protocols_found:
                        total_protocols = len(protocols_found)
                        total_yields = sum(len(yields) for yields in protocols_found.values())
                        self.log_test("DeFi Protocols Summary", True, 
                                    f"Found {total_protocols} protocols with {total_yields} total yields: {list(protocols_found.keys())}")
                    else:
                        self.log_test("DeFi Protocols Summary", False, 
                                    f"No yields found from target DeFi protocols: {target_protocols}")
                else:
                    self.log_test("DeFi Protocols Check", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("DeFi Protocols Check", False, f"Exception: {str(e)}")
    
    async def test_yield_aggregator_combination(self):
        """Check the yield aggregator to see if it's successfully combining DeFi and CeFi data"""
        try:
            async with self.session.get(f"{API_BASE}/yields/stats/summary") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    cefi_count = data.get('cefi_count', 0)
                    defi_count = data.get('defi_count', 0)
                    total_stablecoins = data.get('total_stablecoins', 0)
                    
                    if cefi_count > 0 and defi_count > 0:
                        self.log_test("Yield Aggregator Combination", True, 
                                    f"Successfully combining data - CeFi: {cefi_count}, DeFi: {defi_count}, Total: {total_stablecoins}")
                    elif defi_count > 0:
                        self.log_test("Yield Aggregator Combination", True, 
                                    f"DeFi data available - DeFi: {defi_count}, CeFi: {cefi_count} (CeFi may be blocked)")
                    elif cefi_count > 0:
                        self.log_test("Yield Aggregator Combination", False, 
                                    f"Only CeFi data - CeFi: {cefi_count}, DeFi: {defi_count} (DeFi integration not working)")
                    else:
                        self.log_test("Yield Aggregator Combination", False, 
                                    f"No data from either source - CeFi: {cefi_count}, DeFi: {defi_count}")
                else:
                    self.log_test("Yield Aggregator Combination", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Yield Aggregator Combination", False, f"Exception: {str(e)}")
    
    async def test_defi_llama_direct_integration(self):
        """Test DefiLlama service directly by making a direct API call"""
        print("\n🦙 Testing DefiLlama Direct Integration...")
        
        try:
            # Test direct DefiLlama API call
            async with self.session.get("https://yields.llama.fi/pools") as response:
                if response.status == 200:
                    data = await response.json()
                    pools = data.get('data', [])
                    
                    if pools:
                        # Filter for stablecoin pools
                        stablecoin_pools = []
                        stablecoins = ["USDT", "USDC", "DAI", "PYUSD", "TUSD"]
                        
                        for pool in pools[:100]:  # Check first 100 pools
                            symbol = pool.get('symbol', '').upper()
                            project = pool.get('project', '').lower()
                            
                            for stablecoin in stablecoins:
                                if stablecoin in symbol:
                                    if any(platform in project for platform in ['aave', 'compound', 'curve', 'convex']):
                                        stablecoin_pools.append({
                                            'symbol': symbol,
                                            'project': project,
                                            'chain': pool.get('chain'),
                                            'apy': pool.get('apy', 0),
                                            'tvl': pool.get('tvlUsd', 0)
                                        })
                                    break
                        
                        if stablecoin_pools:
                            self.log_test("DefiLlama Direct API", True, 
                                        f"Found {len(stablecoin_pools)} stablecoin pools from major DeFi protocols")
                            
                            # Show some examples
                            for i, pool in enumerate(stablecoin_pools[:3]):
                                self.log_test(f"DefiLlama Pool Example {i+1}", True, 
                                            f"{pool['symbol']} on {pool['project']} ({pool['chain']}): {pool['apy']:.2f}% APY, ${pool['tvl']:,.0f} TVL")
                        else:
                            self.log_test("DefiLlama Direct API", False, 
                                        f"No stablecoin pools found from major DeFi protocols in first 100 pools")
                    else:
                        self.log_test("DefiLlama Direct API", False, "No pools data returned from DefiLlama")
                else:
                    self.log_test("DefiLlama Direct API", False, f"DefiLlama API returned HTTP {response.status}")
        except Exception as e:
            self.log_test("DefiLlama Direct API", False, f"Exception: {str(e)}")
    
    async def run_defi_tests(self):
        """Run all DeFi integration tests"""
        print(f"🦙 Starting DeFi Integration Tests")
        print(f"📍 Backend URL: {BACKEND_URL}")
        print(f"📍 API Base: {API_BASE}")
        print("=" * 60)
        
        # Test 1: Check for DeFi yields presence
        print("\n1️⃣ Testing DeFi Yields Presence...")
        defi_yields = await self.test_defi_yields_presence()
        
        # Test 2: Check individual endpoints for DeFi sources
        print("\n2️⃣ Testing DeFi Sources in Individual Endpoints...")
        await self.test_defi_sources_in_individual_endpoints()
        
        # Test 3: Check for non-fallback yield values
        print("\n3️⃣ Testing for Real vs Fallback Data...")
        await self.test_non_fallback_yield_values()
        
        # Test 4: Check DeFi metadata
        print("\n4️⃣ Testing DeFi Metadata Presence...")
        await self.test_defi_metadata_presence()
        
        # Test 5: Check specific DeFi protocols
        print("\n5️⃣ Testing Specific DeFi Protocols...")
        await self.test_specific_defi_protocols()
        
        # Test 6: Check yield aggregator combination
        print("\n6️⃣ Testing Yield Aggregator Combination...")
        await self.test_yield_aggregator_combination()
        
        # Test 7: Direct DefiLlama integration
        print("\n7️⃣ Testing DefiLlama Direct Integration...")
        await self.test_defi_llama_direct_integration()
        
        # Summary
        print("\n" + "=" * 60)
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"📋 DEFI INTEGRATION TEST SUMMARY")
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['details']}")
        
        # DeFi-specific analysis
        defi_related_tests = [r for r in self.test_results if 'defi' in r['test'].lower() or 'protocol' in r['test'].lower()]
        defi_passed = sum(1 for r in defi_related_tests if r['success'])
        
        print(f"\n🦙 DEFI INTEGRATION ANALYSIS:")
        print(f"DeFi-related tests: {len(defi_related_tests)}")
        print(f"DeFi tests passed: {defi_passed}")
        
        if defi_passed > 0:
            print("✅ DeFi integration is working to some degree")
        else:
            print("❌ DeFi integration appears to be non-functional")

async def main():
    """Main test runner"""
    async with DeFiIntegrationTester() as tester:
        await tester.run_defi_tests()

if __name__ == "__main__":
    asyncio.run(main())