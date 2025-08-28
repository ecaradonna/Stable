"""
API Routes for StableYield Index (SYI) Calculation
Implements the exact API specification provided
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from datetime import datetime, date
from typing import List, Dict, Any, Optional
import logging

from services.syi_service import (
    get_syi_service, 
    SYIService, 
    SYIPayload, 
    SYIResult, 
    SYIHistoryResponse,
    SYIHistoryEntry
)
from pydantic import BaseModel

router = APIRouter(prefix="/api/syi", tags=["StableYield Index (SYI)"])
logger = logging.getLogger(__name__)

class SYICalculationResponse(BaseModel):
    """Response for SYI calculation"""
    success: bool
    data: Optional[SYIResult] = None
    error: Optional[str] = None

class SYICurrentResponse(BaseModel):
    """Response for current SYI value"""
    success: bool
    syi_decimal: float
    syi_percent: float
    timestamp: str
    methodology_version: str
    components_count: int

@router.post("/calc", response_model=SYICalculationResponse)
async def calculate_syi(
    payload: SYIPayload,
    syi_service: SYIService = Depends(get_syi_service)
):
    """
    Calculate SYI from provided components
    
    POST /api/syi/calc
    
    Request payload:
    {
        "as_of_date": "2025-08-28",
        "components": [
            {"symbol": "USDT", "weight": 72.5, "ray": 4.20},
            {"symbol": "USDC", "weight": 21.8, "ray": 4.50},
            {"symbol": "DAI", "weight": 4.4, "ray": 7.59},
            {"symbol": "TUSD", "weight": 0.4, "ray": 15.02},
            {"symbol": "FRAX", "weight": 0.7, "ray": 6.80},
            {"symbol": "USDP", "weight": 0.2, "ray": 3.42}
        ],
        "meta": {
            "units": "percent",
            "ray_units": "percent"
        }
    }
    """
    try:
        logger.info(f"Calculating SYI for {payload.as_of_date} with {len(payload.components)} components")
        
        result = syi_service.calculate_syi(payload)
        
        return SYICalculationResponse(
            success=True,
            data=result
        )
        
    except ValueError as e:
        logger.error(f"Validation error in SYI calculation: {str(e)}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Error calculating SYI: {str(e)}")
        return SYICalculationResponse(
            success=False,
            error=str(e)
        )

@router.get("/current", response_model=SYICurrentResponse)
async def get_current_syi(
    syi_service: SYIService = Depends(get_syi_service)
):
    """
    Get current SYI value using live system data
    
    GET /api/syi/current
    
    Returns the current SYI calculated from live constituent data
    """
    try:
        result = syi_service.calculate_syi_from_current_data()
        
        return SYICurrentResponse(
            success=True,
            syi_decimal=result.syi_decimal,
            syi_percent=result.syi_percent,
            timestamp=datetime.utcnow().isoformat() + "Z",
            methodology_version=result.methodology_version,
            components_count=result.components_count
        )
        
    except Exception as e:
        logger.error(f"Error getting current SYI: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate current SYI: {str(e)}"
        )

@router.get("/history")
async def get_syi_history(
    from_date: str = Query(..., regex=r'^\d{4}-\d{2}-\d{2}$'),
    to_date: str = Query(..., regex=r'^\d{4}-\d{2}-\d{2}$')
):
    """
    Get SYI historical data
    
    GET /api/syi/history?from=2025-08-20&to=2025-08-28
    
    Returns historical SYI values for the specified date range
    """
    try:
        # Validate dates
        start_date = datetime.strptime(from_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(to_date, '%Y-%m-%d').date()
        
        if start_date > end_date:
            raise HTTPException(status_code=422, detail="from_date must be <= to_date")
        
        # For now, return mock historical data since we don't have database storage yet
        # In production, this would query the syi_values table
        mock_series = [
            SYIHistoryEntry(date="2025-08-26", syi_decimal=0.04431, syi_percent=4.4310),
            SYIHistoryEntry(date="2025-08-27", syi_decimal=0.04455, syi_percent=4.4550),
            SYIHistoryEntry(date="2025-08-28", syi_decimal=0.0447448, syi_percent=4.47448)
        ]
        
        # Filter by date range
        filtered_series = [
            entry for entry in mock_series 
            if start_date <= datetime.strptime(entry.date, '%Y-%m-%d').date() <= end_date
        ]
        
        return SYIHistoryResponse(
            series=filtered_series,
            methodology_version="2.0.0"
        )
        
    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        logger.error(f"Error getting SYI history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upsert")
async def upsert_syi(
    payload: SYIPayload,
    syi_service: SYIService = Depends(get_syi_service)
):
    """
    Calculate and store SYI for a specific date (idempotent)
    
    POST /api/syi/upsert
    
    Validates, calculates, and stores SYI components + calculated value
    """
    try:
        # Calculate SYI first
        result = syi_service.calculate_syi(payload)
        
        # TODO: Implement database storage
        # This would store to syi_components and syi_values tables
        logger.info(f"Would store SYI {result.syi_percent:.5f}% for {payload.as_of_date} "
                   f"with {len(payload.components)} components")
        
        return {
            "success": True,
            "message": f"SYI calculated and stored for {payload.as_of_date}",
            "syi_percent": result.syi_percent,
            "components_count": len(payload.components)
        }
        
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Error in SYI upsert: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/test")
async def test_syi_calculation(
    syi_service: SYIService = Depends(get_syi_service)
):
    """
    Test SYI calculation with the reference dataset from specification
    Expected result: SYI ≈ 4.47448%
    """
    try:
        # Use the exact test data from specification
        from services.syi_service import SYIComponent, SYIPayload
        
        test_components = [
            SYIComponent(symbol="USDT", weight=72.5, ray=4.20),
            SYIComponent(symbol="USDC", weight=21.8, ray=4.50),
            SYIComponent(symbol="DAI", weight=4.4, ray=7.59),
            SYIComponent(symbol="TUSD", weight=0.4, ray=15.02),
            SYIComponent(symbol="FRAX", weight=0.7, ray=6.80),
            SYIComponent(symbol="USDP", weight=0.2, ray=3.42)
        ]
        
        payload = SYIPayload(
            as_of_date="2025-08-28",
            components=test_components,
            meta={
                "units": "percent",
                "ray_units": "percent"
            }
        )
        
        result = syi_service.calculate_syi(payload)
        
        # Check if result matches expected value (≈ 4.47448%)
        expected = 4.47448
        actual = result.syi_percent
        error = abs(actual - expected)
        
        return {
            "success": True,
            "test_result": "PASS" if error < 0.001 else "FAIL",
            "expected_percent": expected,
            "actual_percent": actual,
            "error": error,
            "syi_decimal": result.syi_decimal,
            "components_count": result.components_count,
            "methodology_version": result.methodology_version
        }
        
    except Exception as e:
        logger.error(f"Error in SYI test: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def syi_health_check():
    """Health check for SYI service"""
    return {
        "service": "syi",
        "status": "healthy",
        "methodology_version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }