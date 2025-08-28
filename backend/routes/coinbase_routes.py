"""
API Routes for Coinbase Integration
Exposes endpoints for testing and monitoring Coinbase CeFi data integration
"""

from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from typing import Dict, List, Any
import logging

from services.coinbase_service import get_coinbase_service, CoinbaseYieldData
from pydantic import BaseModel

router = APIRouter(prefix="/api/coinbase", tags=["Coinbase Integration"])
logger = logging.getLogger(__name__)

class CoinbaseStatusResponse(BaseModel):
    """Response model for Coinbase service status"""
    status: str
    connected: bool
    api_configured: bool
    last_check: str
    message: str

class CoinbaseYieldResponse(BaseModel):
    """Response model for Coinbase yield data"""
    success: bool
    data: Dict[str, Any]
    message: str
    timestamp: str

@router.get("/status", response_model=CoinbaseStatusResponse)
async def get_coinbase_status():
    """Get Coinbase API connection status and configuration"""
    try:
        coinbase_service = get_coinbase_service()
        
        # Check if client is configured
        api_configured = coinbase_service.client is not None
        
        if api_configured:
            # Try a simple API call to test connection
            try:
                yield_data = await coinbase_service.get_account_balances()
                connected = len(yield_data) > 0
                status = "healthy" if connected else "configured_no_data"
                message = f"Connected successfully, found {len(yield_data)} yield-bearing accounts" if connected else "API configured but no yield data available"
            except Exception as e:
                connected = False
                status = "configured_error"
                message = f"API configured but connection failed: {str(e)}"
        else:
            connected = False
            status = "not_configured"
            message = "Coinbase API credentials not configured"
        
        return CoinbaseStatusResponse(
            status=status,
            connected=connected,
            api_configured=api_configured,
            last_check=datetime.utcnow().isoformat(),
            message=message
        )
        
    except Exception as e:
        logger.error(f"Error checking Coinbase status: {e}")
        return CoinbaseStatusResponse(
            status="error",
            connected=False,
            api_configured=False,
            last_check=datetime.utcnow().isoformat(),
            message=f"Status check failed: {str(e)}"
        )

@router.get("/yield-data", response_model=CoinbaseYieldResponse)
async def get_coinbase_yield_data():
    """Fetch current yield data from Coinbase API"""
    try:
        coinbase_service = get_coinbase_service()
        yield_data = await coinbase_service.get_account_balances()
        
        # Convert to serializable format
        serialized_data = [
            {
                "currency": item.currency,
                "balance": float(item.balance),
                "available_balance": float(item.available_balance),
                "annual_yield_rate": float(item.annual_yield_rate or 0),
                "yield_source": item.yield_source,
                "account_type": item.account_type,
                "last_updated": item.last_updated.isoformat()
            }
            for item in yield_data
        ]
        
        return CoinbaseYieldResponse(
            success=True,
            data={
                "yield_accounts": serialized_data,
                "total_accounts": len(yield_data),
                "data_source": "coinbase_api" if coinbase_service.client else "mock_data"
            },
            message=f"Successfully fetched {len(yield_data)} yield data entries",
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error fetching Coinbase yield data: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch Coinbase yield data: {str(e)}"
        )

@router.get("/cefi-index", response_model=CoinbaseYieldResponse)
async def get_coinbase_cefi_index():
    """Calculate CeFi index contribution from Coinbase data"""
    try:
        coinbase_service = get_coinbase_service()
        index_data = await coinbase_service.calculate_cefi_index_contribution()
        
        # Convert Decimal values to float for JSON serialization
        serialized_data = {
            "total_value_usd": float(index_data["total_value_usd"]),
            "weighted_yield": float(index_data["weighted_yield"]),
            "constituent_count": index_data["constituent_count"],
            "constituents": index_data["constituents"],
            "data_source": index_data.get("data_source", "unknown"),
            "last_updated": index_data.get("last_updated", datetime.utcnow().isoformat())
        }
        
        return CoinbaseYieldResponse(
            success=True,
            data=serialized_data,
            message=f"CeFi index calculated: {serialized_data['weighted_yield']:.2f}% weighted yield",
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error calculating Coinbase CeFi index: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate CeFi index: {str(e)}"
        )

@router.post("/refresh")
async def refresh_coinbase_data():
    """Trigger refresh of Coinbase data (useful for testing)"""
    try:
        coinbase_service = get_coinbase_service()
        
        # Force refresh by getting fresh data
        yield_data = await coinbase_service.get_account_balances()
        index_data = await coinbase_service.calculate_cefi_index_contribution()
        
        return {
            "success": True,
            "message": "Coinbase data refreshed successfully",
            "summary": {
                "yield_accounts": len(yield_data),
                "total_value_usd": float(index_data["total_value_usd"]),
                "weighted_yield": float(index_data["weighted_yield"])
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error refreshing Coinbase data: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to refresh Coinbase data: {str(e)}"
        )

@router.get("/health")
async def coinbase_health_check():
    """Health check endpoint for Coinbase integration"""
    try:
        coinbase_service = get_coinbase_service()
        
        health_data = {
            "service": "coinbase_integration",
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "api_configured": coinbase_service.client is not None,
            "credentials_present": bool(coinbase_service.api_key and coinbase_service.api_secret)
        }
        
        # Quick connectivity test
        try:
            yield_data = await coinbase_service.get_account_balances()
            health_data["connectivity"] = "ok"
            health_data["data_available"] = len(yield_data) > 0
        except Exception as e:
            health_data["connectivity"] = "error"
            health_data["error"] = str(e)
        
        return health_data
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "service": "coinbase_integration",
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }