"""
Liquidity Filter Service
Implements TVL and liquidity filtering rules for institutional-grade pool curation
"""

import yaml
import os
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
from enum import Enum
import statistics

logger = logging.getLogger(__name__)

class LiquidityGrade(Enum):
    BLUE_CHIP = "blue_chip"
    INSTITUTIONAL = "institutional"
    PROFESSIONAL = "professional"
    RETAIL = "retail"
    INSUFFICIENT = "insufficient"

@dataclass
class LiquidityMetrics:
    tvl_usd: float
    volume_24h: Optional[float]
    liquidity_depth: Optional[float]
    tvl_volatility_7d: Optional[float]
    tvl_volatility_30d: Optional[float]
    grade: LiquidityGrade
    meets_threshold: bool
    exclusion_reasons: List[str]

class LiquidityFilterService:
    def __init__(self):
        self.config = self._load_config()
        self.tvl_cache = {}
        self.volume_cache = {}
        self.last_config_refresh = datetime.utcnow()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load liquidity thresholds configuration"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), "../../config/liquidity_thresholds.yml")
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                logger.info(f"Loaded liquidity thresholds v{config.get('version', 'unknown')}")
                return config
        except Exception as e:
            logger.error(f"Failed to load liquidity thresholds: {e}")
            return self._get_fallback_config()
    
    def _get_fallback_config(self) -> Dict[str, Any]:
        """Fallback configuration when config file is unavailable"""
        return {
            "global_thresholds": {
                "absolute_minimum": 1_000_000,
                "institutional_minimum": 50_000_000,
                "blue_chip_minimum": 500_000_000
            },
            "chain_thresholds": {},
            "asset_thresholds": {},
            "stability_requirements": {
                "max_7d_volatility": 0.30,
                "max_30d_volatility": 0.50
            }
        }
    
    def refresh_config(self) -> bool:
        """Refresh configuration from file"""
        try:
            new_config = self._load_config()
            old_version = self.config.get('version', 'unknown')
            new_version = new_config.get('version', 'unknown')
            
            if old_version != new_version:
                logger.info(f"Liquidity config updated: {old_version} -> {new_version}")
                
            self.config = new_config
            self.tvl_cache.clear()
            self.volume_cache.clear()
            self.last_config_refresh = datetime.utcnow()
            return True
        except Exception as e:
            logger.error(f"Failed to refresh liquidity config: {e}")
            return False
    
    def get_tvl_threshold(self, 
                         chain: str = "ethereum", 
                         asset: str = "USDT", 
                         protocol: str = None,
                         grade: str = "minimum") -> float:
        """Get TVL threshold based on chain, asset, protocol, and grade"""
        
        # Start with global threshold
        global_thresholds = self.config.get('global_thresholds', {})
        base_threshold = global_thresholds.get(f"{grade}_minimum", global_thresholds.get("absolute_minimum", 1_000_000))
        
        # Apply chain-specific adjustments
        chain_thresholds = self.config.get('chain_thresholds', {})
        chain_config = chain_thresholds.get(chain.lower(), {})
        if chain_config:
            chain_threshold = chain_config.get(f"{grade}_tvl", chain_config.get("minimum_tvl", base_threshold))
            base_threshold = max(base_threshold, chain_threshold)
        
        # Apply asset-specific adjustments
        asset_thresholds = self.config.get('asset_thresholds', {})
        asset_config = asset_thresholds.get(asset.upper(), {})
        if asset_config:
            asset_threshold = asset_config.get(f"{grade}_tvl", asset_config.get("minimum_tvl", base_threshold))
            base_threshold = max(base_threshold, asset_threshold)
        
        # Apply protocol-specific adjustments
        if protocol:
            protocol_thresholds = self.config.get('protocol_thresholds', {})
            protocol_config = protocol_thresholds.get(protocol.lower(), {})
            if protocol_config:
                protocol_threshold = protocol_config.get(f"{grade}_pool_tvl", protocol_config.get("minimum_pool_tvl", base_threshold))
                base_threshold = max(base_threshold, protocol_threshold)
        
        return base_threshold
    
    def calculate_liquidity_metrics(self, pool: Dict[str, Any]) -> LiquidityMetrics:
        """Calculate comprehensive liquidity metrics for a pool"""
        
        tvl_usd = float(pool.get('tvl', pool.get('tvlUsd', 0)))
        volume_24h = self._extract_volume(pool)
        chain = pool.get('chain', 'ethereum').lower()
        asset = self._extract_primary_asset(pool)
        protocol = pool.get('canonical_protocol_id', pool.get('project', '')).lower()
        
        exclusion_reasons = []
        
        # Get threshold for different grades
        thresholds = {
            'minimum': self.get_tvl_threshold(chain, asset, protocol, 'minimum'),
            'institutional': self.get_tvl_threshold(chain, asset, protocol, 'institutional'),
            'blue_chip': self.get_tvl_threshold(chain, asset, protocol, 'blue_chip')
        }
        
        # Determine grade based on TVL
        grade = self._determine_liquidity_grade(tvl_usd, thresholds)
        
        # Check minimum threshold
        meets_threshold = tvl_usd >= thresholds['minimum']
        
        if not meets_threshold:
            exclusion_reasons.append(f"TVL ${tvl_usd:,.0f} below minimum ${thresholds['minimum']:,.0f}")
        
        # Check volume requirements if available
        if volume_24h is not None:
            volume_req = self._get_volume_requirement(asset, grade.value)
            if volume_24h < volume_req:
                exclusion_reasons.append(f"24h volume ${volume_24h:,.0f} below requirement ${volume_req:,.0f}")
                if grade != LiquidityGrade.INSUFFICIENT:
                    grade = LiquidityGrade.RETAIL  # Downgrade due to low volume
        
        # Check stability requirements (simulated for now)
        tvl_volatility_7d = self._estimate_tvl_volatility(pool, 7)
        tvl_volatility_30d = self._estimate_tvl_volatility(pool, 30)
        
        stability_config = self.config.get('stability_requirements', {})
        max_7d_vol = stability_config.get('max_7d_volatility', 0.30)
        max_30d_vol = stability_config.get('max_30d_volatility', 0.50)
        
        if tvl_volatility_7d and tvl_volatility_7d > max_7d_vol:
            exclusion_reasons.append(f"7d TVL volatility {tvl_volatility_7d:.1%} exceeds {max_7d_vol:.1%}")
            
        if tvl_volatility_30d and tvl_volatility_30d > max_30d_vol:
            exclusion_reasons.append(f"30d TVL volatility {tvl_volatility_30d:.1%} exceeds {max_30d_vol:.1%}")
        
        # Estimate liquidity depth
        liquidity_depth = self._estimate_liquidity_depth(pool)
        
        return LiquidityMetrics(
            tvl_usd=tvl_usd,
            volume_24h=volume_24h,
            liquidity_depth=liquidity_depth,
            tvl_volatility_7d=tvl_volatility_7d,
            tvl_volatility_30d=tvl_volatility_30d,
            grade=grade,
            meets_threshold=len(exclusion_reasons) == 0,
            exclusion_reasons=exclusion_reasons
        )
    
    def _determine_liquidity_grade(self, tvl_usd: float, thresholds: Dict[str, float]) -> LiquidityGrade:
        """Determine liquidity grade based on TVL"""
        if tvl_usd >= thresholds.get('blue_chip', 500_000_000):
            return LiquidityGrade.BLUE_CHIP
        elif tvl_usd >= thresholds.get('institutional', 50_000_000):
            return LiquidityGrade.INSTITUTIONAL
        elif tvl_usd >= thresholds.get('minimum', 1_000_000) * 5:  # 5x minimum for professional
            return LiquidityGrade.PROFESSIONAL
        elif tvl_usd >= thresholds.get('minimum', 1_000_000):
            return LiquidityGrade.RETAIL
        else:
            return LiquidityGrade.INSUFFICIENT
    
    def _extract_volume(self, pool: Dict[str, Any]) -> Optional[float]:
        """Extract 24h volume from pool data"""
        volume_fields = ['volume24h', 'volume_24h', 'dailyVolume', 'volume']
        for field in volume_fields:
            if field in pool and pool[field] is not None:
                try:
                    return float(pool[field])
                except (ValueError, TypeError):
                    continue
        return None
    
    def _extract_primary_asset(self, pool: Dict[str, Any]) -> str:
        """Extract primary stablecoin asset from pool"""
        # Try various fields that might contain the asset
        asset_fields = ['canonical_stablecoin_id', 'stablecoin', 'symbol', 'asset']
        for field in asset_fields:
            if field in pool and pool[field]:
                asset = str(pool[field]).upper()
                # Return first stablecoin found
                for stablecoin in ['USDT', 'USDC', 'DAI', 'TUSD', 'PYUSD', 'FRAX']:
                    if stablecoin in asset:
                        return stablecoin
        return 'USDT'  # Default fallback
    
    def _get_volume_requirement(self, asset: str, grade: str) -> float:
        """Get volume requirement based on asset and grade"""
        asset_config = self.config.get('asset_thresholds', {}).get(asset.upper(), {})
        volume_config = self.config.get('volume_requirements', {})
        
        if grade == 'blue_chip':
            return asset_config.get('daily_volume_minimum', volume_config.get('institutional_24h_volume', 10_000_000))
        elif grade == 'institutional':
            return asset_config.get('daily_volume_minimum', volume_config.get('institutional_24h_volume', 10_000_000))
        else:
            return volume_config.get('min_24h_volume', 1_000_000)
    
    def _estimate_tvl_volatility(self, pool: Dict[str, Any], days: int) -> Optional[float]:
        """Estimate TVL volatility (placeholder - would use historical data in production)"""
        # In production, this would calculate actual volatility from historical TVL data
        # For now, return a simulated volatility based on pool characteristics
        
        tvl = float(pool.get('tvl', 0))
        protocol = pool.get('canonical_protocol_id', '').lower()
        
        # Simulate volatility based on protocol maturity and TVL size
        if protocol in ['aave_v3', 'compound_v3']:
            base_volatility = 0.10  # 10% for mature protocols
        elif protocol in ['curve', 'uniswap_v3']:
            base_volatility = 0.15  # 15% for AMM protocols
        else:
            base_volatility = 0.25  # 25% for newer protocols
        
        # Adjust based on TVL size (larger pools are more stable)
        if tvl > 100_000_000:  # $100M+
            base_volatility *= 0.8
        elif tvl < 5_000_000:  # <$5M
            base_volatility *= 1.5
        
        # Add time factor
        if days == 7:
            return base_volatility * 0.7  # 7-day is lower than 30-day
        else:
            return base_volatility
    
    def _estimate_liquidity_depth(self, pool: Dict[str, Any]) -> Optional[float]:
        """Estimate liquidity depth (placeholder)"""
        # In production, this would query order book depth or AMM liquidity
        tvl = float(pool.get('tvl', 0))
        
        # Rough estimate: assume 20% of TVL is available as liquidity depth
        return tvl * 0.20
    
    def filter_pools_by_liquidity(self, 
                                pools: List[Dict[str, Any]], 
                                min_tvl: Optional[float] = None,
                                min_volume: Optional[float] = None,
                                max_volatility: Optional[float] = None,
                                grade_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Filter pools based on liquidity requirements"""
        
        filtered_pools = []
        stats = {
            'total_pools': len(pools),
            'filtered_pools': 0,
            'grade_distribution': {},
            'exclusion_reasons': {}
        }
        
        for pool in pools:
            metrics = self.calculate_liquidity_metrics(pool)
            
            # Apply filters
            should_include = True
            exclusion_reason = None
            
            # Minimum TVL filter
            if min_tvl and metrics.tvl_usd < min_tvl:
                should_include = False
                exclusion_reason = f"TVL ${metrics.tvl_usd:,.0f} < required ${min_tvl:,.0f}"
            
            # Minimum volume filter
            if should_include and min_volume and metrics.volume_24h:
                if metrics.volume_24h < min_volume:
                    should_include = False
                    exclusion_reason = f"Volume ${metrics.volume_24h:,.0f} < required ${min_volume:,.0f}"
            
            # Maximum volatility filter
            if should_include and max_volatility and metrics.tvl_volatility_7d:
                if metrics.tvl_volatility_7d > max_volatility:
                    should_include = False
                    exclusion_reason = f"Volatility {metrics.tvl_volatility_7d:.1%} > max {max_volatility:.1%}"
            
            # Grade filter
            if should_include and grade_filter:
                required_grades = {
                    'blue_chip': [LiquidityGrade.BLUE_CHIP],
                    'institutional': [LiquidityGrade.BLUE_CHIP, LiquidityGrade.INSTITUTIONAL],
                    'professional': [LiquidityGrade.BLUE_CHIP, LiquidityGrade.INSTITUTIONAL, LiquidityGrade.PROFESSIONAL],
                    'retail': [LiquidityGrade.BLUE_CHIP, LiquidityGrade.INSTITUTIONAL, LiquidityGrade.PROFESSIONAL, LiquidityGrade.RETAIL]
                }
                
                if grade_filter in required_grades:
                    if metrics.grade not in required_grades[grade_filter]:
                        should_include = False
                        exclusion_reason = f"Grade {metrics.grade.value} not in required {grade_filter}"
            
            # Check base requirements
            if should_include and not metrics.meets_threshold:
                should_include = False
                exclusion_reason = "; ".join(metrics.exclusion_reasons)
            
            # Track statistics
            grade_key = metrics.grade.value
            stats['grade_distribution'][grade_key] = stats['grade_distribution'].get(grade_key, 0) + 1
            
            if not should_include and exclusion_reason:
                stats['exclusion_reasons'][exclusion_reason] = stats['exclusion_reasons'].get(exclusion_reason, 0) + 1
            
            if should_include:
                # Enrich pool with liquidity information
                pool['liquidity_metrics'] = {
                    'tvl_usd': metrics.tvl_usd,
                    'volume_24h': metrics.volume_24h,
                    'liquidity_depth': metrics.liquidity_depth,
                    'tvl_volatility_7d': metrics.tvl_volatility_7d,
                    'liquidity_grade': metrics.grade.value,
                    'meets_all_requirements': metrics.meets_threshold
                }
                
                filtered_pools.append(pool)
                stats['filtered_pools'] += 1
        
        logger.info(f"Liquidity filtering results: {stats}")
        return filtered_pools
    
    def get_liquidity_summary(self) -> Dict[str, Any]:
        """Get summary of current liquidity configuration"""
        global_thresholds = self.config.get('global_thresholds', {})
        
        return {
            'config_version': self.config.get('version', 'unknown'),
            'last_refresh': self.last_config_refresh.isoformat(),
            'thresholds': {
                'absolute_minimum': global_thresholds.get('absolute_minimum', 1_000_000),
                'institutional_minimum': global_thresholds.get('institutional_minimum', 50_000_000),
                'blue_chip_minimum': global_thresholds.get('blue_chip_minimum', 500_000_000)
            },
            'supported_chains': list(self.config.get('chain_thresholds', {}).keys()),
            'supported_assets': list(self.config.get('asset_thresholds', {}).keys()),
            'supported_filters': self.config.get('api_parameters', {}).get('supported_params', [])
        }