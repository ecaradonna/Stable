from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from models.index_models import IndexValue, IndexHistoryQuery
from services.index_storage import IndexStorageService
from services.index_scheduler import get_scheduler_instance
from database import get_database

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/index", tags=["StableYield Index"])

async def get_index_storage():
    """Dependency to get index storage service"""
    db = await get_database()
    return IndexStorageService(db)

@router.get("/current", response_model=IndexValue)
async def get_current_index(storage: IndexStorageService = Depends(get_index_storage)):
    """
    Get the current StableYield Index value
    
    Returns the most recent calculated index value with all constituent data
    """
    try:
        current_index = await storage.get_latest_index_value()
        
        if not current_index:
            raise HTTPException(status_code=404, detail="No index data available")
        
        return current_index
        
    except Exception as e:
        logger.error(f"Error retrieving current index: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve current index")

@router.get("/history", response_model=List[IndexValue])
async def get_index_history(
    start_date: Optional[datetime] = Query(None, description="Start date for historical data"),
    end_date: Optional[datetime] = Query(None, description="End date for historical data"),
    interval: str = Query("1m", description="Data interval: 1m, 5m, 15m, 1h, 1d"),
    limit: Optional[int] = Query(1000, description="Maximum number of records to return"),
    storage: IndexStorageService = Depends(get_index_storage)
):
    """
    Get historical StableYield Index values
    
    Query parameters:
    - start_date: ISO format datetime (optional)
    - end_date: ISO format datetime (optional) 
    - interval: Data granularity (1m, 5m, 15m, 1h, 1d)
    - limit: Maximum records to return (default: 1000)
    """
    try:
        query = IndexHistoryQuery(
            start_date=start_date,
            end_date=end_date,
            interval=interval,
            limit=limit
        )
        
        history = await storage.get_index_history(query)
        
        logger.info(f"Retrieved {len(history)} historical index values")
        return history
        
    except Exception as e:
        logger.error(f"Error retrieving index history: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve index history")

@router.get("/statistics")
async def get_index_statistics(
    days: int = Query(30, description="Number of days for statistical analysis"),
    storage: IndexStorageService = Depends(get_index_storage)
):
    """
    Get statistical summary of StableYield Index performance
    
    Returns statistics for the specified time period including:
    - Average, min, max values
    - Data point count
    - Volatility measures
    """
    try:
        stats = await storage.get_index_statistics(days=days)
        return stats
        
    except Exception as e:
        logger.error(f"Error calculating index statistics: {e}")
        raise HTTPException(status_code=500, detail="Failed to calculate statistics")

@router.get("/constituents")
async def get_current_constituents(storage: IndexStorageService = Depends(get_index_storage)):
    """
    Get current index constituents with their weights and metrics
    
    Returns detailed information about each stablecoin in the index
    """
    try:
        current_index = await storage.get_latest_index_value()
        
        if not current_index:
            raise HTTPException(status_code=404, detail="No index data available")
        
        constituents = []
        for constituent in current_index.constituents:
            constituents.append({
                "symbol": constituent.symbol,
                "name": constituent.name,
                "weight": constituent.weight,
                "market_cap": constituent.market_cap,
                "raw_apy": constituent.raw_apy,
                "ray": constituent.ray,
                "peg_score": constituent.peg_score,
                "liquidity_score": constituent.liquidity_score,
                "counterparty_score": constituent.counterparty_score,
                "last_updated": constituent.last_updated
            })
        
        return {
            "index_value": current_index.value,
            "timestamp": current_index.timestamp,
            "constituents": constituents,
            "total_constituents": len(constituents)
        }
        
    except Exception as e:
        logger.error(f"Error retrieving constituents: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve constituents")

@router.get("/live")
async def get_live_ticker(storage: IndexStorageService = Depends(get_index_storage)):
    """
    Get live ticker data for frontend display
    
    Returns simplified index data optimized for real-time display
    """
    try:
        current_index = await storage.get_latest_index_value()
        
        if not current_index:
            # Return fallback data if no index available
            return {
                "value": 0.0,
                "timestamp": datetime.utcnow(),
                "status": "calculating",
                "constituents_count": 0
            }
        
        # Calculate time since last update
        time_diff = datetime.utcnow() - current_index.timestamp
        is_stale = time_diff.total_seconds() > 300  # 5 minutes
        
        return {
            "value": current_index.value,
            "timestamp": current_index.timestamp,
            "status": "stale" if is_stale else "live",
            "constituents_count": len(current_index.constituents),
            "last_update_seconds": int(time_diff.total_seconds())
        }
        
    except Exception as e:
        logger.error(f"Error retrieving live ticker: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve live ticker")

@router.post("/calculate")
async def force_calculation():
    """
    Force an immediate index calculation (admin/debugging endpoint)
    
    Triggers a manual calculation outside the regular schedule
    """
    try:
        db = await get_database()
        scheduler = await get_scheduler_instance(db)
        
        result = await scheduler.force_calculation()
        
        if result:
            return {
                "success": True,
                "message": "Index calculation completed",
                "value": result.value,
                "timestamp": result.timestamp
            }
        else:
            raise HTTPException(status_code=500, detail="Index calculation failed")
            
    except Exception as e:
        logger.error(f"Error in forced calculation: {e}")
        raise HTTPException(status_code=500, detail="Failed to calculate index")

@router.get("/status")
async def get_scheduler_status():
    """
    Get index calculation scheduler status
    
    Returns information about the background calculation service
    """
    try:
        db = await get_database()
        scheduler = await get_scheduler_instance(db)
        
        status = await scheduler.get_scheduler_status()
        return status
        
    except Exception as e:
        logger.error(f"Error retrieving scheduler status: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve status")

# TODO: PRODUCTION UPGRADES NEEDED
# 1. Add authentication for admin endpoints (/calculate, /status)
# 2. Implement rate limiting for public endpoints
# 3. Add response caching for frequently accessed data
# 4. Add WebSocket endpoint for real-time streaming
# 5. Implement proper error handling and status codes
# 6. Add request validation and sanitization