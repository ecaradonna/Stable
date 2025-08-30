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
backend_dir = os.path.dirname(os.path.dirname(__file__))  # /app/backend
app_dir = os.path.dirname(backend_dir)  # /app
pegcheck_path = os.path.join(app_dir, 'pegcheck')
if app_dir not in sys.path:
    sys.path.append(app_dir)

try:
    from pegcheck.core.compute import compute_peg_analysis
    from pegcheck.core.config import DEFAULT_SYMBOLS
    from pegcheck.sources import coingecko, cryptocompare, chainlink, uniswap
    from pegcheck.storage.memory import MemoryStorage
    
    # Try to import PostgreSQL storage, but make it optional
    try:
        from pegcheck.storage.postgres import PostgreSQLStorage
        POSTGRES_AVAILABLE = True
    except ImportError as e:
        logging.warning(f"PostgreSQL storage not available (asyncpg not installed): {e}")
        POSTGRES_AVAILABLE = False
        PostgreSQLStorage = None
    
    PEGCHECK_AVAILABLE = True
    
    # Initialize storage backend
    storage_backend = None
    POSTGRES_URL = os.getenv("POSTGRES_URL")
    if POSTGRES_URL and POSTGRES_AVAILABLE:
        try:
            storage_backend = PostgreSQLStorage(POSTGRES_URL)
            STORAGE_TYPE = "postgresql"
        except Exception as e:
            logging.warning(f"PostgreSQL storage failed, falling back to memory: {e}")
            storage_backend = MemoryStorage()
            STORAGE_TYPE = "memory"
    else:
        storage_backend = MemoryStorage()
        STORAGE_TYPE = "memory"
        
except ImportError as e:
    logging.warning(f"PegCheck module not available: {e}")
    PEGCHECK_AVAILABLE = False
    storage_backend = None
    STORAGE_TYPE = "none"

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
    with_oracle: bool = Query(
        default=False,
        description="Include Chainlink oracle data"
    ),
    with_dex: bool = Query(
        default=False,
        description="Include Uniswap v3 TWAP data"
    ),
    store_result: bool = Query(
        default=True,
        description="Store result in database for historical analysis"
    ),
    _: None = Depends(check_pegcheck_availability)
):
    """
    Check peg stability for specified stablecoins with enhanced data sources
    
    Analyzes peg deviation from $1.00 using multiple data sources:
    - CoinGecko (primary CeFi reference)  
    - CryptoCompare (secondary CeFi reference)
    - Chainlink Oracles (optional, requires ETH_RPC_URL)
    - Uniswap v3 TWAP (optional, requires ETH_RPC_URL)
    
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
        
        logger.info(f"Checking peg stability for symbols: {symbol_list} (oracle: {with_oracle}, dex: {with_dex})")
        
        # Fetch data from sources
        cg_prices = coingecko.fetch(symbol_list)
        cc_prices = cryptocompare.fetch(symbol_list)
        
        # Optional: Chainlink oracles
        chainlink_prices = None
        if with_oracle:
            try:
                chainlink_prices = chainlink.fetch(symbol_list)
                logger.info(f"Chainlink data fetched: {chainlink_prices}")
            except Exception as e:
                logger.warning(f"Chainlink fetch error: {e}")
                chainlink_prices = {symbol: float('nan') for symbol in symbol_list}
        
        # Optional: Uniswap v3 TWAP  
        uniswap_prices = None
        if with_dex:
            try:
                uniswap_prices = uniswap.fetch(symbol_list)
                logger.info(f"Uniswap data fetched: {uniswap_prices}")
            except Exception as e:
                logger.warning(f"Uniswap fetch error: {e}")
                uniswap_prices = {symbol: float('nan') for symbol in symbol_list}
        
        # Compute peg analysis
        payload = compute_peg_analysis(
            coingecko_prices=cg_prices,
            cryptocompare_prices=cc_prices,
            chainlink_prices=chainlink_prices,
            uniswap_prices=uniswap_prices,
            symbols=symbol_list
        )
        
        # Store result if requested and storage is available
        if store_result and storage_backend:
            try:
                await storage_backend.store_peg_check(payload)
                logger.info(f"Peg check result stored successfully")
            except Exception as e:
                logger.warning(f"Failed to store peg check result: {e}")
        
        # Format response with enhanced data sources
        source_prices = {
            "coingecko": {symbol: round(price, 6) if price == price else None for symbol, price in cg_prices.items()},
            "cryptocompare": {symbol: round(price, 6) if price == price else None for symbol, price in cc_prices.items()}
        }
        
        if chainlink_prices:
            source_prices["chainlink"] = {symbol: round(price, 6) if price == price else None for symbol, price in chainlink_prices.items()}
        
        if uniswap_prices:
            source_prices["uniswap"] = {symbol: round(price, 6) if price == price else None for symbol, price in uniswap_prices.items()}
        
        response_data = {
            "analysis": {
                "timestamp": payload.as_of,
                "symbols_analyzed": len(payload.symbols),
                "depegs_detected": payload.total_depegs,
                "max_deviation_bps": payload.max_deviation_bps,
                "data_sources_used": {
                    "coingecko": True,
                    "cryptocompare": True,
                    "chainlink": chainlink_prices is not None,
                    "uniswap": uniswap_prices is not None
                }
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
                    "sources_used": r.sources_used
                } for r in payload.reports
            ],
            "source_prices": source_prices,
            "source_consistency": {
                symbol: round(consistency, 3) if consistency == consistency else None 
                for symbol, consistency in payload.cefi_consistency.items()
            },
            "configuration": payload.config,
            "storage": {
                "stored": store_result and storage_backend is not None,
                "backend": STORAGE_TYPE
            }
        }
        
        return PegCheckResponse(
            success=True,
            data=response_data,
            message=f"Enhanced peg analysis completed for {len(symbol_list)} symbols using {len(source_prices)} data sources",
            timestamp=datetime.utcnow().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in enhanced peg check: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Enhanced peg check failed: {str(e)}"
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

@router.get("/sources")
async def get_data_sources(
    _: None = Depends(check_pegcheck_availability)
):
    """Get information about available data sources and their health"""
    try:
        # Check each source health
        sources_info = {}
        
        # CoinGecko health check
        try:
            test_result = coingecko.fetch(["USDT"])
            sources_info["coingecko"] = {
                "name": "CoinGecko",
                "type": "CeFi",
                "status": "healthy" if test_result.get("USDT", 0) > 0 else "degraded",
                "description": "Primary CeFi price reference"
            }
        except Exception as e:
            sources_info["coingecko"] = {
                "name": "CoinGecko", 
                "type": "CeFi",
                "status": "error",
                "error": str(e),
                "description": "Primary CeFi price reference"
            }
        
        # CryptoCompare health check
        try:
            test_result = cryptocompare.fetch(["USDT"])
            sources_info["cryptocompare"] = {
                "name": "CryptoCompare",
                "type": "CeFi", 
                "status": "healthy" if test_result.get("USDT", 0) > 0 else "degraded",
                "description": "Secondary CeFi price reference"
            }
        except Exception as e:
            sources_info["cryptocompare"] = {
                "name": "CryptoCompare",
                "type": "CeFi",
                "status": "error", 
                "error": str(e),
                "description": "Secondary CeFi price reference"
            }
        
        # Chainlink health check
        try:
            chainlink_health = chainlink.health_check()
            sources_info["chainlink"] = {
                "name": "Chainlink Oracles",
                "type": "Oracle",
                "status": chainlink_health["status"],
                "description": "On-chain price feeds",
                "configuration": chainlink_health.get("configured", False),
                "feeds_available": chainlink_health.get("feeds_available", 0)
            }
            if "error" in chainlink_health:
                sources_info["chainlink"]["error"] = chainlink_health["error"]
        except Exception as e:
            sources_info["chainlink"] = {
                "name": "Chainlink Oracles",
                "type": "Oracle", 
                "status": "error",
                "error": str(e),
                "description": "On-chain price feeds"
            }
        
        # Uniswap health check
        try:
            uniswap_health = uniswap.health_check()
            sources_info["uniswap"] = {
                "name": "Uniswap v3 TWAP",
                "type": "DEX",
                "status": uniswap_health["status"],
                "description": "Time-weighted average price from DEX",
                "configuration": uniswap_health.get("configured", False),
                "pools_available": uniswap_health.get("pools_available", 0)
            }
            if "error" in uniswap_health:
                sources_info["uniswap"]["error"] = uniswap_health["error"]
        except Exception as e:
            sources_info["uniswap"] = {
                "name": "Uniswap v3 TWAP",
                "type": "DEX",
                "status": "error", 
                "error": str(e),
                "description": "Time-weighted average price from DEX"
            }
        
        return {
            "data_sources": sources_info,
            "configuration": {
                "eth_rpc_configured": bool(os.getenv("ETH_RPC_URL")),
                "cryptocompare_api_configured": bool(os.getenv("CRYPTOCOMPARE_API_KEY")),
                "storage_backend": STORAGE_TYPE
            },
            "capabilities": {
                "cefi_monitoring": True,
                "oracle_monitoring": bool(os.getenv("ETH_RPC_URL")),
                "dex_monitoring": bool(os.getenv("ETH_RPC_URL")), 
                "historical_storage": storage_backend is not None
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting data sources info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{symbol}")
async def get_peg_history(
    symbol: str,
    hours: int = Query(default=24, ge=1, le=168, description="Hours of history to retrieve"),
    _: None = Depends(check_pegcheck_availability)
):
    """Get historical peg data for a symbol"""
    try:
        if not storage_backend:
            raise HTTPException(status_code=503, detail="Storage backend not available")
        
        symbol = symbol.upper()
        history = await storage_backend.get_peg_history(symbol, hours)
        
        if not history:
            return {
                "symbol": symbol,
                "hours_requested": hours,
                "data_points": 0,
                "history": [],
                "message": f"No historical data found for {symbol}"
            }
        
        # Format history data
        formatted_history = [
            {
                "timestamp": timestamp.isoformat(),
                "price_usd": price,
                "status": status,
                "deviation_bps": abs(price - 1.0) * 10000 if price > 0 else None
            }
            for timestamp, price, status in history
        ]
        
        return {
            "symbol": symbol,
            "hours_requested": hours,
            "data_points": len(formatted_history),
            "history": formatted_history,
            "summary": {
                "min_price": min(h["price_usd"] for h in formatted_history),
                "max_price": max(h["price_usd"] for h in formatted_history),
                "avg_price": sum(h["price_usd"] for h in formatted_history) / len(formatted_history),
                "max_deviation_bps": max(h["deviation_bps"] for h in formatted_history if h["deviation_bps"] is not None)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting peg history for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/storage/health")
async def get_storage_health():
    """Get storage backend health and statistics"""
    try:
        if not storage_backend:
            return {
                "status": "unavailable",
                "backend": "none",
                "error": "No storage backend configured"
            }
        
        health_info = await storage_backend.health_check()
        return health_info
        
    except Exception as e:
        logger.error(f"Error checking storage health: {e}")
        return {
            "status": "error",
            "backend": STORAGE_TYPE,
            "error": str(e)
        }

@router.get("/analytics/trends/{symbol}")
async def get_symbol_trends(
    symbol: str,
    hours: int = Query(default=168, ge=1, le=720, description="Hours of history to analyze"),
    _: None = Depends(check_pegcheck_availability)
):
    """Get trend analysis for a specific symbol"""
    try:
        if not storage_backend:
            raise HTTPException(status_code=503, detail="Storage backend not available for trend analysis")
        
        # Import trend analyzer
        from pegcheck.analytics.trend_analyzer import TrendAnalyzer
        
        analyzer = TrendAnalyzer(storage_backend)
        analysis = await analyzer.analyze_symbol_trends(symbol.upper(), hours)
        
        if not analysis:
            raise HTTPException(
                status_code=404,
                detail=f"Insufficient data for trend analysis of {symbol.upper()} (minimum 10 data points required)"
            )
        
        return {
            "symbol": analysis.symbol,
            "analysis_period_hours": analysis.analysis_period_hours,
            "data_points": analysis.data_points,
            "price_metrics": {
                "avg_price": round(analysis.avg_price, 6),
                "min_price": round(analysis.min_price, 6),
                "max_price": round(analysis.max_price, 6),
                "volatility": round(analysis.price_volatility, 6),
                "trend": analysis.price_trend
            },
            "deviation_metrics": {
                "avg_deviation_bps": round(analysis.avg_deviation_bps, 1),
                "max_deviation_bps": round(analysis.max_deviation_bps, 1),
                "deviation_episodes": analysis.deviation_episodes,
                "depeg_episodes": analysis.depeg_episodes,
                "trend": analysis.deviation_trend
            },
            "stability_metrics": {
                "time_in_normal": round(analysis.time_in_normal, 1),
                "time_in_warning": round(analysis.time_in_warning, 1),
                "time_in_depeg": round(analysis.time_in_depeg, 1),
                "risk_score": round(analysis.risk_score, 1),
                "stability_grade": analysis.stability_grade
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing trends for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/market-stability")
async def get_market_stability_report(
    symbols: str = Query(
        default="USDT,USDC,DAI,FRAX,BUSD",
        description="Comma-separated list of symbols to analyze"
    ),
    hours: int = Query(default=168, ge=1, le=720, description="Hours of history to analyze"),
    _: None = Depends(check_pegcheck_availability)
):
    """Get comprehensive market stability report"""
    try:
        if not storage_backend:
            raise HTTPException(status_code=503, detail="Storage backend not available for market analysis")
        
        # Parse symbols
        symbol_list = [s.strip().upper() for s in symbols.split(',') if s.strip()]
        if not symbol_list:
            raise HTTPException(status_code=400, detail="No valid symbols provided")
        
        # Import trend analyzer
        from pegcheck.analytics.trend_analyzer import TrendAnalyzer
        
        analyzer = TrendAnalyzer(storage_backend)
        report = await analyzer.get_market_stability_report(symbol_list, hours)
        
        if "error" in report:
            raise HTTPException(status_code=404, detail=report["error"])
        
        return report
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating market stability report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/jobs/run-peg-check")
async def run_manual_peg_check(
    store_result: bool = Query(default=True, description="Store result in database"),
    with_oracle: bool = Query(default=False, description="Include Chainlink data"),
    with_dex: bool = Query(default=False, description="Include Uniswap data"),
    _: None = Depends(check_pegcheck_availability)
):
    """Manually trigger a comprehensive peg check job"""
    try:
        if not storage_backend:
            raise HTTPException(status_code=503, detail="Storage backend not available")
        
        from pegcheck.jobs.scheduler import PegCheckScheduler
        
        scheduler = PegCheckScheduler(storage_backend, enable_oracle=with_oracle, enable_dex=with_dex)
        success = await scheduler.run_peg_check_job()
        
        if success:
            return {
                "success": True,
                "message": "Peg check job completed successfully",
                "timestamp": datetime.utcnow().isoformat(),
                "configuration": {
                    "oracle_enabled": with_oracle,
                    "dex_enabled": with_dex,
                    "result_stored": store_result
                }
            }
        else:
            raise HTTPException(status_code=500, detail="Peg check job failed")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error running manual peg check: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/jobs/cleanup")
async def run_data_cleanup(
    days_to_keep: int = Query(default=30, ge=7, le=365, description="Days of data to keep"),
    _: None = Depends(check_pegcheck_availability)
):
    """Manually trigger data cleanup job"""
    try:
        if not storage_backend:
            raise HTTPException(status_code=503, detail="Storage backend not available")
        
        deleted_count = await storage_backend.cleanup_old_data(days_to_keep)
        
        return {
            "success": True,
            "message": f"Data cleanup completed",
            "deleted_records": deleted_count,
            "days_kept": days_to_keep,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error running data cleanup: {e}")
        raise HTTPException(status_code=500, detail=str(e))