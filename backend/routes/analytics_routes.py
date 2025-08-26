"""
Analytics Routes (STEP 7)
API endpoints for batch analytics, performance reporting, and compliance
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta

from services.batch_analytics_service import get_batch_analytics_service

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/analytics/status")
async def get_analytics_status() -> Dict[str, Any]:
    """Get status of batch analytics service and all scheduled jobs"""
    try:
        analytics_service = get_batch_analytics_service()
        
        if not analytics_service:
            return {
                "service_running": False,
                "message": "Batch analytics service not started",
                "scheduled_jobs": 0,
                "job_results": {}
            }
        
        return analytics_service.get_job_status()
        
    except Exception as e:
        logger.error(f"Error getting analytics status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get analytics status")

@router.post("/analytics/start")
async def start_analytics_service() -> Dict[str, Any]:
    """Start the batch analytics service and all scheduled jobs"""
    try:
        from services.batch_analytics_service import start_batch_analytics
        
        await start_batch_analytics()
        
        return {
            "message": "Batch analytics service started successfully",
            "scheduled_jobs": [
                "peg_metrics_analytics (15min)",
                "liquidity_metrics_analytics (30min)",
                "risk_analytics (1hour)",
                "performance_analytics (6hour)",
                "compliance_report (daily 2AM UTC)",
                "data_export (daily 3AM UTC)",
                "historical_data_collection (10min)"
            ],
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error starting analytics service: {e}")
        raise HTTPException(status_code=500, detail="Failed to start analytics service")

@router.post("/analytics/stop")
async def stop_analytics_service() -> Dict[str, Any]:
    """Stop the batch analytics service"""
    try:
        from services.batch_analytics_service import stop_batch_analytics
        
        await stop_batch_analytics()
        
        return {
            "message": "Batch analytics service stopped successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error stopping analytics service: {e}")
        raise HTTPException(status_code=500, detail="Failed to stop analytics service")

@router.post("/analytics/jobs/{job_name}/run")
async def run_job_manually(job_name: str) -> Dict[str, Any]:
    """Manually trigger a specific batch analytics job"""
    try:
        analytics_service = get_batch_analytics_service()
        
        if not analytics_service:
            raise HTTPException(status_code=503, detail="Batch analytics service not running")
        
        # Validate job name
        valid_jobs = [
            "peg_metrics_analytics",
            "liquidity_metrics_analytics", 
            "risk_analytics",
            "performance_analytics",
            "compliance_report",
            "data_export"
        ]
        
        if job_name not in valid_jobs:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid job name. Valid jobs: {', '.join(valid_jobs)}"
            )
        
        # Run the job
        result = await analytics_service.run_job_manually(job_name)
        
        return {
            "message": f"Job {job_name} executed successfully",
            "job_result": {
                "job_name": result.job_name,
                "execution_timestamp": result.execution_timestamp.isoformat(),
                "execution_duration_seconds": result.execution_duration_seconds,
                "success": result.success,
                "records_processed": result.records_processed,
                "error_message": result.error_message
            },
            "data": result.data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error running job {job_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to run job {job_name}")

@router.get("/analytics/peg-stability")
async def get_peg_stability_analytics() -> Dict[str, Any]:
    """Get latest peg stability analytics results"""
    try:
        analytics_service = get_batch_analytics_service()
        
        if not analytics_service:
            return {
                "message": "Batch analytics service not running",
                "analytics": {}
            }
        
        # Get latest peg metrics analytics
        job_results = analytics_service.job_results
        peg_analytics = job_results.get("peg_metrics_analytics")
        
        if not peg_analytics:
            return {
                "message": "No peg stability analytics available yet",
                "analytics": {}
            }
        
        return {
            "analytics": peg_analytics.data,
            "last_execution": peg_analytics.execution_timestamp.isoformat(),
            "execution_duration": peg_analytics.execution_duration_seconds,
            "success": peg_analytics.success,
            "records_processed": peg_analytics.records_processed
        }
        
    except Exception as e:
        logger.error(f"Error getting peg stability analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get peg stability analytics")

@router.get("/analytics/liquidity")
async def get_liquidity_analytics() -> Dict[str, Any]:
    """Get latest liquidity analytics results"""
    try:
        analytics_service = get_batch_analytics_service()
        
        if not analytics_service:
            return {
                "message": "Batch analytics service not running",
                "analytics": {}
            }
        
        # Get latest liquidity metrics analytics
        job_results = analytics_service.job_results
        liquidity_analytics = job_results.get("liquidity_metrics_analytics")
        
        if not liquidity_analytics:
            return {
                "message": "No liquidity analytics available yet",
                "analytics": {}
            }
        
        return {
            "analytics": liquidity_analytics.data,
            "last_execution": liquidity_analytics.execution_timestamp.isoformat(),
            "execution_duration": liquidity_analytics.execution_duration_seconds,
            "success": liquidity_analytics.success,
            "records_processed": liquidity_analytics.records_processed
        }
        
    except Exception as e:
        logger.error(f"Error getting liquidity analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get liquidity analytics")

@router.get("/analytics/risk")
async def get_risk_analytics() -> Dict[str, Any]:
    """Get latest advanced risk analytics results"""
    try:
        analytics_service = get_batch_analytics_service()
        
        if not analytics_service:
            return {
                "message": "Batch analytics service not running", 
                "analytics": {}
            }
        
        # Get latest risk analytics
        job_results = analytics_service.job_results
        risk_analytics = job_results.get("risk_analytics")
        
        if not risk_analytics:
            return {
                "message": "No risk analytics available yet",
                "analytics": {}
            }
        
        return {
            "analytics": risk_analytics.data,
            "last_execution": risk_analytics.execution_timestamp.isoformat(),
            "execution_duration": risk_analytics.execution_duration_seconds,
            "success": risk_analytics.success,
            "records_processed": risk_analytics.records_processed
        }
        
    except Exception as e:
        logger.error(f"Error getting risk analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get risk analytics")

@router.get("/analytics/performance")
async def get_performance_analytics(
    period: Optional[str] = Query(default="30d", description="Performance period (1d, 7d, 30d, 90d)")
) -> Dict[str, Any]:
    """Get index performance analytics for specified period"""
    try:
        analytics_service = get_batch_analytics_service()
        
        if not analytics_service:
            return {
                "message": "Batch analytics service not running",
                "performance": {}
            }
        
        # Get latest performance analytics
        job_results = analytics_service.job_results
        performance_analytics = job_results.get("performance_analytics")
        
        if not performance_analytics:
            return {
                "message": "No performance analytics available yet",
                "performance": {}
            }
        
        # Extract performance for requested period
        performance_data = performance_analytics.data
        period_performance = performance_data.get("performance_periods", {}).get(period, {})
        
        return {
            "period": period,
            "performance": period_performance,
            "attribution_analysis": performance_data.get("attribution_analysis", {}),
            "current_index_value": performance_data.get("current_index_value", 0),
            "last_execution": performance_analytics.execution_timestamp.isoformat(),
            "execution_duration": performance_analytics.execution_duration_seconds
        }
        
    except Exception as e:
        logger.error(f"Error getting performance analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get performance analytics")

@router.get("/analytics/compliance-report")
async def get_compliance_report(
    date: Optional[str] = Query(default=None, description="Report date (YYYY-MM-DD), defaults to today")
) -> Dict[str, Any]:
    """Get compliance report for specified date"""
    try:
        analytics_service = get_batch_analytics_service()
        
        if not analytics_service:
            return {
                "message": "Batch analytics service not running",
                "report": {}
            }
        
        # Get latest compliance report
        job_results = analytics_service.job_results
        compliance_report = job_results.get("compliance_report")
        
        if not compliance_report:
            return {
                "message": "No compliance report available yet",
                "report": {}
            }
        
        report_data = compliance_report.data
        
        # If specific date requested, try to load from file
        if date:
            try:
                from pathlib import Path
                import json
                
                data_dir = Path("/app/data/analytics")
                report_file = data_dir / f"compliance_report_{date}.json"
                
                if report_file.exists():
                    with open(report_file, 'r') as f:
                        report_data = json.load(f)
            except Exception as e:
                logger.warning(f"Could not load compliance report for {date}: {e}")
        
        return {
            "report": report_data,
            "last_execution": compliance_report.execution_timestamp.isoformat(),
            "execution_duration": compliance_report.execution_duration_seconds,
            "success": compliance_report.success
        }
        
    except Exception as e:
        logger.error(f"Error getting compliance report: {e}")
        raise HTTPException(status_code=500, detail="Failed to get compliance report")

@router.get("/analytics/historical-data")
async def get_historical_data(
    symbol: Optional[str] = Query(default=None, description="Filter by stablecoin symbol"),
    days: Optional[int] = Query(default=30, description="Number of days of history"),
    limit: Optional[int] = Query(default=1000, description="Maximum number of records")
) -> Dict[str, Any]:
    """Get historical yield and RAY data"""
    try:
        analytics_service = get_batch_analytics_service()
        
        if not analytics_service:
            return {
                "message": "Batch analytics service not running",
                "historical_data": []
            }
        
        # Get historical data
        all_historical_data = analytics_service.historical_data
        
        # Apply filters
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        filtered_data = [
            d for d in all_historical_data 
            if datetime.fromisoformat(d["timestamp"]) >= cutoff_date
        ]
        
        # Filter by symbol if specified
        if symbol:
            filtered_data = [d for d in filtered_data if d["symbol"].upper() == symbol.upper()]
        
        # Apply limit
        filtered_data = filtered_data[-limit:] if limit else filtered_data
        
        return {
            "historical_data": filtered_data,
            "total_records": len(filtered_data),
            "period_days": days,
            "symbol_filter": symbol,
            "data_range": {
                "start_date": filtered_data[0]["timestamp"] if filtered_data else None,
                "end_date": filtered_data[-1]["timestamp"] if filtered_data else None
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting historical data: {e}")
        raise HTTPException(status_code=500, detail="Failed to get historical data")

@router.get("/analytics/export")
async def get_data_export_info() -> Dict[str, Any]:
    """Get information about latest data export"""
    try:
        analytics_service = get_batch_analytics_service()
        
        if not analytics_service:
            return {
                "message": "Batch analytics service not running",
                "export_info": {}
            }
        
        # Get latest data export job
        job_results = analytics_service.job_results
        data_export = job_results.get("data_export")
        
        if not data_export:
            return {
                "message": "No data export available yet",
                "export_info": {}
            }
        
        return {
            "export_info": data_export.data,
            "last_execution": data_export.execution_timestamp.isoformat(),
            "execution_duration": data_export.execution_duration_seconds,
            "success": data_export.success,
            "records_processed": data_export.records_processed
        }
        
    except Exception as e:
        logger.error(f"Error getting data export info: {e}")
        raise HTTPException(status_code=500, detail="Failed to get data export info")

@router.get("/analytics/summary")
async def get_analytics_summary() -> Dict[str, Any]:
    """Get comprehensive summary of all analytics"""
    try:
        analytics_service = get_batch_analytics_service()
        
        if not analytics_service:
            return {
                "message": "Batch analytics service not running",
                "summary": {}
            }
        
        # Get all job results
        job_results = analytics_service.job_results
        
        # Create summary
        summary = {
            "service_status": {
                "running": analytics_service.is_running,
                "scheduled_jobs": len(analytics_service.scheduler.get_jobs()) if analytics_service.scheduler else 0,
                "completed_jobs": len(job_results),
                "success_rate": sum(1 for r in job_results.values() if r.success) / len(job_results) if job_results else 0
            },
            "data_summary": {
                "historical_records": len(analytics_service.historical_data),
                "index_history_records": len(analytics_service.index_history),
                "total_records_processed": sum(r.records_processed for r in job_results.values())
            },
            "latest_analytics": {},
            "last_executions": {}
        }
        
        # Add latest analytics from each job type
        for job_name, result in job_results.items():
            if result.success:
                summary["latest_analytics"][job_name] = {
                    "timestamp": result.execution_timestamp.isoformat(),
                    "records_processed": result.records_processed,
                    "execution_time": result.execution_duration_seconds
                }
                
                # Add key metrics from each analytics type
                if job_name == "peg_metrics_analytics" and result.data:
                    peg_summary = result.data.get("peg_stability_summary", {})
                    summary["latest_analytics"][job_name]["key_metrics"] = {
                        "average_peg_score": peg_summary.get("average_peg_score", 0),
                        "critical_count": peg_summary.get("critical_count", 0)
                    }
                elif job_name == "risk_analytics" and result.data:
                    risk_assessment = result.data.get("risk_assessment", {})
                    summary["latest_analytics"][job_name]["key_metrics"] = {
                        "average_risk_penalty": risk_assessment.get("average_risk_penalty", 0),
                        "high_risk_count": risk_assessment.get("risk_distribution", {}).get("high_risk_count", 0)
                    }
        
        return summary
        
    except Exception as e:
        logger.error(f"Error getting analytics summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to get analytics summary")