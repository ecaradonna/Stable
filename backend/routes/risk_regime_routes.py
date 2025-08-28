"""
API Routes for Risk Regime Inversion Alert System
Exposes endpoints for regime evaluation, history, and management
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
import logging
import os
from motor.motor_asyncio import AsyncIOMotorClient

from services.risk_regime_service import (
    get_risk_regime_service, 
    RiskRegimeService,
    start_risk_regime_service
)
from models.regime_models import (
    RegimeEvaluationRequest, RegimeEvaluationResponse,
    RegimeUpsertRequest, RegimeUpsertResponse,
    RegimeHistoryResponse, RegimeHealthResponse, RegimeStatsResponse,
    RegimeState, AlertType, AlertLevel
)

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

router = APIRouter(prefix="/api/regime", tags=["Risk Regime Detection"])
logger = logging.getLogger(__name__)


@router.post("/evaluate", response_model=RegimeEvaluationResponse)
async def evaluate_regime(
    request: RegimeEvaluationRequest,
    regime_service: RiskRegimeService = Depends(lambda: get_risk_regime_service(db))
):
    """
    Evaluate risk regime for a specific date
    
    POST /api/regime/evaluate
    
    Calculates risk regime state based on:
    - SYI excess (SYI - T-Bill 3M)
    - EMA spreads and volatility normalization
    - Momentum analysis (7-day slope)
    - Breadth calculation across RAY components
    - Peg stress override mechanism
    
    Request payload:
    {
        "date": "2025-08-28",
        "syi": 0.0445,
        "tbill_3m": 0.0530,
        "components": [
            {"symbol": "USDT", "ray": 0.042},
            {"symbol": "USDC", "ray": 0.045},
            {"symbol": "DAI", "ray": 0.075}
        ],
        "peg_status": {"max_depeg_bps": 80, "agg_depeg_bps": 120}
    }
    
    Response includes:
    - Regime state (ON/OFF/OFF_OVERRIDE/NEU)
    - Technical signal indicators
    - Alert information for state changes
    - Persistence and cooldown information
    """
    try:
        logger.info(f"Evaluating risk regime for {request.date}")
        
        result = await regime_service.evaluate_regime(request)
        
        logger.info(f"Regime evaluation complete: {request.date} → {result.state.value}")
        return result
        
    except ValueError as e:
        logger.error(f"Validation error in regime evaluation: {str(e)}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Error evaluating regime: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Regime evaluation failed: {str(e)}")


@router.get("/current")
async def get_current_regime(
    regime_service: RiskRegimeService = Depends(lambda: get_risk_regime_service(db))
):
    """
    Get current regime state and latest indicators
    
    GET /api/regime/current
    
    Returns the most recent regime evaluation with:
    - Current state and days in state
    - Latest signal indicators
    - Active cooldown or override periods
    """
    try:
        # Get most recent evaluation
        history = await regime_service.get_regime_history(
            from_date=(datetime.now().date() - timedelta(days=7)).strftime('%Y-%m-%d'),
            to_date=datetime.now().date().strftime('%Y-%m-%d'),
            limit=1
        )
        
        if not history.series:
            return {
                "state": "NEU",
                "message": "No regime data available",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        
        latest = history.series[-1]
        
        return {
            "date": latest.date,
            "state": latest.state.value,
            "syi_excess": latest.syi_excess,
            "z_score": latest.z_score,
            "spread": latest.spread,
            "slope7": latest.slope7,
            "breadth_pct": latest.breadth_pct,
            "alert_type": latest.alert_type.value if latest.alert_type else None,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
    except Exception as e:
        logger.error(f"Error getting current regime: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get current regime: {str(e)}")


@router.get("/history", response_model=RegimeHistoryResponse)
async def get_regime_history(
    from_date: str = Query(..., pattern=r'^\d{4}-\d{2}-\d{2}$', description="Start date (YYYY-MM-DD)"),
    to_date: str = Query(..., pattern=r'^\d{4}-\d{2}-\d{2}$', description="End date (YYYY-MM-DD)"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of entries"),
    regime_service: RiskRegimeService = Depends(lambda: get_risk_regime_service(db))
):
    """
    Get historical regime data
    
    GET /api/regime/history?from=2025-08-20&to=2025-08-28&limit=100
    
    Returns time series of regime states and indicators:
    - Daily regime states (ON/OFF/OFF_OVERRIDE/NEU)
    - Technical indicators (SYI excess, z-score, spread, etc.)
    - Alert history for regime changes
    - Configurable date range and limit
    
    Query parameters:
    - from: Start date (YYYY-MM-DD)
    - to: End date (YYYY-MM-DD)
    - limit: Max entries (1-1000, default 100)
    """
    try:
        # Validate date range
        start_date = datetime.strptime(from_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(to_date, '%Y-%m-%d').date()
        
        if start_date > end_date:
            raise HTTPException(status_code=422, detail="from_date must be <= to_date")
        
        # Check reasonable date range (max 2 years)
        if (end_date - start_date).days > 730:
            raise HTTPException(status_code=422, detail="Date range too large (max 2 years)")
        
        logger.info(f"Getting regime history: {from_date} to {to_date}")
        
        result = await regime_service.get_regime_history(from_date, to_date, limit)
        
        logger.info(f"Retrieved {len(result.series)} regime history entries")
        return result
        
    except ValueError as e:
        logger.error(f"Date validation error: {str(e)}")
        raise HTTPException(status_code=422, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        logger.error(f"Error getting regime history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get regime history: {str(e)}")


@router.post("/upsert", response_model=RegimeUpsertResponse)
async def upsert_regime_data(
    request: RegimeUpsertRequest,
    regime_service: RiskRegimeService = Depends(lambda: get_risk_regime_service(db))
):
    """
    Calculate and store regime data for a specific date (idempotent)
    
    POST /api/regime/upsert
    
    Performs regime evaluation and stores results to database.
    Operation is idempotent - can be called multiple times for same date.
    
    Use cases:
    - Daily batch processing of regime calculations
    - Backfilling historical regime data
    - Recalculating regime for specific dates
    
    Request payload:
    {
        "date": "2025-08-28",
        "syi": 0.0445,
        "tbill_3m": 0.0530,
        "components": [...],
        "peg_status": {...},
        "force_recalculate": false
    }
    
    Response includes:
    - Calculated regime state
    - Whether new data was created or updated
    - Alert notification status
    """
    try:
        logger.info(f"Upserting regime data for {request.date}")
        
        result = await regime_service.upsert_regime_data(request)
        
        logger.info(f"Regime upsert complete: {request.date} → {result.state.value}")
        return result
        
    except ValueError as e:
        logger.error(f"Validation error in regime upsert: {str(e)}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Error upserting regime data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Regime upsert failed: {str(e)}")


@router.get("/stats", response_model=RegimeStatsResponse)
async def get_regime_statistics(
    regime_service: RiskRegimeService = Depends(lambda: get_risk_regime_service(db))
):
    """
    Get comprehensive regime statistics
    
    GET /api/regime/stats
    
    Returns aggregate statistics:
    - Total days with regime data
    - Days in each regime state (Risk-On, Risk-Off, Override)
    - Total number of regime flips
    - Average regime duration
    - Current state and duration
    - Historical flip analysis
    
    Useful for:
    - Dashboard summary widgets
    - Performance analytics
    - Regime behavior analysis
    """
    try:
        logger.info("Getting regime statistics")
        
        result = await regime_service.get_regime_stats()
        
        logger.info(f"Retrieved regime stats: {result.total_days} days, {result.total_flips} flips")
        return result
        
    except Exception as e:
        logger.error(f"Error getting regime stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get regime statistics: {str(e)}")


@router.get("/health", response_model=RegimeHealthResponse)
async def get_regime_health(
    regime_service: RiskRegimeService = Depends(lambda: get_risk_regime_service(db))
):
    """
    Health check for risk regime service
    
    GET /api/regime/health
    
    Returns service health information:
    - Service status and version
    - Configuration parameters
    - Last evaluation date
    - Total evaluations performed
    - Database connectivity status
    
    Used for monitoring and debugging
    """
    try:
        result = await regime_service.get_health_status()
        return result
        
    except Exception as e:
        logger.error(f"Error getting regime health: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@router.post("/test")
async def test_regime_calculation(
    regime_service: RiskRegimeService = Depends(lambda: get_risk_regime_service(db))
):
    """
    Test regime calculation with sample data
    
    POST /api/regime/test
    
    Performs regime evaluation using predefined test dataset.
    Useful for:
    - Validating calculation algorithms
    - Testing system functionality
    - Debugging regime logic
    
    Returns evaluation results with test data indicators.
    """
    try:
        # Sample test data
        from models.regime_models import RegimeComponent, PegStatus
        
        test_request = RegimeEvaluationRequest(
            date="2025-08-28",
            syi=0.0445,
            tbill_3m=0.0530,
            components=[
                RegimeComponent(symbol="USDT", ray=0.042),
                RegimeComponent(symbol="USDC", ray=0.045),
                RegimeComponent(symbol="DAI", ray=0.075),
                RegimeComponent(symbol="TUSD", ray=0.055),
                RegimeComponent(symbol="FRAX", ray=0.068)
            ],
            peg_status=PegStatus(max_depeg_bps=80, agg_depeg_bps=120)
        )
        
        result = await regime_service.evaluate_regime(test_request)
        
        return {
            "success": True,
            "test_data": True,
            "evaluation_result": result.dict(),
            "message": "Test regime calculation completed successfully"
        }
        
    except Exception as e:
        logger.error(f"Error in regime test: {str(e)}")
        return {
            "success": False,
            "test_data": True,
            "error": str(e),
            "message": "Test regime calculation failed"
        }


@router.get("/alerts/recent")
async def get_recent_alerts(
    days: int = Query(7, ge=1, le=30, description="Number of days to look back"),
    level: Optional[str] = Query(None, description="Filter by alert level (info/warning/critical)"),
    regime_service: RiskRegimeService = Depends(lambda: get_risk_regime_service(db))
):
    """
    Get recent regime alerts
    
    GET /api/regime/alerts/recent?days=7&level=critical
    
    Returns recent alerts filtered by:
    - Time period (1-30 days back)
    - Alert level (optional filter)
    - Alert type (flip, override, warning)
    
    Query parameters:
    - days: Days to look back (1-30, default 7)
    - level: Filter by level (info/warning/critical)
    """
    try:
        # Calculate date range
        end_date = datetime.now().date()
        start_date = end_date - datetime.timedelta(days=days)
        
        # Get history with alerts
        history = await regime_service.get_regime_history(
            from_date=start_date.strftime('%Y-%m-%d'),
            to_date=end_date.strftime('%Y-%m-%d'),
            limit=days * 2  # Allow for multiple alerts per day
        )
        
        # Filter entries with alerts
        alerts = []
        for entry in history.series:
            if entry.alert_type:
                # Filter by level if specified
                if level and level.lower() not in ['info', 'warning', 'critical']:
                    continue
                    
                alert_info = {
                    "date": entry.date,
                    "alert_type": entry.alert_type.value,
                    "state": entry.state.value,
                    "z_score": entry.z_score,
                    "syi_excess": entry.syi_excess,
                    "spread": entry.spread
                }
                alerts.append(alert_info)
        
        return {
            "success": True,
            "alerts": alerts,
            "total_alerts": len(alerts),
            "period_days": days,
            "level_filter": level
        }
        
    except Exception as e:
        logger.error(f"Error getting recent alerts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get recent alerts: {str(e)}")


@router.post("/start")
async def start_regime_service():
    """
    Start the risk regime service
    
    POST /api/regime/start
    
    Initializes the risk regime detection service:
    - Creates database collections and indexes
    - Loads configuration parameters
    - Sets up alert webhooks
    - Initializes calculation cache
    
    Called during application startup or service restart.
    """
    try:
        regime_service = await start_risk_regime_service(db)
        
        logger.info("Risk regime service started successfully")
        
        return {
            "success": True,
            "message": "Risk Regime Inversion Alert Service started",
            "service": "risk_regime",
            "status": "running",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "features": [
                "Risk regime detection (Risk-On/Risk-Off)",
                "SYI excess and EMA trend analysis", 
                "Volatility-normalized z-score calculations",
                "Momentum analysis (7-day slope)",
                "Breadth calculation across RAY components",
                "Peg stress override mechanism",
                "Persistence and cooldown management",
                "Alert system with webhook notifications"
            ]
        }
        
    except Exception as e:
        logger.error(f"Failed to start regime service: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start service: {str(e)}")


@router.post("/stop")
async def stop_regime_service():
    """
    Stop the risk regime service
    
    POST /api/regime/stop
    
    Gracefully shuts down the risk regime service:
    - Clears calculation cache
    - Closes database connections
    - Stops background tasks
    
    Used for maintenance or service updates.
    """
    try:
        from services.risk_regime_service import stop_risk_regime_service
        
        await stop_risk_regime_service()
        
        logger.info("Risk regime service stopped successfully")
        
        return {
            "success": True,
            "message": "Risk Regime Inversion Alert Service stopped",
            "service": "risk_regime", 
            "status": "stopped",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
    except Exception as e:
        logger.error(f"Failed to stop regime service: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to stop service: {str(e)}")


@router.get("/parameters")
async def get_regime_parameters(
    regime_service: RiskRegimeService = Depends(lambda: get_risk_regime_service(db))
):
    """
    Get current regime detection parameters
    
    GET /api/regime/parameters
    
    Returns configuration parameters:
    - EMA periods (short/long)
    - Z-score thresholds
    - Persistence and cooldown settings
    - Breadth thresholds
    - Peg stress limits
    
    Used for debugging and parameter tuning.
    """
    try:
        health = await regime_service.get_health_status()
        
        return {
            "success": True,
            "parameters": health.parameters.dict(),
            "methodology_version": health.methodology_version,
            "params_version": health.params_version
        }
        
    except Exception as e:
        logger.error(f"Error getting parameters: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get parameters: {str(e)}")


@router.get("/summary")
async def get_regime_summary(
    regime_service: RiskRegimeService = Depends(lambda: get_risk_regime_service(db))
):
    """
    Get comprehensive regime service summary
    
    GET /api/regime/summary
    
    Returns complete service overview:
    - Service health and status
    - Current regime state and indicators
    - Recent statistics and performance
    - Configuration parameters
    - Alert summary
    
    Perfect for dashboard overview widgets.
    """
    try:
        # Get health, stats, and current state
        health = await regime_service.get_health_status()
        stats = await regime_service.get_regime_stats()
        
        # Get current state
        current_response = await get_current_regime(regime_service)
        
        return {
            "success": True,
            "service_info": {
                "status": health.status,
                "methodology_version": health.methodology_version,
                "last_evaluation": health.last_evaluation,
                "total_evaluations": health.total_evaluations
            },
            "current_state": current_response,
            "statistics": {
                "total_days": stats.total_days,
                "risk_on_days": stats.risk_on_days,
                "risk_off_days": stats.risk_off_days,
                "override_days": stats.override_days,
                "total_flips": stats.total_flips,
                "avg_regime_duration": stats.avg_regime_duration
            },
            "parameters": health.parameters.dict(),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
    except Exception as e:
        logger.error(f"Error getting regime summary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get summary: {str(e)}")