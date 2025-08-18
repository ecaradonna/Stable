import aiohttp
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DefiLlamaService:
    def __init__(self):
        self.base_url = "https://yields.llama.fi"
        self.stablecoins = ["USDT", "USDC", "DAI", "PYUSD", "TUSD"]
        
    async def get_all_pools(self) -> List[Dict[str, Any]]:
        """Get all yield pools from DefiLlama"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/pools") as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('data', [])
                    else:
                        logger.error(f"DefiLlama API error: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"DefiLlama service error: {str(e)}")
            return []
    
    async def get_stablecoin_pools(self) -> List[Dict[str, Any]]:
        """Filter pools for stablecoins only"""
        all_pools = await self.get_all_pools()
        stablecoin_pools = []
        
        for pool in all_pools:
            symbol = pool.get('symbol', '').upper()
            project = pool.get('project', '').lower()
            
            # Check if pool contains stablecoins
            for stablecoin in self.stablecoins:
                if stablecoin in symbol or stablecoin.lower() in symbol.lower():
                    # Filter for major DeFi platforms
                    if any(platform in project for platform in ['aave', 'compound', 'curve', 'convex']):
                        stablecoin_pools.append({
                            'pool_id': pool.get('pool_id'),
                            'symbol': symbol,
                            'project': project,
                            'chain': pool.get('chain'),
                            'apy': pool.get('apy', 0),
                            'tvl': pool.get('tvlUsd', 0),
                            'stablecoin': self._extract_stablecoin(symbol)
                        })
                    break
        
        return stablecoin_pools
    
    def _extract_stablecoin(self, symbol: str) -> str:
        """Extract the main stablecoin from pool symbol"""
        for coin in self.stablecoins:
            if coin in symbol.upper():
                return coin
        return symbol.split('-')[0] if '-' in symbol else symbol
    
    async def get_pool_history(self, pool_id: str) -> List[Dict[str, Any]]:
        """Get historical data for a specific pool"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/chart/{pool_id}") as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('data', [])
                    else:
                        logger.error(f"DefiLlama history API error: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"DefiLlama history service error: {str(e)}")
            return []
    
    async def get_best_yields(self) -> Dict[str, Dict[str, Any]]:
        """Get the best yield for each stablecoin"""
        pools = await self.get_stablecoin_pools()
        best_yields = {}
        
        for pool in pools:
            coin = pool['stablecoin']
            apy = float(pool['apy']) if pool['apy'] else 0
            
            if coin not in best_yields or apy > best_yields[coin]['apy']:
                best_yields[coin] = {
                    'stablecoin': coin,
                    'name': self._get_coin_name(coin),
                    'currentYield': apy,
                    'source': pool['project'].title(),
                    'sourceType': 'DeFi',
                    'riskScore': self._calculate_risk_score(pool['project'], apy),
                    'liquidity': self._format_liquidity(pool['tvl']),
                    'metadata': {
                        'pool_id': pool['pool_id'],
                        'chain': pool['chain'],
                        'tvl': pool['tvl']
                    }
                }
        
        return best_yields
    
    def _get_coin_name(self, symbol: str) -> str:
        """Get full name for stablecoin"""
        names = {
            'USDT': 'Tether USD',
            'USDC': 'USD Coin', 
            'DAI': 'Dai Stablecoin',
            'PYUSD': 'PayPal USD',
            'TUSD': 'TrueUSD'
        }
        return names.get(symbol, symbol)
    
    def _calculate_risk_score(self, project: str, apy: float) -> str:
        """Calculate risk score based on project and APY"""
        major_protocols = ['aave', 'compound']
        
        if any(proto in project.lower() for proto in major_protocols):
            if apy > 15:
                return 'Medium'
            else:
                return 'Low'
        else:
            if apy > 10:
                return 'High'
            else:
                return 'Medium'
    
    def _format_liquidity(self, tvl: float) -> str:
        """Format TVL as liquidity string"""
        if tvl >= 1e9:
            return f"${tvl/1e9:.1f}B"
        elif tvl >= 1e6:
            return f"${tvl/1e6:.1f}M"
        else:
            return f"${tvl:,.0f}"
    
    async def get_yields_for_token(self, symbol: str) -> Optional[float]:
        """Get the best yield for a specific token"""
        try:
            best_yields = await self.get_best_yields()
            if symbol.upper() in best_yields:
                return best_yields[symbol.upper()]['currentYield']
            return None
        except Exception as e:
            logger.error(f"Error getting yields for {symbol}: {e}")
            return None