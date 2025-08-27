#!/usr/bin/env python3
"""
StableYield Yield Data Quality Test
Focus on unrealistic yield data issues
"""

import asyncio
import aiohttp
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://yield-analytics.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class YieldDataTester:
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
            print(f"    {details}")
        
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details
        })
    
    async def test_yields_realism(self):
        """Test GET /api/yields/ for unrealistic yield data"""
        print("\n🔍 Testing Yield Data Realism...")
        
        try:
            async with self.session.get(f"{API_BASE}/yields/") as response:
                if response.status == 200:
                    data = await response.json()
                    if isinstance(data, list) and len(data) > 0:
                        print(f"Found {len(data)} yield sources")
                        
                        unrealistic_yields = []
                        realistic_yields = []
                        
                        for yield_item in data:
                            coin = yield_item.get('stablecoin', 'Unknown')
                            yield_val = yield_item.get('currentYield', 0)
                            source = yield_item.get('source', 'Unknown')
                            protocol = yield_item.get('protocol', 'Unknown')
                            
                            print(f"  {coin}: {yield_val}% from {source} ({protocol})")
                            
                            # Flag unrealistic yields (>50% for stablecoins)
                            if yield_val > 50:
                                unrealistic_yields.append({
                                    'coin': coin,
                                    'yield': yield_val,
                                    'source': source,
                                    'protocol': protocol
                                })
                            elif yield_val > 15:
                                print(f"    ⚠️  HIGH: {yield_val}% is high for stablecoin")
                            else:
                                realistic_yields.append({
                                    'coin': coin,
                                    'yield': yield_val,
                                    'source': source
                                })
                        
                        if unrealistic_yields:
                            self.log_test("Yield Realism Check", False, 
                                        f"Found {len(unrealistic_yields)} unrealistic yields (>50%): " + 
                                        ", ".join([f"{y['coin']} {y['yield']}% ({y['protocol']})" for y in unrealistic_yields]))
                            
                            # Check specifically for Interest-Curve on Move chain
                            interest_curve_yields = [y for y in unrealistic_yields if 'Interest-Curve' in y.get('protocol', '') or 'Move' in y.get('protocol', '')]
                            if interest_curve_yields:
                                print(f"    🎯 FOUND ISSUE: Interest-Curve/Move yields: {interest_curve_yields}")
                        else:
                            self.log_test("Yield Realism Check", True, 
                                        f"All {len(data)} yields are realistic (<50%)")
                        
                        # Check for demo data patterns
                        demo_patterns = [
                            {'coin': 'USDT', 'yield': 8.45},
                            {'coin': 'USDC', 'yield': 7.12},
                            {'coin': 'TUSD', 'yield': 4.23}
                        ]
                        
                        demo_data_found = []
                        for pattern in demo_patterns:
                            for yield_item in data:
                                if (yield_item.get('stablecoin') == pattern['coin'] and 
                                    abs(yield_item.get('currentYield', 0) - pattern['yield']) < 0.01):
                                    demo_data_found.append(pattern)
                        
                        if demo_data_found:
                            self.log_test("Demo Data Check", False, 
                                        f"Found demo data patterns: {demo_data_found}")
                        else:
                            self.log_test("Demo Data Check", True, "No demo data patterns detected")
                            
                    else:
                        self.log_test("Yields API", False, f"Empty or invalid response: {data}")
                else:
                    self.log_test("Yields API", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Yields API", False, f"Exception: {str(e)}")
    
    async def test_risk_adjusted_yields(self):
        """Test GET /api/v1/strategies/risk-adjusted-yield endpoint"""
        print("\n🔍 Testing Risk-Adjusted Yields...")
        
        try:
            async with self.session.get(f"{API_BASE}/v1/strategies/risk-adjusted-yield") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"Risk-adjusted yields response: {json.dumps(data, indent=2)}")
                    
                    if 'strategies' in data or 'yields' in data:
                        self.log_test("Risk-Adjusted Yields API", True, "API responding with data")
                        
                        # Check for unrealistic risk-adjusted yields
                        yields_to_check = []
                        if 'strategies' in data:
                            for strategy in data['strategies']:
                                if 'yield' in strategy or 'apy' in strategy:
                                    yields_to_check.append(strategy.get('yield', strategy.get('apy', 0)))
                        elif 'yields' in data:
                            yields_to_check = data['yields']
                        
                        unrealistic_ray = [y for y in yields_to_check if isinstance(y, (int, float)) and y > 50]
                        if unrealistic_ray:
                            self.log_test("Risk-Adjusted Yield Realism", False, 
                                        f"Found unrealistic risk-adjusted yields: {unrealistic_ray}")
                        else:
                            self.log_test("Risk-Adjusted Yield Realism", True, 
                                        f"Risk-adjusted yields appear realistic")
                    else:
                        self.log_test("Risk-Adjusted Yields API", False, f"Unexpected response structure: {data}")
                elif response.status == 404:
                    self.log_test("Risk-Adjusted Yields API", False, "Endpoint not found (404)")
                else:
                    self.log_test("Risk-Adjusted Yields API", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Risk-Adjusted Yields API", False, f"Exception: {str(e)}")
    
    async def test_index_current(self):
        """Test GET /api/index/current for demo data"""
        print("\n🔍 Testing Index Current Data...")
        
        try:
            async with self.session.get(f"{API_BASE}/index/current") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"Index current response: {json.dumps(data, indent=2)}")
                    
                    # Check for demo data indicators
                    demo_indicators = [
                        'demo', 'test', 'mock', 'sample', 'placeholder'
                    ]
                    
                    data_str = json.dumps(data).lower()
                    found_demo_indicators = [indicator for indicator in demo_indicators if indicator in data_str]
                    
                    if found_demo_indicators:
                        self.log_test("Index Demo Data Check", False, 
                                    f"Found demo data indicators: {found_demo_indicators}")
                    else:
                        self.log_test("Index Demo Data Check", True, "No obvious demo data indicators")
                    
                    # Check index value realism
                    index_value = data.get('index_value', data.get('value', 0))
                    if index_value and isinstance(index_value, (int, float)):
                        if 0.5 <= index_value <= 2.0:  # Reasonable index range
                            self.log_test("Index Value Realism", True, f"Index value {index_value} appears realistic")
                        else:
                            self.log_test("Index Value Realism", False, f"Index value {index_value} may be unrealistic")
                    
                else:
                    self.log_test("Index Current API", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Index Current API", False, f"Exception: {str(e)}")
    
    async def test_index_constituents(self):
        """Test GET /api/index/constituents for demo vs real data"""
        print("\n🔍 Testing Index Constituents...")
        
        try:
            async with self.session.get(f"{API_BASE}/index/constituents") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"Index constituents response: {json.dumps(data, indent=2)}")
                    
                    constituents = data.get('constituents', data.get('data', []))
                    if isinstance(constituents, list) and len(constituents) > 0:
                        print(f"Found {len(constituents)} constituents")
                        
                        unrealistic_constituent_yields = []
                        for constituent in constituents:
                            yield_val = constituent.get('yield', constituent.get('apy', constituent.get('currentYield', 0)))
                            weight = constituent.get('weight', 0)
                            symbol = constituent.get('symbol', constituent.get('stablecoin', 'Unknown'))
                            
                            print(f"  {symbol}: {yield_val}% (weight: {weight})")
                            
                            if yield_val > 50:
                                unrealistic_constituent_yields.append({
                                    'symbol': symbol,
                                    'yield': yield_val,
                                    'weight': weight
                                })
                        
                        if unrealistic_constituent_yields:
                            self.log_test("Index Constituents Realism", False, 
                                        f"Found {len(unrealistic_constituent_yields)} unrealistic constituent yields: " +
                                        ", ".join([f"{c['symbol']} {c['yield']}%" for c in unrealistic_constituent_yields]))
                        else:
                            self.log_test("Index Constituents Realism", True, 
                                        f"All {len(constituents)} constituent yields appear realistic")
                        
                        # Check for demo data patterns in constituents
                        demo_symbols = ['TEST', 'DEMO', 'MOCK', 'SAMPLE']
                        found_demo_symbols = [c for c in constituents if any(demo in str(c.get('symbol', '')).upper() for demo in demo_symbols)]
                        
                        if found_demo_symbols:
                            self.log_test("Index Constituents Demo Check", False, 
                                        f"Found demo symbols: {[c.get('symbol') for c in found_demo_symbols]}")
                        else:
                            self.log_test("Index Constituents Demo Check", True, "No demo symbols detected")
                    
                    else:
                        self.log_test("Index Constituents API", False, f"No constituents found: {data}")
                else:
                    self.log_test("Index Constituents API", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Index Constituents API", False, f"Exception: {str(e)}")
    
    async def test_specific_protocols(self):
        """Test specific protocols mentioned in the issue"""
        print("\n🔍 Testing Specific Protocol Issues...")
        
        # Test Interest-Curve protocol specifically
        try:
            async with self.session.get(f"{API_BASE}/yields/") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    interest_curve_yields = []
                    move_chain_yields = []
                    
                    for yield_item in data:
                        protocol = yield_item.get('protocol', '')
                        chain = yield_item.get('chain', '')
                        metadata = yield_item.get('metadata', {})
                        
                        if 'Interest-Curve' in protocol or 'interest-curve' in protocol.lower():
                            interest_curve_yields.append(yield_item)
                        
                        if 'Move' in chain or 'move' in chain.lower():
                            move_chain_yields.append(yield_item)
                    
                    if interest_curve_yields:
                        print(f"Found {len(interest_curve_yields)} Interest-Curve yields:")
                        for yield_item in interest_curve_yields:
                            coin = yield_item.get('stablecoin')
                            yield_val = yield_item.get('currentYield')
                            chain = yield_item.get('chain', 'Unknown')
                            print(f"  {coin}: {yield_val}% on {chain}")
                            
                            if yield_val > 70:  # Specifically looking for 78-81% range
                                self.log_test("Interest-Curve Protocol Issue", False, 
                                            f"CONFIRMED ISSUE: {coin} showing {yield_val}% from Interest-Curve on {chain}")
                    
                    if move_chain_yields:
                        print(f"Found {len(move_chain_yields)} Move chain yields:")
                        for yield_item in move_chain_yields:
                            coin = yield_item.get('stablecoin')
                            yield_val = yield_item.get('currentYield')
                            protocol = yield_item.get('protocol', 'Unknown')
                            print(f"  {coin}: {yield_val}% from {protocol}")
                    
                    if not interest_curve_yields and not move_chain_yields:
                        self.log_test("Specific Protocol Check", True, "No Interest-Curve or Move chain yields found")
                        
        except Exception as e:
            self.log_test("Specific Protocol Check", False, f"Exception: {str(e)}")
    
    async def run_all_tests(self):
        """Run all yield data quality tests"""
        print("🚀 Starting StableYield Yield Data Quality Tests")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 60)
        
        await self.test_yields_realism()
        await self.test_risk_adjusted_yields()
        await self.test_index_current()
        await self.test_index_constituents()
        await self.test_specific_protocols()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total*100):.1f}%")
        
        print("\n🔍 FAILED TESTS:")
        for result in self.test_results:
            if not result['success']:
                print(f"❌ {result['test']}: {result['details']}")
        
        return self.test_results

async def main():
    async with YieldDataTester() as tester:
        await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())