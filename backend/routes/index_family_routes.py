"""
API Routes for StableYield Index Family
Exposes endpoints for SY100, SY-CeFi, SY-DeFi, SY-RPI
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from datetime import datetime, date, timedelta
from typing import Optional, List
import logging

from models.index_family import (
    IndexCode, IndexResponse, IndexSeriesResponse, IndexFamilyResponse,
    IndexConstituentsResponse, IndexFactsheetResponse, IndexValue,
    IndexSeries, IndexFamilyOverview, IndexFactsheet
)
from services.index_family_service import IndexFamilyService
from database import get_database

router = APIRouter(prefix="/api/v1/index-family", tags=["Index Family"])
logger = logging.getLogger(__name__)

async def get_index_family_service():
    """Dependency to get IndexFamilyService instance"""
    db = await get_database()
    return IndexFamilyService(db)

@router.get("/overview", response_model=IndexFamilyResponse)
async def get_index_family_overview(
    date: Optional[str] = Query(None, description="Date (YYYY-MM-DD), defaults to latest"),
    service: IndexFamilyService = Depends(get_index_family_service)
):
    """Get overview of all indices in the StableYield family"""
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d") if date else datetime.utcnow()
        
        overview = await service.get_index_family_overview(target_date)
        
        return IndexFamilyResponse(
            success=True,
            data=overview,
            message=f"Index family overview for {target_date.strftime('%Y-%m-%d')}"
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        logger.error(f"Error getting index family overview: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{index_code}", response_model=IndexResponse)
async def get_index_value(
    index_code: IndexCode,
    date: Optional[str] = Query(None, description="Date (YYYY-MM-DD), defaults to latest"),
    service: IndexFamilyService = Depends(get_index_family_service)
):
    """Get current or historical value for a specific index"""
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d") if date else datetime.utcnow()
        
        index_value = await service.get_index_value(index_code, target_date)
        
        if not index_value:
            raise HTTPException(
                status_code=404, 
                detail=f"No data found for {index_code.value} on or before {target_date.strftime('%Y-%m-%d')}"
            )
            
        return IndexResponse(
            success=True,
            data=index_value,
            message=f"{index_code.value} value for {index_value.date.strftime('%Y-%m-%d')}"
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting {index_code} value: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{index_code}/series", response_model=IndexSeriesResponse)
async def get_index_series(
    index_code: IndexCode,
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD), defaults to today"),
    service: IndexFamilyService = Depends(get_index_family_service)
):
    """Get time series data for a specific index"""
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d") if end_date else datetime.utcnow()
        
        if start_dt > end_dt:
            raise HTTPException(status_code=400, detail="Start date must be before end date")
            
        # Get series data
        series_data = await service.get_index_series(index_code, start_dt, end_dt)
        
        if not series_data:
            raise HTTPException(
                status_code=404,
                detail=f"No series data found for {index_code.value} between {start_date} and {end_date or 'today'}"
            )
            
        return IndexSeriesResponse(
            success=True,
            data=series_data,
            message=f"{index_code.value} series from {start_date} to {end_date or 'today'}"
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting {index_code} series: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{index_code}/constituents", response_model=IndexConstituentsResponse)
async def get_index_constituents(
    index_code: IndexCode,
    date: Optional[str] = Query(None, description="Date (YYYY-MM-DD), defaults to latest"),
    service: IndexFamilyService = Depends(get_index_family_service)
):
    """Get constituents and weights for a specific index"""
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d") if date else datetime.utcnow()
        
        constituents_data = await service.get_index_constituents(index_code, target_date)
        
        if not constituents_data:
            raise HTTPException(
                status_code=404,
                detail=f"No constituents data found for {index_code.value} on or before {target_date.strftime('%Y-%m-%d')}"
            )
            
        return IndexConstituentsResponse(
            success=True,
            data=constituents_data,
            message=f"{index_code.value} constituents for {constituents_data.date.strftime('%Y-%m-%d')}"
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting {index_code} constituents: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/calculate")
async def calculate_indices(
    date: Optional[str] = Query(None, description="Date to calculate (YYYY-MM-DD), defaults to today"),
    force: bool = Query(False, description="Force recalculation even if data exists"),
    service: IndexFamilyService = Depends(get_index_family_service)
):
    """Calculate all indices for a specific date (admin endpoint)"""
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d") if date else datetime.utcnow()
        
        # Check if calculation already exists and force is not set
        if not force:
            existing = await service.get_index_value(IndexCode.SY100, target_date)
            if existing and existing.date.date() == target_date.date():
                return {
                    "success": True,
                    "message": f"Indices for {target_date.strftime('%Y-%m-%d')} already exist. Use force=true to recalculate."
                }
        
        # Calculate all indices
        results = await service.calculate_daily_indices(target_date)
        
        return {
            "success": True,
            "data": {
                "date": target_date.strftime('%Y-%m-%d'),
                "calculated_indices": [code.value for code in results.keys()],
                "values": {code.value: result.value for code, result in results.items()}
            },
            "message": f"Successfully calculated {len(results)} indices for {target_date.strftime('%Y-%m-%d')}"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        logger.error(f"Error calculating indices: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error calculating indices: {str(e)}")

@router.get("/factsheet", response_model=IndexFactsheetResponse)
async def get_daily_factsheet(
    date: Optional[str] = Query(None, description="Date (YYYY-MM-DD), defaults to latest"),
    format: str = Query("json", description="Format: json or pdf"),
    service: IndexFamilyService = Depends(get_index_family_service)
):
    """Get daily factsheet for all indices"""
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d") if date else datetime.utcnow()
        
        factsheet = await service.generate_factsheet(target_date, format)
        
        if not factsheet:
            raise HTTPException(
                status_code=404,
                detail=f"No factsheet data available for {target_date.strftime('%Y-%m-%d')}"
            )
            
        return IndexFactsheetResponse(
            success=True,
            data=factsheet,
            message=f"Daily factsheet for {target_date.strftime('%Y-%m-%d')}"
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating factsheet: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Risk Premium Index specific endpoints
@router.get("/rpi/analysis")
async def get_rpi_analysis(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    service: IndexFamilyService = Depends(get_index_family_service)
):
    """Get Risk Premium Index analysis with regime detection"""
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d") if end_date else datetime.utcnow()
        
        analysis = await service.get_rpi_analysis(start_dt, end_dt)
        
        return {
            "success": True,
            "data": analysis,
            "message": f"RPI analysis from {start_date} to {end_date or 'today'}"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        logger.error(f"Error getting RPI analysis: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/health")
async def health_check(service: IndexFamilyService = Depends(get_index_family_service)):
    """Health check endpoint for index family service"""
    try:
        # Check if we can calculate indices for today
        today = datetime.utcnow()
        
        # Get latest values for each index
        health_status = {}
        for index_code in IndexCode:
            try:
                latest_value = await service.get_index_value(index_code, today)
                if latest_value:
                    age_hours = (today - latest_value.date).total_seconds() / 3600
                    health_status[index_code.value] = {
                        "status": "healthy" if age_hours < 48 else "stale",
                        "last_update": latest_value.date.isoformat(),
                        "age_hours": age_hours,
                        "confidence": latest_value.confidence
                    }
                else:
                    health_status[index_code.value] = {
                        "status": "no_data",
                        "last_update": None,
                        "age_hours": None,
                        "confidence": 0.0
                    }
            except Exception as e:
                health_status[index_code.value] = {
                    "status": "error",
                    "error": str(e),
                    "last_update": None,
                    "age_hours": None,
                    "confidence": 0.0
                }
        
        overall_status = "healthy"
        if any(status["status"] == "error" for status in health_status.values()):
            overall_status = "error"
        elif any(status["status"] == "stale" for status in health_status.values()):
            overall_status = "stale"
        elif any(status["status"] == "no_data" for status in health_status.values()):
            overall_status = "degraded"
            
        return {
            "success": True,
            "status": overall_status,
            "timestamp": today.isoformat(),
            "indices": health_status
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "success": False,
            "status": "error", 
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }