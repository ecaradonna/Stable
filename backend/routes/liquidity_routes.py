"""
Liquidity Routes
API endpoints for liquidity and TVL filtering information
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
import logging
from services.liquidity_filter_service import LiquidityFilterService
from services.yield_aggregator import YieldAggregator

logger = logging.getLogger(__name__)
router = APIRouter()
liquidity_service = LiquidityFilterService()
yield_aggregator = YieldAggregator()

@router.get("/liquidity/summary")
async def get_liquidity_summary() -> Dict[str, Any]:
    """Get summary of liquidity filtering configuration"""
    try:
        return liquidity_service.get_liquidity_summary()
    except Exception as e:
        logger.error(f"Error getting liquidity summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to get liquidity summary")

@router.get("/liquidity/thresholds")
async def get_liquidity_thresholds(
    chain: Optional[str] = Query(default=None, description="Chain to get thresholds for"),
    asset: Optional[str] = Query(default=None, description="Asset to get thresholds for"),
    protocol: Optional[str] = Query(default=None, description="Protocol to get thresholds for")
) -> Dict[str, Any]:
    """Get TVL thresholds for specific chain/asset/protocol combination"""
    try:
        thresholds = {}
        grades = ['minimum', 'institutional', 'blue_chip']
        
        for grade in grades:
            threshold = liquidity_service.get_tvl_threshold(
                chain=chain or 'ethereum',
                asset=asset or 'USDT', 
                protocol=protocol,
                grade=grade
            )
            thresholds[f"{grade}_tvl"] = threshold
        
        return {
            'chain': chain or 'ethereum',
            'asset': asset or 'USDT',
            'protocol': protocol or 'any',
            'thresholds': thresholds,
            'currency': 'USD'
        }
    except Exception as e:
        logger.error(f"Error getting liquidity thresholds: {e}")
        raise HTTPException(status_code=500, detail="Failed to get liquidity thresholds")

@router.get("/liquidity/metrics/{pool_id}")
async def get_pool_liquidity_metrics(pool_id: str) -> Dict[str, Any]:
    """Get detailed liquidity metrics for a specific pool"""
    try:
        # This would typically fetch from database, for now simulate
        pool_data = {
            'pool_id': pool_id,
            'tvl': 25_000_000,  # $25M
            'volume_24h': 2_000_000,  # $2M
            'canonical_protocol_id': 'aave_v3',
            'canonical_stablecoin_id': 'USDC',
            'chain': 'ethereum'
        }
        
        metrics = liquidity_service.calculate_liquidity_metrics(pool_data)
        
        return {
            'pool_id': pool_id,
            'tvl_usd': metrics.tvl_usd,
            'volume_24h_usd': metrics.volume_24h,
            'liquidity_depth': metrics.liquidity_depth,
            'tvl_volatility_7d': metrics.tvl_volatility_7d,
            'tvl_volatility_30d': metrics.tvl_volatility_30d,
            'liquidity_grade': metrics.grade.value,
            'meets_threshold': metrics.meets_threshold,
            'exclusion_reasons': metrics.exclusion_reasons
        }
    except Exception as e:
        logger.error(f"Error getting pool liquidity metrics for {pool_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get liquidity metrics for pool {pool_id}")

@router.get("/pools/filter")
async def filter_pools_by_liquidity(
    min_tvl: Optional[float] = Query(default=None, description="Minimum TVL in USD", ge=0),
    min_volume: Optional[float] = Query(default=None, description="Minimum 24h volume in USD", ge=0),
    max_volatility: Optional[float] = Query(default=None, description="Maximum TVL volatility (0.0-1.0)", ge=0.0, le=1.0),
    grade_filter: Optional[str] = Query(default=None, description="Liquidity grade filter", regex="^(blue_chip|institutional|professional|retail)$"),
    chain: Optional[str] = Query(default=None, description="Filter by blockchain"),
    asset: Optional[str] = Query(default=None, description="Filter by stablecoin asset"),
    limit: int = Query(default=50, description="Maximum number of pools to return", ge=1, le=1000)
) -> Dict[str, Any]:
    """Filter and return pools based on liquidity criteria"""
    try:
        # Get yield data and convert to pools
        yields_data = await yield_aggregator.get_all_yields()
        
        pools = []
        for yield_data in yields_data:
            # Convert liquidity string to float (e.g., "$89.2B" -> 89_200_000_000)
            liquidity_str = yield_data.get('liquidity', '0')
            tvl = 0
            try:
                # Remove currency symbols and convert
                clean_str = liquidity_str.replace('$', '').replace(',', '')
                if 'B' in clean_str:
                    tvl = float(clean_str.replace('B', '')) * 1_000_000_000
                elif 'M' in clean_str:
                    tvl = float(clean_str.replace('M', '')) * 1_000_000
                elif 'K' in clean_str:
                    tvl = float(clean_str.replace('K', '')) * 1_000
                else:
                    tvl = float(clean_str)
            except:
                tvl = 0
            
            pool = {
                'pool_id': f"{yield_data['stablecoin']}_{yield_data['source'].replace(' ', '_')}",
                'stablecoin': yield_data['stablecoin'],
                'protocol': yield_data['source'],
                'chain': yield_data.get('metadata', {}).get('chain', 'ethereum'),
                'tvl': tvl,
                'apy': yield_data['currentYield'],
                'source_type': yield_data['sourceType'],
                'risk_score': yield_data['riskScore'],
                'canonical_protocol_id': yield_data['source'].lower().replace(' ', '_'),
                'canonical_stablecoin_id': yield_data['stablecoin']
            }
            pools.append(pool)
        
        # Apply chain filter
        if chain:
            pools = [p for p in pools if p['chain'].lower() == chain.lower()]
        
        # Apply asset filter
        if asset:
            pools = [p for p in pools if p['stablecoin'].upper() == asset.upper()]
        
        # Apply liquidity filtering
        filtered_pools = liquidity_service.filter_pools_by_liquidity(
            pools,
            min_tvl=min_tvl,
            min_volume=min_volume,
            max_volatility=max_volatility,
            grade_filter=grade_filter
        )
        
        # Limit results
        limited_pools = filtered_pools[:limit]
        
        return {
            'pools': limited_pools,
            'total_pools': len(filtered_pools),
            'returned_pools': len(limited_pools),
            'filters_applied': {
                'min_tvl': min_tvl,
                'min_volume': min_volume,
                'max_volatility': max_volatility,
                'grade_filter': grade_filter,
                'chain': chain,
                'asset': asset
            }
        }
    except Exception as e:
        logger.error(f"Error filtering pools by liquidity: {e}")
        raise HTTPException(status_code=500, detail="Failed to filter pools by liquidity")

@router.post("/liquidity/refresh")
async def refresh_liquidity_config() -> Dict[str, Any]:
    """Refresh liquidity configuration from file"""
    try:
        success = liquidity_service.refresh_config()
        
        if success:
            return {
                "status": "success",
                "message": "Liquidity configuration refreshed successfully",
                "summary": liquidity_service.get_liquidity_summary()
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to refresh liquidity configuration")
            
    except Exception as e:
        logger.error(f"Error refreshing liquidity config: {e}")
        raise HTTPException(status_code=500, detail="Failed to refresh liquidity configuration")

@router.get("/liquidity/stats")
async def get_liquidity_stats() -> Dict[str, Any]:
    """Get liquidity statistics across all pools"""
    try:
        # Get all yield data
        yields_data = await yield_aggregator.get_all_yields()
        
        # Convert to pools and calculate metrics
        all_metrics = []
        grade_counts = {}
        
        for yield_data in yields_data:
            pool = {
                'tvl': float(yield_data.get('liquidity', '0').replace('$', '').replace('B', '000000000').replace('M', '000000').replace('K', '000').replace(',', '')),
                'canonical_protocol_id': yield_data.get('source', '').lower().replace(' ', '_'),
                'canonical_stablecoin_id': yield_data.get('stablecoin', ''),
                'chain': yield_data.get('metadata', {}).get('chain', 'ethereum')
            }
            
            metrics = liquidity_service.calculate_liquidity_metrics(pool)
            all_metrics.append(metrics)
            
            grade = metrics.grade.value
            grade_counts[grade] = grade_counts.get(grade, 0) + 1
        
        # Calculate aggregate statistics
        total_tvl = sum(m.tvl_usd for m in all_metrics)
        avg_tvl = total_tvl / len(all_metrics) if all_metrics else 0
        
        # Find median TVL
        tvl_values = sorted([m.tvl_usd for m in all_metrics])
        median_tvl = tvl_values[len(tvl_values)//2] if tvl_values else 0
        
        return {
            'total_pools': len(all_metrics),
            'total_tvl_usd': total_tvl,
            'average_tvl_usd': avg_tvl,
            'median_tvl_usd': median_tvl,
            'grade_distribution': grade_counts,
            'pools_meeting_threshold': sum(1 for m in all_metrics if m.meets_threshold),
            'institutional_grade_pools': grade_counts.get('institutional', 0) + grade_counts.get('blue_chip', 0),
            'config_version': liquidity_service.config.get('version', 'unknown')
        }
    except Exception as e:
        logger.error(f"Error getting liquidity stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get liquidity statistics")