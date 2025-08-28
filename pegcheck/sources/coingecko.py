"""
CoinGecko API integration for stablecoin price data
"""

import time
import requests
from typing import Dict, List, Optional, Tuple

from ..core.models import PricePoint
from ..core.config import COINGECKO_BASE_URL, COINGECKO_IDS, REQUEST_TIMEOUT

def _get_coingecko_id(symbol: str) -> Optional[str]:
    """Get CoinGecko ID for a symbol"""
    return COINGECKO_IDS.get(symbol.upper())

def fetch(symbols: List[str]) -> Dict[str, float]:
    """
    Fetch spot prices in USD for a list of symbols from CoinGecko
    Returns dict[symbol] = price
    """
    out: Dict[str, float] = {}
    ts = int(time.time())
    
    # Map symbols to CoinGecko IDs
    symbol_to_id = {}
    valid_ids = []
    
    for symbol in symbols:
        gecko_id = _get_coingecko_id(symbol)
        if gecko_id:
            symbol_to_id[gecko_id] = symbol
            valid_ids.append(gecko_id)
    
    if not valid_ids:
        # No valid CoinGecko IDs found
        return {symbol: float('nan') for symbol in symbols}
    
    try:
        # Batch request for all symbols
        ids_str = ','.join(valid_ids)
        url = f"{COINGECKO_BASE_URL}/simple/price"
        params = {
            'ids': ids_str,
            'vs_currencies': 'usd'
        }
        
        response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        
        # Parse response and map back to symbols
        for gecko_id, symbol in symbol_to_id.items():
            if gecko_id in data and 'usd' in data[gecko_id]:
                price = float(data[gecko_id]['usd'])
                out[symbol] = price
            else:
                out[symbol] = float('nan')
        
        # Fill in any missing symbols with NaN
        for symbol in symbols:
            if symbol not in out:
                out[symbol] = float('nan')
                
    except Exception as e:
        print(f"CoinGecko API error: {e}")
        # Return NaN for all symbols on error
        out = {symbol: float('nan') for symbol in symbols}
    
    return out

def fetch_historical(symbol: str, days: int = 30) -> List[Tuple[int, float]]:
    """
    Fetch historical price data for a symbol
    Returns list of (timestamp, price) tuples
    """
    gecko_id = _get_coingecko_id(symbol)
    if not gecko_id:
        return []
    
    try:
        url = f"{COINGECKO_BASE_URL}/coins/{gecko_id}/market_chart"
        params = {
            'vs_currency': 'usd',
            'days': str(days),
            'interval': 'daily' if days > 1 else 'hourly'
        }
        
        response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        
        if 'prices' in data:
            # CoinGecko returns timestamps in milliseconds, convert to seconds
            return [(int(point[0] / 1000), float(point[1])) for point in data['prices']]
        
    except Exception as e:
        print(f"CoinGecko historical data error for {symbol}: {e}")
    
    return []

def get_market_data(symbols: List[str]) -> Dict[str, Dict]:
    """
    Get detailed market data including volume, market cap, etc.
    """
    out = {}
    
    # Map symbols to CoinGecko IDs
    symbol_to_id = {}
    valid_ids = []
    
    for symbol in symbols:
        gecko_id = _get_coingecko_id(symbol)
        if gecko_id:
            symbol_to_id[gecko_id] = symbol
            valid_ids.append(gecko_id)
    
    if not valid_ids:
        return {}
    
    try:
        ids_str = ','.join(valid_ids)
        url = f"{COINGECKO_BASE_URL}/coins/markets"
        params = {
            'vs_currency': 'usd',
            'ids': ids_str,
            'order': 'market_cap_desc',
            'per_page': 100,
            'page': 1,
            'sparkline': False
        }
        
        response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        
        for coin_data in data:
            gecko_id = coin_data.get('id')
            if gecko_id in symbol_to_id:
                symbol = symbol_to_id[gecko_id]
                out[symbol] = {
                    'price': coin_data.get('current_price', 0),
                    'market_cap': coin_data.get('market_cap', 0),
                    'volume_24h': coin_data.get('total_volume', 0),
                    'price_change_24h': coin_data.get('price_change_percentage_24h', 0),
                    'last_updated': coin_data.get('last_updated', '')
                }
        
    except Exception as e:
        print(f"CoinGecko market data error: {e}")
    
    return out