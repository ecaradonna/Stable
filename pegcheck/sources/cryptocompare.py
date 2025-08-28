"""
CryptoCompare API integration for stablecoin price data
"""

import time
import requests
from typing import Dict, List, Optional, Tuple

from ..core.models import PricePoint
from ..core.config import CRYPTOCOMPARE_BASE_URL, CRYPTOCOMPARE_API_KEY, REQUEST_TIMEOUT

def _headers() -> Dict[str, str]:
    """Get headers for CryptoCompare API requests"""
    headers = {}
    if CRYPTOCOMPARE_API_KEY:
        headers["authorization"] = f"Apikey {CRYPTOCOMPARE_API_KEY}"
    return headers

def fetch(symbols: List[str]) -> Dict[str, float]:
    """
    Fetch spot prices in USD for a list of symbols from CryptoCompare
    Returns dict[symbol] = price
    """
    out: Dict[str, float] = {}
    ts = int(time.time())
    
    for symbol in symbols:
        try:
            url = f"{CRYPTOCOMPARE_BASE_URL}/data/price"
            params = {"fsym": symbol, "tsyms": "USD"}
            headers = _headers()
            
            response = requests.get(url, params=params, headers=headers, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            data = response.json()
            
            if "USD" in data:
                price = float(data["USD"])
                out[symbol] = price
            else:
                out[symbol] = float("nan")
                
        except Exception as e:
            print(f"CryptoCompare error for {symbol}: {e}")
            out[symbol] = float("nan")
    
    return out

def histoday(symbol: str, limit: int = 200, to_ts: Optional[int] = None) -> List[Tuple[int, float]]:
    """
    Get daily historical data for a symbol
    Returns list of (timestamp, close_price) tuples
    """
    try:
        url = f"{CRYPTOCOMPARE_BASE_URL}/data/v2/histoday"
        params = {"fsym": symbol, "tsym": "USD", "limit": int(limit)}
        if to_ts is not None:
            params["toTs"] = int(to_ts)
        
        headers = _headers()
        response = requests.get(url, params=params, headers=headers, timeout=15)
        response.raise_for_status()
        
        data = response.json().get("Data", {}).get("Data", [])
        return [(int(row.get("time", 0)), float(row.get("close", 0.0))) for row in data]
        
    except Exception as e:
        print(f"CryptoCompare histoday error for {symbol}: {e}")
        return []

def histominute(symbol: str, limit: int = 120, to_ts: Optional[int] = None, aggregate: int = 1) -> List[Tuple[int, float]]:
    """
    Get minute historical data for a symbol
    Returns list of (timestamp, close_price) tuples
    """
    try:
        url = f"{CRYPTOCOMPARE_BASE_URL}/data/v2/histominute"
        params = {
            "fsym": symbol, 
            "tsym": "USD", 
            "limit": int(limit), 
            "aggregate": int(aggregate)
        }
        if to_ts is not None:
            params["toTs"] = int(to_ts)
        
        headers = _headers()
        response = requests.get(url, params=params, headers=headers, timeout=15)
        response.raise_for_status()
        
        data = response.json().get("Data", {}).get("Data", [])
        return [(int(row.get("time", 0)), float(row.get("close", 0.0))) for row in data]
        
    except Exception as e:
        print(f"CryptoCompare histominute error for {symbol}: {e}")
        return []

def get_top_list_by_volume(tsym: str = "USD", limit: int = 50) -> Dict[str, Dict]:
    """
    Get top cryptocurrencies by volume
    """
    try:
        url = f"{CRYPTOCOMPARE_BASE_URL}/data/top/totalvolfull"
        params = {"limit": limit, "tsym": tsym}
        headers = _headers()
        
        response = requests.get(url, params=params, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        
        result = {}
        for item in data.get("Data", []):
            coin_info = item.get("CoinInfo", {})
            raw_data = item.get("RAW", {}).get(tsym, {})
            
            symbol = coin_info.get("Name", "")
            if symbol:
                result[symbol] = {
                    "price": raw_data.get("PRICE", 0),
                    "volume_24h": raw_data.get("VOLUME24HOUR", 0),
                    "market_cap": raw_data.get("MKTCAP", 0),
                    "change_24h": raw_data.get("CHANGEPCT24HOUR", 0),
                    "name": coin_info.get("FullName", "")
                }
        
        return result
        
    except Exception as e:
        print(f"CryptoCompare top list error: {e}")
        return {}

def multiple_symbols_full_data(symbols: List[str], tsym: str = "USD") -> Dict[str, Dict]:
    """
    Get full market data for multiple symbols
    """
    try:
        url = f"{CRYPTOCOMPARE_BASE_URL}/data/pricemultifull"
        params = {"fsyms": ",".join(symbols), "tsyms": tsym}
        headers = _headers()
        
        response = requests.get(url, params=params, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        
        result = {}
        raw_data = data.get("RAW", {})
        
        for symbol in symbols:
            if symbol in raw_data and tsym in raw_data[symbol]:
                symbol_data = raw_data[symbol][tsym]
                result[symbol] = {
                    "price": symbol_data.get("PRICE", 0),
                    "volume_24h": symbol_data.get("VOLUME24HOUR", 0),
                    "market_cap": symbol_data.get("MKTCAP", 0),
                    "change_24h": symbol_data.get("CHANGEPCT24HOUR", 0),
                    "high_24h": symbol_data.get("HIGH24HOUR", 0),
                    "low_24h": symbol_data.get("LOW24HOUR", 0),
                    "last_update": symbol_data.get("LASTUPDATE", 0)
                }
        
        return result
        
    except Exception as e:
        print(f"CryptoCompare multi-symbol error: {e}")
        return {}