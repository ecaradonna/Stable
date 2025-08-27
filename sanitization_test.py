#!/usr/bin/env python3
"""
Test yield sanitization directly to understand why unrealistic yields are passing through
"""

import asyncio
import aiohttp
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://stablecoin-yield-hub.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class SanitizationTester:
    def __init__(self):
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_sanitization_config(self):
        """Test sanitization configuration"""
        print("🔧 Testing Sanitization Configuration...")
        
        try:
            async with self.session.get(f"{API_BASE}/sanitization/summary") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"Sanitization Config: {json.dumps(data, indent=2)}")
                    
                    config = data.get('config', {})
                    apy_bounds = config.get('apy_bounds', {})
                    
                    print(f"\n📊 APY Bounds Configuration:")
                    print(f"  Reasonable Maximum: {apy_bounds.get('reasonable_maximum', 'N/A')}%")
                    print(f"  Suspicious Threshold: {apy_bounds.get('suspicious_threshold', 'N/A')}%")
                    print(f"  Absolute Maximum: {apy_bounds.get('absolute_maximum', 'N/A')}%")
                    
                    # Check if 78-81% should be flagged
                    reasonable_max = apy_bounds.get('reasonable_maximum', 50)
                    if 78 > reasonable_max:
                        print(f"  ✅ 78% SHOULD be flagged (> {reasonable_max}%)")
                    else:
                        print(f"  ❌ 78% would NOT be flagged (< {reasonable_max}%)")
                        
                else:
                    print(f"❌ Sanitization config API failed: HTTP {response.status}")
        except Exception as e:
            print(f"❌ Exception testing sanitization config: {str(e)}")
    
    async def test_sanitization_direct(self):
        """Test sanitization with high APY values directly"""
        print("\n🧪 Testing Direct Sanitization...")
        
        test_cases = [
            {"apy": 78.5, "description": "USDT Interest-Curve yield"},
            {"apy": 81.2, "description": "USDC Interest-Curve yield"},
            {"apy": 150.0, "description": "Extreme test case"},
            {"apy": 8.5, "description": "Normal yield"}
        ]
        
        for test_case in test_cases:
            try:
                payload = {
                    "apy": test_case["apy"],
                    "source": "Interest-Curve",
                    "stablecoin": "USDT"
                }
                
                async with self.session.post(f"{API_BASE}/sanitization/test", json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        result = data.get('sanitization_result', {})
                        
                        original = result.get('original_apy', test_case["apy"])
                        sanitized = result.get('sanitized_apy', test_case["apy"])
                        action = result.get('action_taken', 'unknown')
                        confidence = result.get('confidence_score', 0)
                        warnings = result.get('warnings', [])
                        
                        print(f"\n  {test_case['description']} ({original}%):")
                        print(f"    Action: {action}")
                        print(f"    Sanitized: {sanitized}%")
                        print(f"    Confidence: {confidence:.2f}")
                        if warnings:
                            print(f"    Warnings: {warnings}")
                        
                        # Check if high yields are being properly handled
                        if original > 50 and action == 'accept':
                            print(f"    ⚠️  HIGH YIELD NOT SANITIZED!")
                        elif original > 50 and action in ['flag', 'cap', 'winsorize', 'reject']:
                            print(f"    ✅ High yield properly handled")
                            
                    else:
                        print(f"    ❌ Test failed: HTTP {response.status}")
                        
            except Exception as e:
                print(f"    ❌ Exception: {str(e)}")
    
    async def test_yield_pipeline(self):
        """Test the full yield pipeline to see where sanitization fails"""
        print("\n🔄 Testing Full Yield Pipeline...")
        
        try:
            # Get raw yields
            async with self.session.get(f"{API_BASE}/yields/?refresh=true") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    print(f"Found {len(data)} yields in pipeline:")
                    for yield_item in data:
                        coin = yield_item.get('stablecoin')
                        yield_val = yield_item.get('currentYield')
                        source = yield_item.get('source')
                        metadata = yield_item.get('metadata', {})
                        
                        print(f"\n  {coin}: {yield_val}% from {source}")
                        
                        # Check for sanitization metadata
                        sanitization = metadata.get('sanitization', {})
                        if sanitization:
                            print(f"    Sanitization applied:")
                            print(f"      Original: {sanitization.get('original_apy')}%")
                            print(f"      Sanitized: {sanitization.get('sanitized_apy')}%")
                            print(f"      Action: {sanitization.get('action_taken')}")
                            print(f"      Confidence: {sanitization.get('confidence_score')}")
                            if sanitization.get('warnings'):
                                print(f"      Warnings: {sanitization.get('warnings')}")
                        else:
                            print(f"    ❌ NO SANITIZATION METADATA FOUND")
                            
                        # Check if this is an unrealistic yield
                        if yield_val > 50:
                            if not sanitization:
                                print(f"    🚨 UNREALISTIC YIELD ({yield_val}%) WITH NO SANITIZATION!")
                            elif sanitization.get('action_taken') == 'accept':
                                print(f"    🚨 UNREALISTIC YIELD ({yield_val}%) ACCEPTED BY SANITIZER!")
                                
                else:
                    print(f"❌ Yields API failed: HTTP {response.status}")
                    
        except Exception as e:
            print(f"❌ Exception testing yield pipeline: {str(e)}")
    
    async def test_sanitization_stats(self):
        """Test sanitization statistics"""
        print("\n📈 Testing Sanitization Statistics...")
        
        try:
            async with self.session.get(f"{API_BASE}/sanitization/stats") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"Sanitization Stats: {json.dumps(data, indent=2)}")
                    
                    # Check processing statistics
                    processed = data.get('yields_processed', 0)
                    flagged = data.get('flagged_yields', 0)
                    rejected = data.get('rejected_yields', 0)
                    
                    print(f"\n📊 Processing Summary:")
                    print(f"  Yields Processed: {processed}")
                    print(f"  Flagged: {flagged}")
                    print(f"  Rejected: {rejected}")
                    
                    if processed > 0:
                        flag_rate = (flagged / processed) * 100
                        reject_rate = (rejected / processed) * 100
                        print(f"  Flag Rate: {flag_rate:.1f}%")
                        print(f"  Reject Rate: {reject_rate:.1f}%")
                        
                        if flag_rate == 0 and reject_rate == 0:
                            print(f"  ⚠️  NO YIELDS FLAGGED OR REJECTED - SANITIZATION MAY NOT BE WORKING")
                    
                else:
                    print(f"❌ Sanitization stats API failed: HTTP {response.status}")
                    
        except Exception as e:
            print(f"❌ Exception testing sanitization stats: {str(e)}")
    
    async def run_all_tests(self):
        """Run all sanitization tests"""
        print("🧪 Starting Yield Sanitization Analysis")
        print("=" * 60)
        
        await self.test_sanitization_config()
        await self.test_sanitization_direct()
        await self.test_yield_pipeline()
        await self.test_sanitization_stats()
        
        print("\n" + "=" * 60)
        print("🎯 ANALYSIS COMPLETE")
        print("=" * 60)

async def main():
    async with SanitizationTester() as tester:
        await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())