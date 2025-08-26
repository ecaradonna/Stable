"""
Risk-Adjusted Yield (RAY) Routes
API endpoints for RAY calculations and analysis
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
import logging
import statistics
from services.ray_calculator import RAYCalculator, RiskFactorType
from services.syi_compositor import SYICompositor
from services.yield_aggregator import YieldAggregator

logger = logging.getLogger(__name__)
router = APIRouter()
ray_calculator = RAYCalculator()
syi_compositor = SYICompositor()
yield_aggregator = YieldAggregator()

@router.get("/ray/methodology")
async def get_ray_methodology() -> Dict[str, Any]:
    """Get RAY calculation methodology and configuration"""
    try:
        return ray_calculator.get_ray_summary()
    except Exception as e:
        logger.error(f"Error getting RAY methodology: {e}")
        raise HTTPException(status_code=500, detail="Failed to get RAY methodology")

@router.post("/ray/calculate")
async def calculate_ray_single(
    apy: float = Query(description="Base APY to calculate RAY for"),
    stablecoin: str = Query(default="USDT", description="Stablecoin symbol"),
    protocol: str = Query(default="aave_v3", description="Protocol identifier"),
    tvl_usd: Optional[float] = Query(default=None, description="TVL in USD for liquidity scoring"),
    use_market_context: bool = Query(default=True, description="Use current market context")
) -> Dict[str, Any]:
    """Calculate RAY for a single yield input"""
    try:
        # Prepare yield data
        yield_data = {
            'currentYield': apy,
            'stablecoin': stablecoin,
            'canonical_stablecoin_id': stablecoin,
            'source': protocol,
            'canonical_protocol_id': protocol,
            'sourceType': 'DeFi',
            'tvl': tvl_usd or 50_000_000,
            'liquidity': f"${tvl_usd:,.0f}" if tvl_usd else "$50,000,000"
        }
        
        # Get market context if requested
        market_context = []
        if use_market_context:
            try:
                current_yields = await yield_aggregator.get_all_yields()
                market_context = current_yields[:10]  # Use up to 10 for context
            except:
                market_context = []
        
        # Calculate RAY
        ray_result = ray_calculator.calculate_ray(yield_data, market_context)
        
        return {
            'input': {
                'base_apy': apy,
                'stablecoin': stablecoin,
                'protocol': protocol,
                'tvl_usd': tvl_usd,
                'market_context_size': len(market_context)
            },
            'ray_result': {
                'base_apy': ray_result.base_apy,
                'risk_adjusted_yield': ray_result.risk_adjusted_yield,
                'risk_penalty': ray_result.risk_penalty,
                'confidence_score': ray_result.confidence_score,
                'risk_factors': {
                    'peg_stability_score': ray_result.risk_factors.peg_stability_score,
                    'liquidity_score': ray_result.risk_factors.liquidity_score,
                    'counterparty_score': ray_result.risk_factors.counterparty_score,
                    'protocol_reputation': ray_result.risk_factors.protocol_reputation,
                    'temporal_stability': ray_result.risk_factors.temporal_stability
                },
                'breakdown': ray_result.breakdown,
                'metadata': ray_result.metadata
            }
        }
    except Exception as e:
        logger.error(f"Error calculating RAY: {e}")
        raise HTTPException(status_code=500, detail="Failed to calculate RAY")

@router.get("/ray/market-analysis")
async def get_market_ray_analysis() -> Dict[str, Any]:
    """Get RAY analysis for current market yields"""
    try:
        # Get current yield data
        yields_data = await yield_aggregator.get_all_yields()
        
        if not yields_data:
            return {
                'message': 'No yield data available for RAY analysis',
                'analysis': {}
            }
        
        # Calculate RAY for all yields
        ray_results = ray_calculator.calculate_ray_batch(yields_data)
        
        # Analyze results
        analysis = {
            'total_yields_analyzed': len(ray_results),
            'ray_statistics': {
                'average_ray': statistics.mean([r.risk_adjusted_yield for r in ray_results]),
                'median_ray': statistics.median([r.risk_adjusted_yield for r in ray_results]),
                'min_ray': min([r.risk_adjusted_yield for r in ray_results]),
                'max_ray': max([r.risk_adjusted_yield for r in ray_results]),
                'average_risk_penalty': statistics.mean([r.risk_penalty for r in ray_results]),
                'average_confidence': statistics.mean([r.confidence_score for r in ray_results])
            },
            'quality_metrics': {
                'high_confidence_rate': len([r for r in ray_results if r.confidence_score > 0.80]) / len(ray_results),
                'low_risk_penalty_rate': len([r for r in ray_results if r.risk_penalty < 0.20]) / len(ray_results),
                'institutional_grade_rate': len([r for r in ray_results if r.confidence_score > 0.70 and r.risk_penalty < 0.30]) / len(ray_results)
            }
        }
        
        # Top RAY yields
        sorted_by_ray = sorted(ray_results, key=lambda x: x.risk_adjusted_yield, reverse=True)
        
        top_rays = []
        for i, result in enumerate(sorted_by_ray[:5]):
            corresponding_yield = yields_data[ray_results.index(result)]
            top_rays.append({
                'rank': i + 1,
                'stablecoin': corresponding_yield.get('stablecoin', 'Unknown'),
                'protocol': corresponding_yield.get('source', 'Unknown'),
                'base_apy': result.base_apy,
                'ray': result.risk_adjusted_yield,
                'risk_penalty': result.risk_penalty,
                'confidence_score': result.confidence_score
            })
        
        analysis['top_ray_yields'] = top_rays
        
        return {
            'analysis': analysis,
            'methodology_version': '2.0.0',
            'calculation_timestamp': ray_results[0].metadata['calculation_timestamp'] if ray_results else None
        }
        
    except Exception as e:
        logger.error(f"Error performing market RAY analysis: {e}")
        raise HTTPException(status_code=500, detail="Failed to perform market RAY analysis")

@router.get("/syi/composition")
async def get_syi_composition() -> Dict[str, Any]:
    """Get detailed SYI composition using RAY methodology"""
    try:
        # Get yield data
        yields_data = await yield_aggregator.get_all_yields()
        
        if not yields_data:
            return {
                'message': 'No yield data available for SYI composition',
                'composition': {}
            }
        
        # Calculate SYI composition
        syi_composition = syi_compositor.compose_syi(yields_data)
        
        # Format response
        response = {
            'index_value': syi_composition.index_value,
            'constituent_count': syi_composition.constituent_count,
            'total_weight': syi_composition.total_weight,
            'methodology_version': syi_composition.methodology_version,
            'calculation_timestamp': syi_composition.calculation_timestamp,
            'constituents': [
                {
                    'stablecoin': c.stablecoin,
                    'protocol': c.protocol,
                    'weight': c.weight,
                    'ray': c.ray,
                    'base_apy': c.base_apy,
                    'risk_penalty': c.risk_penalty,
                    'tvl_usd': c.tvl_usd,
                    'confidence_score': c.confidence_score,
                    'contribution_to_index': c.ray * c.weight
                }
                for c in syi_composition.constituents
            ],
            'quality_metrics': syi_composition.quality_metrics,
            'breakdown': syi_composition.breakdown
        }
        
        return response
        
    except Exception as e:
        logger.error(f"Error getting SYI composition: {e}")
        raise HTTPException(status_code=500, detail="Failed to get SYI composition")

@router.get("/syi/methodology")
async def get_syi_methodology() -> Dict[str, Any]:
    """Get SYI composition methodology"""
    try:
        return syi_compositor.get_syi_methodology()
    except Exception as e:
        logger.error(f"Error getting SYI methodology: {e}")
        raise HTTPException(status_code=500, detail="Failed to get SYI methodology")