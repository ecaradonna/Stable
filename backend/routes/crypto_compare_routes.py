from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from models.crypto_compare_models import (
    StablecoinMetricsResponse, RiskAdjustedStrategy, 
    PegMetrics, LiquidityMetrics
)
from services.crypto_compare_service import CryptoCompareService
from services.yield_aggregator import YieldAggregator

router = APIRouter(prefix="/v1", tags=["Market Intelligence"])

# Initialize services
crypto_service = CryptoCompareService()
yield_aggregator = YieldAggregator()

@router.get("/stablecoins/metrics", response_model=StablecoinMetricsResponse)
async def get_stablecoin_metrics(
    symbol: str = Query(..., description="Stablecoin symbol (USDT, USDC, etc.)"),
    window: str = Query("1h", description="Time window for metrics")
):
    """Get comprehensive peg stability and liquidity metrics for a stablecoin"""
    try:
        symbol = symbol.upper()
        if symbol not in crypto_service.stablecoins:
            raise HTTPException(status_code=400, detail=f"Unsupported stablecoin: {symbol}")
        
        metrics = await crypto_service.get_comprehensive_metrics(symbol)
        
        return StablecoinMetricsResponse(
            symbol=metrics['symbol'],
            vw_price=metrics['vw_price'],
            peg_dev_bps=metrics['peg_dev_bps'],
            peg_vol_5m_bps=metrics['peg_vol_5m_bps'],
            liq_score=metrics['liq_score'],
            depth_usd={
                "10bps": metrics['depth_10bps_usd'],
                "20bps": metrics['depth_20bps_usd'],
                "50bps": metrics['depth_50bps_usd']
            },
            avg_spread_bps=metrics['avg_spread_bps'],
            asof=metrics['asof']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")

@router.get("/stablecoins/all-metrics")
async def get_all_stablecoins_metrics():
    """Get metrics for all supported stablecoins"""
    try:
        all_metrics = []
        
        for symbol in crypto_service.stablecoins:
            try:
                metrics = await crypto_service.get_comprehensive_metrics(symbol)
                all_metrics.append({
                    'symbol': symbol,
                    'peg_score': metrics['peg_score'],
                    'liq_score': metrics['liq_score'],
                    'peg_dev_bps': metrics['peg_dev_bps'],
                    'vw_price': metrics['vw_price']
                })
            except Exception as e:
                logger.warning(f"Failed to get metrics for {symbol}: {e}")
                continue
        
        return {
            'stablecoins': all_metrics,
            'count': len(all_metrics),
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get all metrics: {str(e)}")

@router.get("/strategies/risk-adjusted-yield")
async def get_risk_adjusted_yields(
    symbol: Optional[str] = Query(None, description="Filter by stablecoin symbol"),
    lookback: str = Query("30d", description="Lookback period"),
    min_capacity: int = Query(1000000, description="Minimum capacity in USD")
):
    """Get risk-adjusted yields for all strategies"""
    try:
        # Get yield data from existing aggregator
        yield_data = await yield_aggregator.get_all_yields()
        
        risk_adjusted_strategies = []
        
        for yield_item in yield_data:
            item_symbol = yield_item['stablecoin']
            
            # Filter by symbol if specified
            if symbol and item_symbol.upper() != symbol.upper():
                continue
            
            # Get risk metrics for this stablecoin
            try:
                metrics = await crypto_service.get_comprehensive_metrics(item_symbol)
                
                # Calculate risk-adjusted yield
                ry_apy = crypto_service.calculate_risk_adjusted_yield(
                    yield_item['currentYield'],
                    metrics['peg_score'],
                    metrics['liq_score']
                )
                
                # Determine risk tier
                risk_tier = "Low"
                if metrics['peg_score'] < 0.8 or metrics['liq_score'] < 0.6:
                    risk_tier = "Medium" 
                if metrics['peg_score'] < 0.6 or metrics['liq_score'] < 0.4:
                    risk_tier = "High"
                
                strategy = RiskAdjustedStrategy(
                    strategy_id=f"{yield_item['source']}_{item_symbol}",
                    platform=yield_item['source'],
                    symbol=item_symbol,
                    apy=yield_item['currentYield'],
                    ry_apy=ry_apy,
                    peg_score=metrics['peg_score'],
                    liq_score=metrics['liq_score'],
                    capacity_usd=float(yield_item.get('liquidity', '1000000').replace('$', '').replace('B', '000000000').replace('M', '000000').replace(',', '')),
                    lockup_days=0,  # Assume flexible for now
                    risk_tier=risk_tier
                )
                
                risk_adjusted_strategies.append(strategy)
                
            except Exception as e:
                logger.warning(f"Failed to calculate risk-adjusted yield for {item_symbol}: {e}")
                continue
        
        # Sort by risk-adjusted yield (highest first)
        risk_adjusted_strategies.sort(key=lambda x: x.ry_apy, reverse=True)
        
        return {
            'strategies': risk_adjusted_strategies,
            'count': len(risk_adjusted_strategies),
            'lookback': lookback,
            'min_capacity_usd': min_capacity,
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get risk-adjusted yields: {str(e)}")

@router.get("/peg-stability/ranking")
async def get_peg_stability_ranking():
    """Get stablecoins ranked by peg stability"""
    try:
        stability_ranking = []
        
        for symbol in crypto_service.stablecoins:
            try:
                metrics = await crypto_service.get_comprehensive_metrics(symbol)
                stability_ranking.append({
                    'symbol': symbol,
                    'peg_score': metrics['peg_score'],
                    'peg_dev_bps': metrics['peg_dev_bps'],
                    'peg_vol_5m_bps': metrics['peg_vol_5m_bps'],
                    'vw_price': metrics['vw_price']
                })
            except Exception as e:
                logger.warning(f"Failed to get peg metrics for {symbol}: {e}")
                continue
        
        # Sort by peg score (highest first)
        stability_ranking.sort(key=lambda x: x['peg_score'], reverse=True)
        
        return {
            'ranking': stability_ranking,
            'methodology': {
                'peg_score_formula': "1 - (|peg_dev_bps| / 50) - (vol_5m_bps / 100)",
                'data_source': "Volume-weighted average across top exchanges",
                'update_frequency': "Real-time (30s intervals)"
            },
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get peg ranking: {str(e)}")

@router.get("/liquidity/analysis")
async def get_liquidity_analysis(
    symbol: Optional[str] = Query(None, description="Filter by stablecoin symbol")
):
    """Get detailed liquidity analysis for stablecoins"""
    try:
        symbols_to_analyze = [symbol.upper()] if symbol else crypto_service.stablecoins
        
        liquidity_analysis = []
        
        for sym in symbols_to_analyze:
            try:
                metrics = await crypto_service.get_comprehensive_metrics(sym)
                
                liquidity_analysis.append({
                    'symbol': sym,
                    'liq_score': metrics['liq_score'],
                    'depth_analysis': {
                        'depth_10bps_usd': metrics['depth_10bps_usd'],
                        'depth_20bps_usd': metrics['depth_20bps_usd'], 
                        'depth_50bps_usd': metrics['depth_50bps_usd']
                    },
                    'spread_analysis': {
                        'avg_spread_bps': metrics['avg_spread_bps'],
                        'spread_tier': 'Tight' if metrics['avg_spread_bps'] < 5 else 'Wide'
                    },
                    'venues_covered': metrics['venues_covered'],
                    'liquidity_tier': (
                        'Excellent' if metrics['liq_score'] > 0.8 else
                        'Good' if metrics['liq_score'] > 0.6 else
                        'Fair' if metrics['liq_score'] > 0.4 else 'Poor'
                    )
                })
                
            except Exception as e:
                logger.warning(f"Failed to analyze liquidity for {sym}: {e}")
                continue
        
        return {
            'liquidity_analysis': liquidity_analysis,
            'methodology': {
                'liq_score_components': ["Depth at 10/20/50bps", "Average spread", "Venue coverage"],
                'weights': "40% depth_10bps, 40% depth_20bps, 20% spread_penalty",
                'data_source': "Top 5-8 exchanges per stablecoin"
            },
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get liquidity analysis: {str(e)}")

# Add logging import
import logging
logger = logging.getLogger(__name__)