#!/usr/bin/env python3
"""
Simple Trading Engine Test
Tests basic trading endpoints to verify Step 11 implementation
"""

import asyncio
import aiohttp
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://stableyield-trade.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

async def test_trading_endpoints():
    """Test key trading endpoints"""
    
    async with aiohttp.ClientSession() as session:
        print(f"🏦 Testing Trading Engine at: {API_BASE}")
        print("=" * 60)
        
        # Test 1: Health check
        try:
            async with session.get(f"{API_BASE}/health") as response:
                print(f"Health Check: HTTP {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"  Status: {data.get('status', 'unknown')}")
        except Exception as e:
            print(f"Health Check: ERROR - {e}")
        
        # Test 2: Trading Status
        try:
            async with session.get(f"{API_BASE}/trading/status") as response:
                print(f"Trading Status: HTTP {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"  Service Running: {data.get('service_running', False)}")
                    print(f"  Trading Pairs: {data.get('trading_pairs', 0)}")
                elif response.status == 503:
                    print("  Trading engine not started (expected)")
        except Exception as e:
            print(f"Trading Status: ERROR - {e}")
        
        # Test 3: Start Trading Engine
        try:
            async with session.post(f"{API_BASE}/trading/start") as response:
                print(f"Trading Start: HTTP {response.status}")
                if response.status == 200:
                    data = await response.json()
                    capabilities = data.get('capabilities', [])
                    print(f"  Started with {len(capabilities)} capabilities")
        except Exception as e:
            print(f"Trading Start: ERROR - {e}")
        
        # Test 4: Market Data
        try:
            async with session.get(f"{API_BASE}/trading/market-data") as response:
                print(f"Market Data: HTTP {response.status}")
                if response.status == 200:
                    data = await response.json()
                    symbols = data.get('symbols_count', 0)
                    print(f"  Market data for {symbols} symbols")
        except Exception as e:
            print(f"Market Data: ERROR - {e}")
        
        # Test 5: Trading Summary
        try:
            async with session.get(f"{API_BASE}/trading/summary") as response:
                print(f"Trading Summary: HTTP {response.status}")
                if response.status == 200:
                    data = await response.json()
                    status = data.get('service_status', 'unknown')
                    print(f"  Service Status: {status}")
        except Exception as e:
            print(f"Trading Summary: ERROR - {e}")

if __name__ == "__main__":
    asyncio.run(test_trading_endpoints())