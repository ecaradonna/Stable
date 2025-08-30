"""
Chainlink Price Feeds integration for stablecoin price data
"""

import time
import requests
from typing import Dict, List, Optional, Tuple
from decimal import Decimal, getcontext

from ..core.models import PricePoint
from ..core.config import CHAINLINK_FEEDS, ETH_RPC_URL, REQUEST_TIMEOUT

# Set decimal precision for accurate price calculations
getcontext().prec = 18

# Chainlink AggregatorV3Interface ABI (minimal)
AGGREGATOR_ABI = [
    {
        "inputs": [],
        "name": "latestRoundData",
        "outputs": [
            {"internalType": "uint80", "name": "roundId", "type": "uint80"},
            {"internalType": "int256", "name": "answer", "type": "int256"},
            {"internalType": "uint256", "name": "startedAt", "type": "uint256"},
            {"internalType": "uint256", "name": "updatedAt", "type": "uint256"},
            {"internalType": "uint80", "name": "answeredInRound", "type": "uint80"}
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "decimals",
        "outputs": [{"internalType": "uint8", "name": "", "type": "uint8"}],
        "stateMutability": "view",
        "type": "function"
    }
]

def _make_eth_rpc_call(method: str, params: List) -> Optional[Dict]:
    """Make an Ethereum RPC call"""
    if not ETH_RPC_URL:
        print("ETH_RPC_URL not configured, cannot fetch Chainlink data")
        return None
        
    try:
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": 1
        }
        
        response = requests.post(ETH_RPC_URL, json=payload, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        
        if "result" in data:
            return data["result"]
        elif "error" in data:
            print(f"RPC error: {data['error']}")
            return None
            
    except Exception as e:
        print(f"RPC call error: {e}")
        return None
    
    return None

def _encode_function_call(function_name: str) -> str:
    """Encode function call for eth_call"""
    # Simple function signature hashing (first 4 bytes of keccak256)
    if function_name == "latestRoundData()":
        return "0xfeaf968c"  # latestRoundData() signature
    elif function_name == "decimals()":
        return "0x313ce567"  # decimals() signature
    return "0x"

def _decode_uint256(hex_data: str) -> int:
    """Decode uint256 from hex string"""
    if hex_data.startswith("0x"):
        hex_data = hex_data[2:]
    return int(hex_data, 16)

def _decode_int256(hex_data: str) -> int:
    """Decode int256 from hex string"""
    if hex_data.startswith("0x"):
        hex_data = hex_data[2:]
    
    value = int(hex_data, 16)
    
    # Handle signed integers (2's complement for negative values)
    if value >= 2**255:
        value -= 2**256
    
    return value

def _fetch_price_feed_data(feed_address: str) -> Optional[Tuple[float, int]]:
    """Fetch latest price data from a Chainlink price feed"""
    try:
        # Get decimals first
        decimals_call_data = _encode_function_call("decimals()")
        decimals_result = _make_eth_rpc_call("eth_call", [
            {"to": feed_address, "data": decimals_call_data},
            "latest"
        ])
        
        if not decimals_result:
            return None
            
        decimals = _decode_uint256(decimals_result)
        
        # Get latest round data
        latest_round_call_data = _encode_function_call("latestRoundData()")
        result = _make_eth_rpc_call("eth_call", [
            {"to": feed_address, "data": latest_round_call_data},
            "latest"
        ])
        
        if not result or result == "0x":
            return None
        
        # Decode the result (5 return values, each 32 bytes)
        if len(result) < 322:  # 2 + 5*64 = 322 characters minimum
            return None
            
        # Extract the answer (second return value, bytes 32-63)
        answer_hex = result[66:130]  # Skip 0x and first 64 chars
        answer = _decode_int256("0x" + answer_hex)
        
        # Extract updated timestamp (fourth return value, bytes 96-127)
        timestamp_hex = result[194:258]
        timestamp = _decode_uint256("0x" + timestamp_hex)
        
        if answer <= 0:
            return None
            
        # Convert to float with proper decimal places
        price = float(answer) / (10 ** decimals)
        
        return price, timestamp
        
    except Exception as e:
        print(f"Error fetching Chainlink price feed {feed_address}: {e}")
        return None

def fetch(symbols: List[str]) -> Dict[str, float]:
    """
    Fetch spot prices in USD for a list of symbols from Chainlink price feeds
    Returns dict[symbol] = price
    """
    out: Dict[str, float] = {}
    
    for symbol in symbols:
        symbol_upper = symbol.upper()
        
        if symbol_upper not in CHAINLINK_FEEDS:
            out[symbol] = float('nan')
            continue
            
        feed_address = CHAINLINK_FEEDS[symbol_upper]
        result = _fetch_price_feed_data(feed_address)
        
        if result:
            price, timestamp = result
            
            # Check if data is fresh (within last hour)
            current_time = int(time.time())
            if current_time - timestamp > 3600:  # 1 hour
                print(f"Chainlink data for {symbol} is stale: {current_time - timestamp} seconds old")
            
            out[symbol] = price
        else:
            out[symbol] = float('nan')
    
    return out

def get_feed_info(symbols: List[str]) -> Dict[str, Dict]:
    """
    Get detailed information about Chainlink price feeds
    """
    out = {}
    
    for symbol in symbols:
        symbol_upper = symbol.upper()
        
        if symbol_upper not in CHAINLINK_FEEDS:
            continue
            
        feed_address = CHAINLINK_FEEDS[symbol_upper]
        result = _fetch_price_feed_data(feed_address)
        
        if result:
            price, timestamp = result
            out[symbol] = {
                "feed_address": feed_address,
                "price": price,
                "timestamp": timestamp,
                "age_seconds": int(time.time()) - timestamp,
                "is_fresh": int(time.time()) - timestamp < 3600
            }
    
    return out

def fetch_historical(symbol: str, blocks_back: int = 100) -> List[Tuple[int, float]]:
    """
    Fetch historical price data from Chainlink (simplified version)
    Note: This would require more complex block iteration for full implementation
    Returns list of (timestamp, price) tuples
    """
    # This is a simplified version - full implementation would require
    # iterating through historical blocks and calling the price feed at each block
    
    symbol_upper = symbol.upper()
    if symbol_upper not in CHAINLINK_FEEDS:
        return []
    
    # For now, just return current price
    current_data = fetch([symbol])
    if symbol in current_data and not str(current_data[symbol]).lower() == 'nan':
        current_time = int(time.time())
        return [(current_time, current_data[symbol])]
    
    return []

def health_check() -> Dict[str, any]:
    """
    Check the health of the Chainlink data source
    """
    health_info = {
        "source": "chainlink",
        "configured": bool(ETH_RPC_URL),
        "feeds_available": len(CHAINLINK_FEEDS),
        "supported_symbols": list(CHAINLINK_FEEDS.keys()),
        "rpc_url_configured": bool(ETH_RPC_URL),
        "status": "unknown"
    }
    
    if not ETH_RPC_URL:
        health_info["status"] = "error"
        health_info["error"] = "ETH_RPC_URL not configured"
        return health_info
    
    # Test with a simple symbol
    try:
        test_result = fetch(["USDT"])
        if "USDT" in test_result and not str(test_result["USDT"]).lower() == 'nan':
            health_info["status"] = "healthy"
            health_info["test_price"] = test_result["USDT"]
        else:
            health_info["status"] = "degraded"
            health_info["error"] = "Test price fetch failed"
    except Exception as e:
        health_info["status"] = "error"
        health_info["error"] = str(e)
    
    return health_info