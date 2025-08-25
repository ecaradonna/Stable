import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
from .defi_llama_service import DefiLlamaService
from .binance_service import BinanceService
from .protocol_policy_service import ProtocolPolicyService

logger = logging.getLogger(__name__)

class YieldAggregator:
    def __init__(self):
        self.defi_llama = DefiLlamaService()
        self.binance = BinanceService()
        self.policy_service = ProtocolPolicyService()
        self.cache = {}
        self.cache_expiry = {}
        self.cache_duration = timedelta(minutes=5)  # Cache for 5 minutes
        
    async def get_all_yields(self, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """Get aggregated yields from all sources"""
        cache_key = "all_yields"
        
        # Check cache first
        if not force_refresh and self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        try:
            # Get data from all sources concurrently
            defi_yields_task = self.defi_llama.get_best_yields()
            cefi_yields_task = self.binance.get_stablecoin_yields()
            
            defi_yields, cefi_yields = await asyncio.gather(
                defi_yields_task, 
                cefi_yields_task,
                return_exceptions=True
            )
            
            # Handle exceptions
            if isinstance(defi_yields, Exception):
                logger.error(f"DeFi yields error: {defi_yields}")
                defi_yields = {}
                
            if isinstance(cefi_yields, Exception):
                logger.error(f"CeFi yields error: {cefi_yields}")
                cefi_yields = {}
            
            # Combine and prioritize yields
            combined_yields = self._combine_yields(defi_yields, cefi_yields)
            
            # Apply protocol policy filtering
            filtered_yields = self._apply_policy_filtering(combined_yields)
            
            # Add 24h change simulation (in production, this would be calculated from historical data)
            for yield_data in filtered_yields:
                yield_data['change24h'] = self._simulate_24h_change()
            
            # Cache the results
            self.cache[cache_key] = filtered_yields
            self.cache_expiry[cache_key] = datetime.utcnow() + self.cache_duration
            
            return filtered_yields
            
        except Exception as e:
            logger.error(f"Yield aggregation error: {str(e)}")
            return self._get_fallback_data()
    
    def _combine_yields(self, defi_yields: Dict, cefi_yields: Dict) -> List[Dict[str, Any]]:
        """Combine yields from different sources, prioritizing higher yields"""
        combined = {}
        
        # Add DeFi yields
        for coin, data in defi_yields.items():
            combined[coin] = data
            
        # Add or update with CeFi yields (prioritize higher yield)
        for coin, data in cefi_yields.items():
            if coin not in combined or data['currentYield'] > combined[coin]['currentYield']:
                combined[coin] = data
                
        # Convert to list and sort by yield (highest first)
        result = list(combined.values())
        result.sort(key=lambda x: x['currentYield'], reverse=True)
        
        return result
    
    def _simulate_24h_change(self) -> float:
        """Simulate 24h change (replace with real calculation in production)"""
        import random
        return round(random.uniform(-0.5, 0.5), 2)
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cache is still valid"""
        if cache_key not in self.cache or cache_key not in self.cache_expiry:
            return False
        return datetime.utcnow() < self.cache_expiry[cache_key]
    
    def _get_fallback_data(self) -> List[Dict[str, Any]]:
        """Fallback data when all APIs fail"""
        return [
            {
                'stablecoin': 'USDT',
                'name': 'Tether USD',
                'currentYield': 8.45,
                'source': 'Binance Earn',
                'sourceType': 'CeFi',
                'riskScore': 'Medium',
                'change24h': 0.12,
                'liquidity': '$89.2B',
                'metadata': {'fallback': True}
            },
            {
                'stablecoin': 'USDC',
                'name': 'USD Coin', 
                'currentYield': 7.82,
                'source': 'Aave V3',
                'sourceType': 'DeFi',
                'riskScore': 'Low',
                'change24h': -0.05,
                'liquidity': '$32.1B',
                'metadata': {'fallback': True}
            },
            {
                'stablecoin': 'DAI',
                'name': 'Dai Stablecoin',
                'currentYield': 6.95,
                'source': 'Compound',
                'sourceType': 'DeFi', 
                'riskScore': 'Medium',
                'change24h': 0.08,
                'liquidity': '$4.8B',
                'metadata': {'fallback': True}
            }
        ]
    
    async def get_stablecoin_yield(self, stablecoin: str) -> Optional[Dict[str, Any]]:
        """Get yield data for a specific stablecoin"""
        all_yields = await self.get_all_yields()
        
        for yield_data in all_yields:
            if yield_data['stablecoin'].upper() == stablecoin.upper():
                return yield_data
                
        return None
    
    async def get_historical_data(self, stablecoin: str, days: int = 7) -> List[Dict[str, Any]]:
        """Get historical yield data (simulated for now)"""
        # In production, this would query historical data from database
        # For now, we'll simulate historical data
        import random
        from datetime import date, timedelta
        
        current_yield_data = await self.get_stablecoin_yield(stablecoin)
        if not current_yield_data:
            return []
            
        base_yield = current_yield_data['currentYield']
        historical_data = []
        
        for i in range(days, 0, -1):
            date_point = date.today() - timedelta(days=i)
            # Simulate historical yield with some variance
            yield_value = base_yield + random.uniform(-1, 1)
            
            historical_data.append({
                'date': date_point.isoformat(),
                'yield': round(yield_value, 2)
            })
            
        return historical_data
    
    async def refresh_cache(self):
        """Force refresh all cached data"""
        await self.get_all_yields(force_refresh=True)
        logger.info("Yield data cache refreshed")