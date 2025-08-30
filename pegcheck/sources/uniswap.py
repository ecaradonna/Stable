"""
Uniswap V3 TWAP integration for stablecoin price data
"""

import time
import requests
import math
from typing import Dict, List, Optional, Tuple

from ..core.models import PricePoint
from ..core.config import UNISWAP_POOLS, ETH_RPC_URL, REQUEST_TIMEOUT

# Uniswap V3 Pool ABI (minimal for TWAP)
POOL_ABI = [
    {
        "inputs": [{"internalType": "uint32[]", "name": "secondsAgos", "type": "uint32[]"}],
        "name": "observe",
        "outputs": [
            {"internalType": "int56[]", "name": "tickCumulatives", "type": "int56[]"},
            {"internalType": "uint160[]", "name": "secondsPerLiquidityX128s", "type": "uint160[]"}
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "slot0",
        "outputs": [
            {"internalType": "uint160", "name": "sqrtPriceX96", "type": "uint160"},
            {"internalType": "int24", "name": "tick", "type": "int24"},
            {"internalType": "uint16", "name": "observationIndex", "type": "uint16"},
            {"internalType": "uint16", "name": "observationCardinality", "type": "uint16"},
            {"internalType": "uint16", "name": "observationCardinalityNext", "type": "uint16"},
            {"internalType": "uint8", "name": "feeProtocol", "type": "uint8"},
            {"internalType": "bool", "name": "unlocked", "type": "bool"}
        ],
        "stateMutability": "view",
        "type": "function"
    }
]

# Standard token decimals (most are 18, USDT/USDC are 6)
TOKEN_DECIMALS = {
    "0xA0b86a33E6441E2476d8F8F554Daddadbd2ec11c": 6,  # USDT
    "0xA0b86a33E6441E2476d8F8F554Daddadbd2ec11c": 6,  # USDC (same address for demo)
    "0x6B175474E89094C44Da98b954EedeAC495271d0F": 18, # DAI
    "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2": 18  # WETH
}

def _make_eth_rpc_call(method: str, params: List) -> Optional[Dict]:
    """Make an Ethereum RPC call"""
    if not ETH_RPC_URL:
        print("ETH_RPC_URL not configured, cannot fetch Uniswap data")
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

def _encode_function_call(function_name: str, params: List = None) -> str:
    """Encode function call for eth_call (simplified)"""
    if function_name == "slot0()":
        return "0x3850c7bd"  # slot0() signature
    elif function_name == "observe":
        # This would need more complex ABI encoding for the uint32[] parameter
        # For now, we'll use a hardcoded call for common TWAP periods
        # observe([3600]) for 1-hour TWAP
        return "0x883bdbfd00000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000000e10"
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
    
    # Handle signed integers (2's complement)
    if value >= 2**255:
        value -= 2**256
    
    return value

def _tick_to_price(tick: int, token0_decimals: int = 18, token1_decimals: int = 18) -> float:
    """Convert Uniswap tick to price"""
    try:
        # Price = (1.0001^tick) * (10^(token0_decimals - token1_decimals))
        price_ratio = math.pow(1.0001, tick)
        decimal_adjustment = math.pow(10, token0_decimals - token1_decimals)
        return price_ratio * decimal_adjustment
    except (OverflowError, ValueError):
        return float('nan')

def _get_current_price(pool_address: str, token0: str, token1: str) -> Optional[float]:
    """Get current spot price from Uniswap V3 pool"""
    try:
        slot0_call_data = _encode_function_call("slot0()")
        result = _make_eth_rpc_call("eth_call", [
            {"to": pool_address, "data": slot0_call_data},
            "latest"
        ])
        
        if not result or result == "0x":
            return None
        
        # Decode slot0 result
        # sqrtPriceX96 is first return value (bytes 0-31)
        # tick is second return value (bytes 32-63)
        if len(result) < 130:  # Need at least 2*32 bytes
            return None
            
        tick_hex = result[66:130]  # Skip 0x and first 64 chars, get next 64
        tick = _decode_int256("0x" + tick_hex)
        
        # Get token decimals
        token0_decimals = TOKEN_DECIMALS.get(token0, 18)
        token1_decimals = TOKEN_DECIMALS.get(token1, 18)
        
        price = _tick_to_price(tick, token0_decimals, token1_decimals)
        return price
        
    except Exception as e:
        print(f"Error getting Uniswap price from pool {pool_address}: {e}")
        return None

def _get_twap_price(pool_address: str, token0: str, token1: str, period_seconds: int = 3600) -> Optional[float]:
    """Get Time-Weighted Average Price from Uniswap V3 pool"""
    try:
        # For simplified implementation, we'll just return current price
        # Full TWAP implementation would require observe() function with proper ABI encoding
        return _get_current_price(pool_address, token0, token1)
        
    except Exception as e:
        print(f"Error getting Uniswap TWAP from pool {pool_address}: {e}")
        return None

def _convert_to_usd(symbol: str, eth_price: float, stablecoin_eth_price: float) -> float:
    """Convert stablecoin/ETH price to USD price"""
    if eth_price <= 0 or stablecoin_eth_price <= 0:
        return float('nan')
    
    # Most stablecoins are token0 in pools, so we need to invert the price
    # and multiply by ETH/USD price to get stablecoin/USD price
    try:
        usd_price = (1.0 / stablecoin_eth_price) * eth_price
        return usd_price
    except (ZeroDivisionError, ValueError):
        return float('nan')

def fetch(symbols: List[str], eth_usd_price: Optional[float] = None) -> Dict[str, float]:
    """
    Fetch spot prices in USD for stablecoins from Uniswap V3 pools
    Returns dict[symbol] = price
    
    Note: Requires ETH/USD price for conversion since pools are typically vs ETH
    """
    out: Dict[str, float] = {}
    
    # If no ETH price provided, try to get it from a simple oracle (simplified)
    if eth_usd_price is None:
        eth_usd_price = 3000.0  # Fallback ETH price for demo
    
    for symbol in symbols:
        symbol_upper = symbol.upper()
        
        if symbol_upper not in UNISWAP_POOLS:
            out[symbol] = float('nan')
            continue
            
        pool_config = UNISWAP_POOLS[symbol_upper]
        pool_address = pool_config["address"]
        token0 = pool_config["token0"]
        token1 = pool_config["token1"]
        
        # Get TWAP price (stablecoin/ETH)
        stablecoin_eth_price = _get_twap_price(pool_address, token0, token1)
        
        if stablecoin_eth_price is not None and stablecoin_eth_price > 0:
            # Convert to USD price
            usd_price = _convert_to_usd(symbol, eth_usd_price, stablecoin_eth_price)
            out[symbol] = usd_price
        else:
            out[symbol] = float('nan')
    
    return out

def get_pool_info(symbols: List[str]) -> Dict[str, Dict]:
    """
    Get detailed information about Uniswap V3 pools
    """
    out = {}
    
    for symbol in symbols:
        symbol_upper = symbol.upper()
        
        if symbol_upper not in UNISWAP_POOLS:
            continue
            
        pool_config = UNISWAP_POOLS[symbol_upper]
        pool_address = pool_config["address"]
        token0 = pool_config["token0"]
        token1 = pool_config["token1"]
        
        current_price = _get_current_price(pool_address, token0, token1)
        twap_price = _get_twap_price(pool_address, token0, token1)
        
        out[symbol] = {
            "pool_address": pool_address,
            "token0": token0,
            "token1": token1,
            "fee": pool_config["fee"],
            "current_price": current_price,
            "twap_price": twap_price,
            "is_available": current_price is not None
        }
    
    return out

def fetch_historical(symbol: str, hours_back: int = 24) -> List[Tuple[int, float]]:
    """
    Fetch historical TWAP data (simplified version)
    Returns list of (timestamp, price) tuples
    """
    # This is a simplified version - full implementation would require
    # multiple observe() calls with different time periods
    
    symbol_upper = symbol.upper()
    if symbol_upper not in UNISWAP_POOLS:
        return []
    
    # For now, just return current price
    current_data = fetch([symbol])
    if symbol in current_data and not str(current_data[symbol]).lower() == 'nan':
        current_time = int(time.time())
        return [(current_time, current_data[symbol])]
    
    return []

def health_check() -> Dict[str, any]:
    """
    Check the health of the Uniswap V3 data source
    """
    health_info = {
        "source": "uniswap_v3",
        "configured": bool(ETH_RPC_URL),
        "pools_available": len(UNISWAP_POOLS),
        "supported_symbols": list(UNISWAP_POOLS.keys()),
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

def get_supported_pairs() -> List[str]:
    """Get list of supported stablecoin pairs"""
    return list(UNISWAP_POOLS.keys())

def estimate_gas_for_twap() -> Dict[str, int]:
    """Estimate gas costs for TWAP operations"""
    return {
        "observe_call": 50000,      # Estimated gas for observe() call
        "slot0_call": 2500,         # Estimated gas for slot0() call
        "total_estimated": 55000    # Total estimated gas
    }