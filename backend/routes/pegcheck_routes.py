"""
API Routes for PegCheck Integration in StableYield
Integrates stablecoin peg monitoring into the main StableYield API
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
import sys
import os

# Add pegcheck to Python path
pegcheck_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'pegcheck')
if pegcheck_path not in sys.path:
    sys.path.append(os.path.dirname(pegcheck_path))

try:
    from pegcheck.core.compute import compute_peg_analysis
    from pegcheck.core.config import DEFAULT_SYMBOLS
    from pegcheck.sources import coingecko, cryptocompare
    PEGCHECK_AVAILABLE = True
except ImportError as e:
    logging.warning(f"PegCheck module not available: {e}")
    PEGCHECK_AVAILABLE = False

from pydantic import BaseModel

router = APIRouter(prefix="/api/peg", tags=["Peg Monitoring"])
logger = logging.getLogger(__name__)

class PegCheckResponse(BaseModel):
    """Response model for peg check operations"""
    success: bool
    data: Dict[str, Any]
    message: str
    timestamp: str

class PegSummaryResponse(BaseModel):
    """Response model for peg summary"""
    success: bool
    summary: Dict[str, Any]
    timestamp: str

async def check_pegcheck_availability():
    """Dependency to check if PegCheck is available"""
    if not PEGCHECK_AVAILABLE:
        raise HTTPException(
            status_code=503, 
            detail="PegCheck module not available. Please check installation."
        )

@router.get("/health")
async def peg_health_check():
    """Health check for peg monitoring system"""
    try:
        status = "available" if PEGCHECK_AVAILABLE else "unavailable"
        
        if PEGCHECK_AVAILABLE:
            # Test basic functionality
            test_symbols = ["USDT", "USDC"]
            cg_prices = coingecko.fetch(test_symbols)
            cc_prices = cryptocompare.fetch(test_symbols)
            
            valid_cg = sum(1 for price in cg_prices.values() if price == price and price > 0)
            valid_cc = sum(1 for price in cc_prices.values() if price == price and price > 0)
            
            api_status = {
                "coingecko": f"{valid_cg}/{len(test_symbols)} symbols",
                "cryptocompare": f"{valid_cc}/{len(test_symbols)} symbols"
            }
        else:
            api_status = {"error": "PegCheck module not loaded"}
        
        return {
            "service": "pegcheck",
            "status": status,
            "api_status": api_status,
            "timestamp": datetime.utcnow().isoformat(),
            "available_symbols": DEFAULT_SYMBOLS if PEGCHECK_AVAILABLE else []
        }
        
    except Exception as e:
        logger.error(f"Peg health check failed: {e}")
        return {
            "service": "pegcheck",
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@router.get("/check", response_model=PegCheckResponse)
async def check_peg_stability(
    symbols: str = Query(
        default="USDT,USDC,DAI",
        description="Comma-separated list of symbols to check"
    ),
    _: None = Depends(check_pegcheck_availability)
):
    """
    Check peg stability for specified stablecoins
    
    Analyzes peg deviation from $1.00 using multiple data sources:
    - CoinGecko (primary CeFi reference)  
    - CryptoCompare (secondary CeFi reference)
    
    Returns detailed analysis including deviation in basis points,
    peg status (normal/warning/depeg), and cross-source consistency.
    """
    try:
        # Parse symbols
        symbol_list = [s.strip().upper() for s in symbols.split(',') if s.strip()]
        if not symbol_list:
            raise HTTPException(status_code=400, detail="No valid symbols provided")
        
        if len(symbol_list) > 10:
            raise HTTPException(status_code=400, detail="Maximum 10 symbols allowed")
        
        logger.info(f"Checking peg stability for symbols: {symbol_list}")
        
        # Fetch data from sources
        cg_prices = coingecko.fetch(symbol_list)
        cc_prices = cryptocompare.fetch(symbol_list)
        
        # Compute peg analysis
        payload = compute_peg_analysis(
            coingecko_prices=cg_prices,
            cryptocompare_prices=cc_prices,
            symbols=symbol_list
        )
        
        # Format response
        response_data = {
            "analysis": {
                "timestamp": payload.as_of,
                "symbols_analyzed": len(payload.symbols),
                "depegs_detected": payload.total_depegs,
                "max_deviation_bps": payload.max_deviation_bps
            },
            "results": [
                {
                    "symbol": r.symbol,
                    "price_usd": round(r.avg_ref, 6) if r.avg_ref == r.avg_ref else None,
                    "deviation": {
                        "absolute": round(r.abs_diff, 6) if r.abs_diff == r.abs_diff else None,
                        "percentage": round(r.pct_diff, 4) if r.pct_diff == r.pct_diff else None,
                        "basis_points": round(r.bps_diff, 1) if r.bps_diff == r.bps_diff else None
                    },
                    "peg_status": r.status.value,
                    "is_depegged": r.is_depeg,
                    "confidence": round(r.confidence, 2),
                    "sources_used": r.sources_used,
                    "source_prices": {
                        "coingecko": round(cg_prices.get(r.symbol, float('nan')), 6),
                        "cryptocompare": round(cc_prices.get(r.symbol, float('nan')), 6)
                    }
                } for r in payload.reports
            ],
            "source_consistency": {
                symbol: round(consistency, 3) if consistency == consistency else None 
                for symbol, consistency in payload.cefi_consistency.items()
            },
            "configuration": payload.config
        }
        
        return PegCheckResponse(
            success=True,
            data=response_data,
            message=f"Peg analysis completed for {len(symbol_list)} symbols",
            timestamp=datetime.utcnow().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in peg check: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Peg check failed: {str(e)}"
        )

@router.get("/summary", response_model=PegSummaryResponse)
async def get_peg_summary(
    _: None = Depends(check_pegcheck_availability)
):
    """
    Get summary of peg stability for major stablecoins
    
    Provides quick overview of peg status for top stablecoins
    including any current depegs and market consistency.
    """
    try:
        # Use top 6 stablecoins for summary
        symbols = ["USDT", "USDC", "DAI", "BUSD", "FRAX", "USDP"]
        
        logger.info("Generating peg stability summary")
        
        # Fetch data
        cg_prices = coingecko.fetch(symbols)
        cc_prices = cryptocompare.fetch(symbols)
        
        # Compute analysis
        payload = compute_peg_analysis(
            coingecko_prices=cg_prices,
            cryptocompare_prices=cc_prices,
            symbols=symbols
        )
        
        # Count by status
        status_counts = {"normal": 0, "warning": 0, "depeg": 0}
        for report in payload.reports:
            if report.avg_ref == report.avg_ref:  # Valid price
                status_counts[report.status.value] += 1
        
        # Find worst deviation
        worst_deviation = max([r for r in payload.reports if r.bps_diff == r.bps_diff], 
                             key=lambda x: x.bps_diff, default=None)
        
        # Calculate average consistency
        valid_consistencies = [c for c in payload.cefi_consistency.values() if c == c]
        avg_consistency = sum(valid_consistencies) / len(valid_consistencies) if valid_consistencies else 0
        
        summary = {
            "overview": {
                "total_symbols": len([r for r in payload.reports if r.avg_ref == r.avg_ref]),
                "status_distribution": status_counts,
                "total_depegs": payload.total_depegs,
                "market_health": "healthy" if payload.total_depegs == 0 else "warning" if payload.total_depegs < 2 else "critical"
            },
            "key_metrics": {
                "max_deviation_bps": round(payload.max_deviation_bps, 1),
                "avg_source_consistency": round(avg_consistency, 3),
                "worst_performer": {
                    "symbol": worst_deviation.symbol if worst_deviation else None,
                    "deviation_bps": round(worst_deviation.bps_diff, 1) if worst_deviation else 0,
                    "status": worst_deviation.status.value if worst_deviation else "normal"
                } if worst_deviation else None
            },
            "alerts": [
                {
                    "symbol": r.symbol,
                    "status": r.status.value,
                    "deviation_bps": round(r.bps_diff, 1),
                    "price": round(r.avg_ref, 6)
                }
                for r in payload.reports 
                if r.status.value in ["warning", "depeg"] and r.avg_ref == r.avg_ref
            ],
            "data_quality": {
                "coingecko_coverage": sum(1 for price in cg_prices.values() if price == price),
                "cryptocompare_coverage": sum(1 for price in cc_prices.values() if price == price),
                "total_symbols": len(symbols)
            }
        }
        
        return PegSummaryResponse(
            success=True,
            summary=summary,
            timestamp=datetime.utcnow().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating peg summary: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Peg summary failed: {str(e)}"
        )

@router.get("/symbols")
async def get_supported_symbols(
    _: None = Depends(check_pegcheck_availability)
):
    """Get list of supported stablecoin symbols for peg monitoring"""
    return {
        "supported_symbols": DEFAULT_SYMBOLS,
        "total_count": len(DEFAULT_SYMBOLS),
        "categories": {
            "major": ["USDT", "USDC", "DAI", "BUSD"],
            "algorithmic": ["FRAX", "USDP"], 
            "other": ["TUSD", "PYUSD"]
        },
        "description": "Stablecoins supported for peg monitoring analysis"
    }

@router.get("/thresholds")
async def get_peg_thresholds():
    """Get peg monitoring thresholds and configuration"""
    try:
        if PEGCHECK_AVAILABLE:
            from pegcheck.core.config import DEPEG_THRESHOLD_BPS, WARNING_THRESHOLD_BPS
            
            return {
                "thresholds": {
                    "warning": {
                        "basis_points": WARNING_THRESHOLD_BPS,
                        "percentage": WARNING_THRESHOLD_BPS / 100,
                        "description": "Price deviation that triggers warning status"
                    },
                    "depeg": {
                        "basis_points": DEPEG_THRESHOLD_BPS,
                        "percentage": DEPEG_THRESHOLD_BPS / 100,
                        "description": "Price deviation that indicates depeg event"
                    }
                },
                "methodology": {
                    "target_price": 1.00,
                    "primary_source": "coingecko",
                    "secondary_source": "cryptocompare",
                    "weighting": "70% CoinGecko, 30% CryptoCompare"
                }
            }
        else:
            return {
                "error": "PegCheck module not available",
                "status": 503
            }
    except Exception as e:
        logger.error(f"Error getting thresholds: {e}")
        raise HTTPException(status_code=500, detail=str(e))