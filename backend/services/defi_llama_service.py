import aiohttp
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from .data_validator import DataValidator
from .protocol_policy_service import ProtocolPolicyService

logger = logging.getLogger(__name__)

class DefiLlamaService:
    def __init__(self):
        self.base_url = "https://yields.llama.fi"
        self.stablecoins = ["USDT", "USDC", "DAI", "PYUSD", "TUSD"]
        self.validator = DataValidator()
        self.policy_service = ProtocolPolicyService()
        
    async def get_all_pools(self) -> List[Dict[str, Any]]:
        """Get all yield pools from DefiLlama""" 
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/pools") as response:
                    if response.status == 200:
                        data = await response.json()
                        pools = data.get('data', [])
                        logger.info(f"Retrieved {len(pools)} total pools from DefiLlama")
                        return pools
                    else:
                        logger.error(f"DefiLlama API error: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"DefiLlama service error: {str(e)}")
            return []
    
    async def get_stablecoin_pools(self) -> List[Dict[str, Any]]:
        """Filter pools for stablecoins with canonical normalization and policy enforcement"""
        all_pools = await self.get_all_pools()
        stablecoin_pools = []
        processed_count = 0
        valid_count = 0
        
        for pool in all_pools:
            processed_count += 1
            
            # Extract basic pool information
            symbol = pool.get('symbol', '').upper()
            project = pool.get('project', '').lower()
            
            # Check if pool contains supported stablecoins
            canonical_stablecoin = None
            for stablecoin in self.stablecoins:
                if stablecoin in symbol or stablecoin.lower() in symbol.lower():
                    canonical_stablecoin = self.validator.normalize_stablecoin_id(stablecoin)
                    break
            
            if not canonical_stablecoin:
                continue
                
            # Normalize protocol ID
            canonical_protocol = self.validator.normalize_protocol_id(project)
            if not canonical_protocol:
                continue
            
            # Check protocol policy BEFORE processing
            protocol_info = self.policy_service.get_protocol_info(canonical_protocol, pool.get('tvlUsd', 0))
            
            # Skip denied protocols
            if protocol_info.policy_decision.value == 'deny':
                logger.debug(f"Skipping denied protocol {canonical_protocol}: {protocol_info.rationale}")
                continue
                
            # Validate and normalize yield data
            raw_yield_data = {
                'pool_id': pool.get('pool'),
                'symbol': canonical_stablecoin,
                'project': canonical_protocol,
                'chain': pool.get('chain', 'ethereum'),
                'apy': pool.get('apy', 0),
                'tvlUsd': pool.get('tvlUsd', 0),
                'metadata': pool
            }
            
            is_valid, normalized_data, errors = self.validator.validate_and_normalize_yield_data(raw_yield_data)
            
            if is_valid:
                # Add StableYield-specific fields with policy information
                normalized_pool = {
                    'pool_id': normalized_data['pool_id'],
                    'canonical_stablecoin_id': normalized_data['stablecoin_id'],
                    'canonical_protocol_id': normalized_data['protocol_id'],
                    'symbol': symbol,
                    'project': project.title(),
                    'chain': normalized_data['chain_id'],
                    'apy': normalized_data['apy_base'],
                    'tvl': normalized_data['tvl_usd'],
                    'stablecoin': canonical_stablecoin,  # Fix: Add stablecoin field
                    'reputation_score': protocol_info.reputation_score,
                    'reputation_tier': protocol_info.tier,
                    'risk_factors': protocol_info.risk_factors,
                    'policy_decision': protocol_info.policy_decision.value,
                    'is_institutional_grade': self.validator.is_institutional_grade(
                        normalized_data['tvl_usd'], 
                        normalized_data['protocol_id']
                    ),
                    'normalized_data': normalized_data
                }
                
                # Add policy warnings for greylist protocols
                if protocol_info.policy_decision.value == 'greylist':
                    normalized_pool['policy_warning'] = f"Under review: {protocol_info.rationale}"
                
                stablecoin_pools.append(normalized_pool)
                valid_count += 1
            else:
                logger.debug(f"Invalid pool data for {symbol} on {project}: {errors}")
        
        # Apply final policy filtering
        filtered_pools = self.policy_service.filter_pools_by_policy(stablecoin_pools)
        
        logger.info(f"Processed {processed_count} pools, found {valid_count} valid stablecoin pools, {len(filtered_pools)} passed policy filter")
        return filtered_pools
    
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
            
            if coin not in best_yields or apy > best_yields[coin]['currentYield']:
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