import os
import asyncio
import aiohttp
import websockets
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from collections import deque
import math

logger = logging.getLogger(__name__)

class CryptoCompareService:
    def __init__(self):
        self.api_key = os.getenv('CC_API_KEY_STABLEYIELD', 'DEMO_KEY')
        self.base_url = "https://min-api.cryptocompare.com/data"
        self.ws_url = f"wss://streamer.cryptocompare.com/v2?api_key={self.api_key}"
        self.stablecoins = ["USDT", "USDC", "DAI", "TUSD", "FRAX", "USDP", "GUSD"]
        
        # In-memory storage for real-time calculations
        self.price_cache = {}
        self.price_history = {symbol: deque(maxlen=720) for symbol in self.stablecoins}  # 12h of 1min data
        
    async def get_multi_price(self) -> Dict[str, float]:
        """Get current prices for all stablecoins"""
        try:
            if self.api_key == 'DEMO_KEY':
                return self._get_demo_prices()
                
            async with aiohttp.ClientSession() as session:
                params = {
                    'fsyms': ','.join(self.stablecoins),
                    'tsyms': 'USD',
                    'api_key': self.api_key
                }
                
                async with session.get(f"{self.base_url}/pricemulti", params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {symbol: data.get(symbol, {}).get('USD', 1.0) for symbol in self.stablecoins}
                    else:
                        logger.error(f"CryptoCompare API error: {response.status}")
                        return self._get_demo_prices()
                        
        except Exception as e:
            logger.error(f"CryptoCompare service error: {str(e)}")
            return self._get_demo_prices()
    
    def _get_demo_prices(self) -> Dict[str, float]:
        """Demo prices when API is not available"""
        import random
        base_prices = {
            'USDT': 1.0002,
            'USDC': 0.9998, 
            'DAI': 1.0001,
            'TUSD': 0.9999,
            'FRAX': 1.0003,
            'USDP': 0.9997,
            'GUSD': 1.0000
        }
        
        # Add small random variations to simulate real market data
        return {
            symbol: price + random.uniform(-0.0005, 0.0005) 
            for symbol, price in base_prices.items()
        }
    
    async def get_top_exchanges(self, symbol: str) -> List[Dict[str, Any]]:
        """Get top exchanges for a stablecoin"""
        try:
            if self.api_key == 'DEMO_KEY':
                return self._get_demo_exchanges(symbol)
                
            async with aiohttp.ClientSession() as session:
                params = {
                    'fsym': symbol,
                    'tsym': 'USD',
                    'api_key': self.api_key
                }
                
                async with session.get(f"{self.base_url}/top/exchanges", params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('Data', [])
                    else:
                        return self._get_demo_exchanges(symbol)
                        
        except Exception as e:
            logger.error(f"Error fetching exchanges for {symbol}: {str(e)}")
            return self._get_demo_exchanges(symbol)
    
    def _get_demo_exchanges(self, symbol: str) -> List[Dict[str, Any]]:
        """Demo exchange data"""
        exchanges = ['Binance', 'Coinbase Pro', 'Kraken', 'Bybit', 'OKX', 'Bitstamp']
        base_volume = {'USDT': 1e9, 'USDC': 8e8, 'DAI': 2e8}.get(symbol, 1e8)
        
        return [
            {
                'MARKET': exchange,
                'PRICE': 1.0 + random.uniform(-0.001, 0.001),
                'VOLUME24HOUR': base_volume * random.uniform(0.1, 0.3),
                'VOLUME24HOURTO': base_volume * random.uniform(0.1, 0.3)
            }
            for i, exchange in enumerate(exchanges[:5])
        ]
    
    def calculate_vwap(self, exchanges: List[Dict[str, Any]]) -> float:
        """Calculate volume-weighted average price"""
        total_value = 0
        total_volume = 0
        
        for exchange in exchanges:
            price = float(exchange.get('PRICE', 1.0))
            volume = float(exchange.get('VOLUME24HOUR', 0))
            
            if volume > 0:
                total_value += price * volume
                total_volume += volume
        
        return total_value / total_volume if total_volume > 0 else 1.0
    
    def calculate_peg_metrics(self, symbol: str, current_price: float) -> Dict[str, float]:
        """Calculate peg stability metrics"""
        # Store current price in history
        self.price_history[symbol].append({
            'price': current_price,
            'timestamp': datetime.utcnow()
        })
        
        # Calculate peg deviation
        peg_dev_bps = 10000 * (current_price - 1.0) / 1.0
        
        # Calculate volatility (simplified - using recent price history)
        recent_prices = [p['price'] for p in list(self.price_history[symbol])[-60:]]  # Last 60 data points
        
        if len(recent_prices) > 1:
            price_changes = [abs(recent_prices[i] - recent_prices[i-1]) for i in range(1, len(recent_prices))]
            peg_vol_5m_bps = 10000 * (sum(price_changes) / len(price_changes)) if price_changes else 0
        else:
            peg_vol_5m_bps = 0
        
        # Calculate peg score (0-1)
        peg_score = max(0, min(1, 1 - (abs(peg_dev_bps) / 50) - (peg_vol_5m_bps / 100)))
        
        return {
            'peg_dev_bps': peg_dev_bps,
            'peg_vol_5m_bps': peg_vol_5m_bps,
            'peg_vol_1h_bps': peg_vol_5m_bps * 2,  # Simplified
            'peg_score': peg_score
        }
    
    def calculate_liquidity_score(self, exchanges: List[Dict[str, Any]], symbol: str) -> Dict[str, float]:
        """Calculate liquidity metrics"""
        # Simulate depth calculations (in production, would use order book data)
        total_volume = sum(float(ex.get('VOLUME24HOUR', 0)) for ex in exchanges)
        
        # Estimate depth based on volume (simplified proxy)
        depth_10bps = min(total_volume * 0.001, 50_000_000)  # Cap at $50M
        depth_20bps = min(total_volume * 0.002, 100_000_000)  # Cap at $100M
        depth_50bps = min(total_volume * 0.005, 200_000_000)  # Cap at $200M
        
        # Calculate average spread (demo data)
        avg_spread_bps = random.uniform(1, 5) if symbol in ['USDT', 'USDC'] else random.uniform(3, 10)
        
        # Calculate liquidity score
        w1, w2, w3 = 0.4, 0.4, 0.2
        liq_score = (
            w1 * min(depth_10bps / 10_000_000, 1) +
            w2 * min(depth_20bps / 25_000_000, 1) +
            w3 * min(1 / (1 + avg_spread_bps / 5), 1)
        )
        
        return {
            'depth_10bps_usd': depth_10bps,
            'depth_20bps_usd': depth_20bps,
            'depth_50bps_usd': depth_50bps,
            'avg_spread_bps': avg_spread_bps,
            'liq_score': liq_score,
            'venues_covered': len(exchanges)
        }
    
    async def get_comprehensive_metrics(self, symbol: str) -> Dict[str, Any]:
        """Get comprehensive metrics for a stablecoin"""
        try:
            # Get current prices and exchanges
            prices = await self.get_multi_price()
            exchanges = await self.get_top_exchanges(symbol)
            
            current_price = prices.get(symbol, 1.0)
            vwap = self.calculate_vwap(exchanges)
            
            # Calculate peg metrics
            peg_metrics = self.calculate_peg_metrics(symbol, vwap)
            
            # Calculate liquidity metrics
            liq_metrics = self.calculate_liquidity_score(exchanges, symbol)
            
            return {
                'symbol': symbol,
                'vw_price': vwap,
                'current_price': current_price,
                **peg_metrics,
                **liq_metrics,
                'asof': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting comprehensive metrics for {symbol}: {str(e)}")
            return self._get_fallback_metrics(symbol)
    
    def _get_fallback_metrics(self, symbol: str) -> Dict[str, Any]:
        """Fallback metrics when API is unavailable"""
        return {
            'symbol': symbol,
            'vw_price': 1.0,
            'current_price': 1.0,
            'peg_dev_bps': 0.0,
            'peg_vol_5m_bps': 2.0,
            'peg_vol_1h_bps': 4.0,
            'peg_score': 0.95,
            'depth_10bps_usd': 10_000_000,
            'depth_20bps_usd': 25_000_000,
            'depth_50bps_usd': 50_000_000,
            'avg_spread_bps': 2.0,
            'liq_score': 0.85,
            'venues_covered': 5,
            'asof': datetime.utcnow().isoformat()
        }
    
    def calculate_risk_adjusted_yield(self, apy: float, peg_score: float, liq_score: float, 
                                    alpha: float = 1.0, beta: float = 0.7) -> float:
        """Calculate risk-adjusted yield"""
        return apy * (peg_score ** alpha) * (liq_score ** beta)

# Import random for demo data
import random