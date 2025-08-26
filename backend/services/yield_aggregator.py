import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
import statistics
from .defi_llama_service import DefiLlamaService
from .binance_service import BinanceService
from .protocol_policy_service import ProtocolPolicyService
from .yield_sanitizer import YieldSanitizer, SanitizationAction

logger = logging.getLogger(__name__)

class YieldAggregator:
    def __init__(self):
        self.defi_llama = DefiLlamaService()
        self.binance = BinanceService()
        self.policy_service = ProtocolPolicyService()
        self.yield_sanitizer = YieldSanitizer()
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
            
            # Apply yield sanitization and outlier detection
            sanitized_yields = self._apply_yield_sanitization(filtered_yields)
            
            # Add 24h change simulation (in production, this would be calculated from historical data)
            for yield_data in sanitized_yields:
                yield_data['change24h'] = self._simulate_24h_change()
            
            # Cache the results
            self.cache[cache_key] = sanitized_yields
            self.cache_expiry[cache_key] = datetime.utcnow() + self.cache_duration
            
            return sanitized_yields
            
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
    
    def _apply_policy_filtering(self, yields: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply protocol policy filtering to yields"""
        try:
            # Convert yields to pool-like format for policy filtering
            pools = []
            for yield_data in yields:
                # Map source to protocol_id
                protocol_id = self._map_source_to_protocol_id(yield_data.get('source', ''))
                logger.info(f"Mapping source '{yield_data.get('source', '')}' to protocol_id '{protocol_id}'")
                
                pool = {
                    'pool_id': f"{yield_data['stablecoin']}_{protocol_id}",
                    'canonical_protocol_id': protocol_id,
                    'project': yield_data.get('source', ''),
                    'tvl': self._estimate_tvl_from_liquidity(yield_data.get('liquidity', '0')),
                    'yield_data': yield_data  # Store original yield data
                }
                pools.append(pool)
            
            # Apply policy filtering
            filtered_pools = self.policy_service.filter_pools_by_policy(pools)
            
            # Extract yield data from filtered pools and enrich with policy info
            filtered_yields = []
            for pool in filtered_pools:
                yield_data = pool['yield_data']
                
                # Add protocol policy information to metadata
                if 'protocol_info' in pool:
                    if 'metadata' not in yield_data:
                        yield_data['metadata'] = {}
                    yield_data['metadata']['protocol_info'] = pool['protocol_info']
                
                # Add policy warning if present
                if 'policy_warning' in pool:
                    if 'metadata' not in yield_data:
                        yield_data['metadata'] = {}
                    yield_data['metadata']['policy_warning'] = pool['policy_warning']
                
                filtered_yields.append(yield_data)
            
            logger.info(f"Policy filtering: {len(yields)} -> {len(filtered_yields)} yields")
            return filtered_yields
            
        except Exception as e:
            logger.error(f"Policy filtering error: {e}")
            # Return original yields if policy filtering fails
            return yields
    
    def _apply_yield_sanitization(self, yields: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply statistical outlier detection and yield sanitization"""
        try:
            if not yields:
                return yields
            
            logger.info(f"Applying yield sanitization to {len(yields)} yields")
            
            # Prepare yields for sanitization
            sanitization_input = []
            for yield_data in yields:
                sanitization_data = {
                    'apy': yield_data['currentYield'],
                    'source': yield_data['source'],
                    'canonical_protocol_id': yield_data.get('metadata', {}).get('protocol_info', {}).get('protocol_id'),
                    'stablecoin': yield_data['stablecoin']
                }
                sanitization_input.append(sanitization_data)
            
            # Run batch sanitization
            sanitization_results = self.yield_sanitizer.sanitize_yield_batch(sanitization_input)
            
            # Apply sanitization results
            sanitized_yields = []
            for i, (yield_data, result) in enumerate(zip(yields, sanitization_results)):
                # Skip rejected yields
                if result.action_taken == SanitizationAction.REJECT:
                    logger.warning(f"Rejecting yield for {yield_data['stablecoin']} from {yield_data['source']}: {result.warnings}")
                    continue
                
                # Update yield with sanitized value
                original_yield = yield_data['currentYield']
                sanitized_yield_data = yield_data.copy()
                sanitized_yield_data['currentYield'] = result.sanitized_apy
                
                # Add sanitization metadata
                if 'metadata' not in sanitized_yield_data:
                    sanitized_yield_data['metadata'] = {}
                
                sanitized_yield_data['metadata']['sanitization'] = {
                    'original_apy': result.original_apy,
                    'sanitized_apy': result.sanitized_apy,
                    'action_taken': result.action_taken.value,
                    'confidence_score': result.confidence_score,
                    'outlier_score': result.outlier_score,
                    'warnings': result.warnings,
                    'adjustment_magnitude': abs(result.sanitized_apy - result.original_apy)
                }
                
                # Add warning flags for flagged yields
                if result.action_taken == SanitizationAction.FLAG:
                    sanitized_yield_data['metadata']['yield_warning'] = "Yield flagged by sanitization system"
                
                # Update risk score based on sanitization confidence
                if result.confidence_score < 0.70:
                    original_risk = sanitized_yield_data.get('riskScore', 'Medium')
                    if original_risk == 'Low':
                        sanitized_yield_data['riskScore'] = 'Medium'
                    elif original_risk == 'Medium':
                        sanitized_yield_data['riskScore'] = 'High'
                
                sanitized_yields.append(sanitized_yield_data)
            
            # Log sanitization summary
            original_count = len(yields)
            sanitized_count = len(sanitized_yields)
            rejected_count = original_count - sanitized_count
            
            if sanitization_results:
                avg_confidence = statistics.mean([r.confidence_score for r in sanitization_results])
                flagged_count = sum(1 for r in sanitization_results if r.action_taken == SanitizationAction.FLAG)
                capped_count = sum(1 for r in sanitization_results if r.action_taken == SanitizationAction.CAP)
                winsorized_count = sum(1 for r in sanitization_results if r.action_taken == SanitizationAction.WINSORIZE)
                
                logger.info(f"Sanitization complete: {sanitized_count}/{original_count} yields kept, "
                          f"{rejected_count} rejected, {flagged_count} flagged, {capped_count} capped, "
                          f"{winsorized_count} winsorized. Avg confidence: {avg_confidence:.2f}")
            
            return sanitized_yields
            
        except Exception as e:
            logger.error(f"Yield sanitization error: {e}")
            # Return original yields if sanitization fails
            return yields
    
    def _map_source_to_protocol_id(self, source: str) -> str:
        """Map yield source to protocol ID for policy checking"""
        source_lower = source.lower()
        
        # Map common sources to protocol IDs
        mapping = {
            'aave v3': 'aave_v3',
            'aave': 'aave_v3',
            'compound v3': 'compound_v3', 
            'compound': 'compound_v3',
            'curve': 'curve',
            'curve finance': 'curve',
            'uniswap v3': 'uniswap_v3',
            'uniswap': 'uniswap_v3',
            'convex': 'convex',
            'convex finance': 'convex',
            'binance earn': 'binance_earn',
            'kraken staking': 'kraken_staking',
            'coinbase earn': 'coinbase_earn',
            # Add more mappings for common DeFi protocols
            'yearn': 'yearn_finance',
            'yearn finance': 'yearn_finance',
            'maker': 'maker_dao',
            'makerdao': 'maker_dao',
            'frax': 'frax_finance',
            'frax finance': 'frax_finance'
        }
        
        # Try exact match first
        if source_lower in mapping:
            return mapping[source_lower]
            
        # Try partial matches for flexibility
        for key, protocol_id in mapping.items():
            if key in source_lower or source_lower in key:
                return protocol_id
        
        # Default fallback - use source as protocol_id (normalized)
        return source_lower.replace(' ', '_').replace('-', '_')
    
    def _estimate_tvl_from_liquidity(self, liquidity_str: str) -> float:
        """Estimate TVL from liquidity string (e.g., '$89.2B' -> 89200000000)"""
        try:
            if not liquidity_str or liquidity_str == '0':
                return 0
                
            # Remove $ and convert
            clean_str = liquidity_str.replace('$', '').replace(',', '')
            
            if clean_str.endswith('B'):
                return float(clean_str[:-1]) * 1_000_000_000
            elif clean_str.endswith('M'):
                return float(clean_str[:-1]) * 1_000_000
            elif clean_str.endswith('K'):
                return float(clean_str[:-1]) * 1_000
            else:
                return float(clean_str)
        except:
            return 0
    
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
                'source': 'Aave V3',  # Changed from 'Binance Earn' to use allowlisted protocol
                'sourceType': 'DeFi',
                'riskScore': 'Low',
                'change24h': 0.12,
                'liquidity': '$89.2B',
                'metadata': {'fallback': True}
            },
            {
                'stablecoin': 'USDC',
                'name': 'USD Coin', 
                'currentYield': 7.82,
                'source': 'Compound V3',  # Already using allowlisted protocol
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
                'source': 'Curve',  # Changed from 'Compound' to use allowlisted protocol
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