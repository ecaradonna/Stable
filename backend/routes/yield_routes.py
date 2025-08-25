from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from typing import List, Dict, Any, Optional
from datetime import datetime
from models.yield_models import YieldData, HistoricalYield, User, WaitlistSignup, NewsletterSignup
from services.yield_aggregator import YieldAggregator
from services.liquidity_filter_service import LiquidityFilterService

router = APIRouter(prefix="/yields", tags=["Yields"])

# Initialize services
yield_aggregator = YieldAggregator()
liquidity_filter = LiquidityFilterService()

@router.get("/", response_model=List[YieldData])
async def get_all_yields(
    refresh: bool = False,
    min_tvl: Optional[float] = Query(default=None, description="Minimum TVL in USD", ge=0),
    min_volume: Optional[float] = Query(default=None, description="Minimum 24h volume in USD", ge=0),
    max_volatility: Optional[float] = Query(default=None, description="Maximum TVL volatility (0.0-1.0)", ge=0.0, le=1.0),
    grade_filter: Optional[str] = Query(default=None, description="Liquidity grade filter", regex="^(blue_chip|institutional|professional|retail)$"),
    institutional_only: bool = Query(default=False, description="Include only institutional-grade pools"),
    chain: Optional[str] = Query(default=None, description="Filter by blockchain"),
    asset: Optional[str] = Query(default=None, description="Filter by stablecoin asset")
):
    """Get current yields for all stablecoins with liquidity filtering"""
    try:
        # Get base yields
        yields_data = await yield_aggregator.get_all_yields(force_refresh=refresh)
        
        # Apply liquidity filtering
        if any([min_tvl, min_volume, max_volatility, grade_filter, institutional_only]):
            # Convert yields to pool format for filtering
            pools = []
            for yield_data in yields_data:
                pool = {
                    'tvl': float(yield_data.get('liquidity', '0').replace('$', '').replace('B', '000000000').replace('M', '000000').replace('K', '000').replace(',', '')),
                    'canonical_protocol_id': yield_data.get('source', '').lower().replace(' ', '_'),
                    'canonical_stablecoin_id': yield_data.get('stablecoin', ''),
                    'chain': yield_data.get('metadata', {}).get('chain', 'ethereum'),
                    'yield_data': yield_data
                }
                pools.append(pool)
            
            # Set institutional filter if requested
            actual_grade_filter = 'institutional' if institutional_only else grade_filter
            
            # Apply liquidity filtering
            filtered_pools = liquidity_filter.filter_pools_by_liquidity(
                pools, 
                min_tvl=min_tvl,
                min_volume=min_volume, 
                max_volatility=max_volatility,
                grade_filter=actual_grade_filter
            )
            
            # Extract yield data from filtered pools
            yields_data = [pool['yield_data'] for pool in filtered_pools]
        
        # Apply additional filters
        if chain:
            yields_data = [y for y in yields_data if y.get('metadata', {}).get('chain', 'ethereum').lower() == chain.lower()]
        
        if asset:
            yields_data = [y for y in yields_data if y.get('stablecoin', '').upper() == asset.upper()]
        
        # Convert to YieldData models
        yield_models = []
        for data in yields_data:
            yield_model = YieldData(
                stablecoin=data['stablecoin'],
                name=data['name'],
                currentYield=data['currentYield'],
                source=data['source'],
                sourceType=data['sourceType'],
                riskScore=data['riskScore'],
                change24h=data['change24h'],
                liquidity=data['liquidity'],
                metadata=data.get('metadata', {})
            )
            yield_models.append(yield_model)
        
        return yield_models
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch yields: {str(e)}")

@router.get("/{stablecoin}")
async def get_stablecoin_yield(stablecoin: str):
    """Get yield data for a specific stablecoin"""
    try:
        yield_data = await yield_aggregator.get_stablecoin_yield(stablecoin)
        
        if not yield_data:
            raise HTTPException(status_code=404, detail=f"Stablecoin {stablecoin} not found")
            
        return YieldData(**yield_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch yield data: {str(e)}")

@router.get("/{stablecoin}/history")
async def get_stablecoin_history(stablecoin: str, days: int = 7):
    """Get historical yield data for a specific stablecoin"""
    try:
        if days > 365:
            raise HTTPException(status_code=400, detail="Maximum 365 days of history allowed")
            
        historical_data = await yield_aggregator.get_historical_data(stablecoin, days)
        
        return {
            "stablecoin": stablecoin.upper(),
            "days": days,
            "data": historical_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch historical data: {str(e)}")

@router.post("/refresh")
async def refresh_yields(background_tasks: BackgroundTasks):
    """Manually refresh yield data (admin endpoint)"""
    try:
        background_tasks.add_task(yield_aggregator.refresh_cache)
        
        return {
            "message": "Yield data refresh initiated",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to refresh yields: {str(e)}")

@router.get("/stats/summary")
async def get_yield_summary():
    """Get summary statistics of all yields"""
    try:
        yields_data = await yield_aggregator.get_all_yields()
        
        if not yields_data:
            return {"message": "No yield data available"}
            
        yields = [data['currentYield'] for data in yields_data]
        
        summary = {
            "total_stablecoins": len(yields_data),
            "highest_yield": max(yields),
            "lowest_yield": min(yields),
            "average_yield": sum(yields) / len(yields),
            "cefi_count": len([d for d in yields_data if d['sourceType'] == 'CeFi']),
            "defi_count": len([d for d in yields_data if d['sourceType'] == 'DeFi']),
            "last_updated": datetime.utcnow().isoformat()
        }
        
        return summary
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate summary: {str(e)}")

@router.get("/compare/{coin1}/{coin2}")
async def compare_yields(coin1: str, coin2: str):
    """Compare yields between two stablecoins"""
    try:
        yield1 = await yield_aggregator.get_stablecoin_yield(coin1)
        yield2 = await yield_aggregator.get_stablecoin_yield(coin2)
        
        if not yield1:
            raise HTTPException(status_code=404, detail=f"Stablecoin {coin1} not found")
        if not yield2:
            raise HTTPException(status_code=404, detail=f"Stablecoin {coin2} not found")
            
        comparison = {
            "comparison": {
                coin1.upper(): yield1,
                coin2.upper(): yield2
            },
            "analysis": {
                "higher_yield": coin1.upper() if yield1['currentYield'] > yield2['currentYield'] else coin2.upper(),
                "yield_difference": abs(yield1['currentYield'] - yield2['currentYield']),
                "risk_comparison": {
                    coin1.upper(): yield1['riskScore'],
                    coin2.upper(): yield2['riskScore']
                }
            }
        }
        
        return comparison
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to compare yields: {str(e)}")