"""
Batch Analytics Service (STEP 7)
Scheduled batch jobs for advanced analytics, historical data processing, and institutional reporting
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import json
from pathlib import Path
import pandas as pd
import numpy as np
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from .yield_aggregator import YieldAggregator
from .ray_calculator import RAYCalculator
from .syi_compositor import SYICompositor
from .realtime_data_integrator import get_realtime_integrator

logger = logging.getLogger(__name__)

@dataclass
class BatchAnalyticsResult:
    job_name: str
    execution_timestamp: datetime
    execution_duration_seconds: float
    success: bool
    records_processed: int
    data: Dict[str, Any]
    error_message: Optional[str] = None

@dataclass
class HistoricalDataPoint:
    timestamp: datetime
    symbol: str
    apy: float
    ray: float
    risk_penalty: float
    confidence_score: float
    peg_stability_score: Optional[float] = None
    liquidity_score: Optional[float] = None

@dataclass
class IndexPerformanceMetrics:
    period: str
    start_date: datetime
    end_date: datetime
    starting_value: float
    ending_value: float
    total_return: float
    annualized_return: float
    volatility: float
    sharpe_ratio: float
    max_drawdown: float
    constituent_changes: int

class BatchAnalyticsService:
    """Service for running scheduled batch analytics jobs"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.yield_aggregator = YieldAggregator()
        self.ray_calculator = RAYCalculator()
        self.syi_compositor = SYICompositor()
        
        # Data storage paths
        self.data_dir = Path("/app/data/analytics")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Historical data storage
        self.historical_data = []
        self.index_history = []
        
        # Job execution tracking
        self.job_results = {}
        self.last_execution_times = {}
        
        # Configuration
        self.config = {
            "historical_data_retention_days": 365,
            "batch_size": 1000,
            "export_formats": ["json", "csv", "parquet"],
            "analytics_intervals": {
                "peg_metrics": "15min",
                "liquidity_metrics": "30min", 
                "risk_analytics": "1hour",
                "performance_analytics": "6hour",
                "compliance_report": "1day",
                "data_export": "1day"
            }
        }
        
        self.is_running = False
    
    async def start(self):
        """Start the batch analytics service and schedule jobs"""
        if self.is_running:
            logger.warning("⚠️ Batch analytics service already running")
            return
        
        self.is_running = True
        logger.info("🚀 Starting batch analytics service...")
        
        # Schedule all batch jobs
        await self._schedule_jobs()
        
        # Start the scheduler
        self.scheduler.start()
        logger.info("✅ Batch analytics service started with scheduled jobs")
    
    async def stop(self):
        """Stop the batch analytics service"""
        if not self.is_running:
            return
        
        self.is_running = False
        self.scheduler.shutdown(wait=True)
        logger.info("🛑 Batch analytics service stopped")
    
    async def _schedule_jobs(self):
        """Schedule all batch analytics jobs"""
        
        # Peg Metrics Analytics (every 15 minutes)
        self.scheduler.add_job(
            self._run_peg_metrics_analytics,
            IntervalTrigger(minutes=15),
            id='peg_metrics_analytics',
            name='Peg Stability Metrics Analytics',
            replace_existing=True
        )
        
        # Liquidity Metrics Analytics (every 30 minutes) 
        self.scheduler.add_job(
            self._run_liquidity_metrics_analytics,
            IntervalTrigger(minutes=30),
            id='liquidity_metrics_analytics',
            name='Liquidity Metrics Analytics',
            replace_existing=True
        )
        
        # Risk Analytics (every hour)
        self.scheduler.add_job(
            self._run_risk_analytics,
            IntervalTrigger(hours=1),
            id='risk_analytics',
            name='Advanced Risk Analytics',
            replace_existing=True
        )
        
        # Performance Analytics (every 6 hours)
        self.scheduler.add_job(
            self._run_performance_analytics,
            IntervalTrigger(hours=6),
            id='performance_analytics', 
            name='Index Performance Analytics',
            replace_existing=True
        )
        
        # Daily Compliance Report (every day at 2 AM UTC)
        self.scheduler.add_job(
            self._run_compliance_report,
            CronTrigger(hour=2, minute=0),
            id='compliance_report',
            name='Daily Compliance Report',
            replace_existing=True
        )
        
        # Daily Data Export (every day at 3 AM UTC)
        self.scheduler.add_job(
            self._run_data_export,
            CronTrigger(hour=3, minute=0),
            id='data_export',
            name='Daily Data Export',
            replace_existing=True
        )
        
        # Historical Data Collection (every 10 minutes)
        self.scheduler.add_job(
            self._collect_historical_data,
            IntervalTrigger(minutes=10),
            id='historical_data_collection',
            name='Historical Data Collection',
            replace_existing=True
        )
        
        logger.info("📅 Scheduled 7 batch analytics jobs")
    
    async def _run_peg_metrics_analytics(self):
        """Batch job for peg stability metrics analytics"""
        start_time = datetime.utcnow()
        job_name = "peg_metrics_analytics"
        
        try:
            logger.info(f"🎯 Running {job_name}...")
            
            # Get real-time integrator data
            rt_integrator = get_realtime_integrator()
            peg_metrics = rt_integrator.get_peg_metrics() if rt_integrator else {}
            
            # Calculate peg stability analytics
            analytics_data = {
                "analysis_timestamp": start_time.isoformat(),
                "symbols_analyzed": list(peg_metrics.keys()),
                "peg_stability_summary": {},
                "alerts": [],
                "trends": {}
            }
            
            if peg_metrics:
                # Calculate summary statistics
                scores = [m["peg_stability_score"] for m in peg_metrics.values()]
                deviations = [m["current_deviation"] for m in peg_metrics.values()]
                
                analytics_data["peg_stability_summary"] = {
                    "average_peg_score": np.mean(scores),
                    "median_peg_score": np.median(scores),
                    "min_peg_score": np.min(scores),
                    "max_peg_score": np.max(scores),
                    "average_deviation": np.mean(deviations),
                    "max_deviation": np.max(deviations),
                    "stable_count": len([s for s in scores if s > 0.95]),
                    "warning_count": len([s for s in scores if 0.70 < s <= 0.95]),
                    "critical_count": len([s for s in scores if s <= 0.70])
                }
                
                # Generate alerts for critical deviations
                for symbol, metrics in peg_metrics.items():
                    if metrics["current_deviation"] > 0.02:  # 2% deviation alert
                        analytics_data["alerts"].append({
                            "type": "critical_deviation",
                            "symbol": symbol,
                            "deviation": metrics["current_deviation"],
                            "severity": "high" if metrics["current_deviation"] > 0.05 else "medium"
                        })
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            result = BatchAnalyticsResult(
                job_name=job_name,
                execution_timestamp=start_time,
                execution_duration_seconds=execution_time,
                success=True,
                records_processed=len(peg_metrics),
                data=analytics_data
            )
            
            self.job_results[job_name] = result
            self.last_execution_times[job_name] = start_time
            
            logger.info(f"✅ {job_name} completed: {len(peg_metrics)} symbols analyzed in {execution_time:.2f}s")
            
        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"❌ {job_name} failed: {e}")
            
            result = BatchAnalyticsResult(
                job_name=job_name,
                execution_timestamp=start_time,
                execution_duration_seconds=execution_time,
                success=False,
                records_processed=0,
                data={},
                error_message=str(e)
            )
            
            self.job_results[job_name] = result
    
    async def _run_liquidity_metrics_analytics(self):
        """Batch job for liquidity metrics analytics"""
        start_time = datetime.utcnow()
        job_name = "liquidity_metrics_analytics"
        
        try:
            logger.info(f"💧 Running {job_name}...")
            
            # Get real-time liquidity data
            rt_integrator = get_realtime_integrator()
            liquidity_metrics = rt_integrator.get_liquidity_metrics() if rt_integrator else {}
            
            # Calculate liquidity analytics
            analytics_data = {
                "analysis_timestamp": start_time.isoformat(),
                "symbols_analyzed": list(liquidity_metrics.keys()),
                "liquidity_summary": {},
                "market_conditions": {},
                "alerts": []
            }
            
            if liquidity_metrics:
                # Calculate summary statistics
                scores = [m["liquidity_score"] for m in liquidity_metrics.values()]
                spreads = [m["avg_spread_bps"] for m in liquidity_metrics.values()]
                depths = [m["total_depth_usd"] for m in liquidity_metrics.values()]
                
                analytics_data["liquidity_summary"] = {
                    "average_liquidity_score": np.mean(scores),
                    "median_liquidity_score": np.median(scores),
                    "average_spread_bps": np.mean(spreads),
                    "median_spread_bps": np.median(spreads),
                    "total_market_depth": np.sum(depths),
                    "average_depth_per_symbol": np.mean(depths),
                    "excellent_liquidity_count": len([s for s in scores if s > 0.90]),
                    "good_liquidity_count": len([s for s in scores if 0.75 < s <= 0.90]),
                    "poor_liquidity_count": len([s for s in scores if s <= 0.75])
                }
                
                # Market condition analysis
                avg_spread = np.mean(spreads)
                analytics_data["market_conditions"] = {
                    "market_stress_level": "high" if avg_spread > 50 else "medium" if avg_spread > 20 else "low",
                    "liquidity_environment": "tight" if np.mean(scores) < 0.70 else "normal" if np.mean(scores) < 0.85 else "abundant",
                    "total_market_depth_usd": np.sum(depths),
                    "depth_concentration": np.max(depths) / np.sum(depths) if np.sum(depths) > 0 else 0
                }
                
                # Generate liquidity alerts
                for symbol, metrics in liquidity_metrics.items():
                    if metrics["avg_spread_bps"] > 100:  # 100bps spread alert
                        analytics_data["alerts"].append({
                            "type": "wide_spread",
                            "symbol": symbol,
                            "spread_bps": metrics["avg_spread_bps"],
                            "severity": "high" if metrics["avg_spread_bps"] > 200 else "medium"
                        })
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            result = BatchAnalyticsResult(
                job_name=job_name,
                execution_timestamp=start_time,
                execution_duration_seconds=execution_time,
                success=True,
                records_processed=len(liquidity_metrics),
                data=analytics_data
            )
            
            self.job_results[job_name] = result
            self.last_execution_times[job_name] = start_time
            
            logger.info(f"✅ {job_name} completed: {len(liquidity_metrics)} symbols analyzed in {execution_time:.2f}s")
            
        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"❌ {job_name} failed: {e}")
            
            result = BatchAnalyticsResult(
                job_name=job_name,
                execution_timestamp=start_time,
                execution_duration_seconds=execution_time,
                success=False,
                records_processed=0,
                data={},
                error_message=str(e)
            )
            
            self.job_results[job_name] = result
    
    async def _run_risk_analytics(self):
        """Batch job for advanced risk analytics"""
        start_time = datetime.utcnow()
        job_name = "risk_analytics"
        
        try:
            logger.info(f"⚠️ Running {job_name}...")
            
            # Get current yield data and calculate RAY
            current_yields = await self.yield_aggregator.get_all_yields()
            ray_results = self.ray_calculator.calculate_ray_batch(current_yields) if current_yields else []
            
            # Advanced risk analytics
            analytics_data = {
                "analysis_timestamp": start_time.isoformat(),
                "risk_assessment": {},
                "portfolio_metrics": {},
                "stress_tests": {},
                "risk_attribution": {}
            }
            
            if ray_results:
                # Risk factor analysis
                peg_scores = [r.risk_factors.peg_stability_score for r in ray_results]
                liquidity_scores = [r.risk_factors.liquidity_score for r in ray_results]
                counterparty_scores = [r.risk_factors.counterparty_score for r in ray_results]
                protocol_scores = [r.risk_factors.protocol_reputation for r in ray_results]
                temporal_scores = [r.risk_factors.temporal_stability for r in ray_results]
                
                risk_penalties = [r.risk_penalty for r in ray_results]
                confidence_scores = [r.confidence_score for r in ray_results]
                
                analytics_data["risk_assessment"] = {
                    "average_risk_factors": {
                        "peg_stability": np.mean(peg_scores),
                        "liquidity_risk": 1 - np.mean(liquidity_scores),
                        "counterparty_risk": 1 - np.mean(counterparty_scores),
                        "protocol_risk": 1 - np.mean(protocol_scores),
                        "temporal_risk": 1 - np.mean(temporal_scores)
                    },
                    "risk_distribution": {
                        "low_risk_count": len([p for p in risk_penalties if p < 0.20]),
                        "medium_risk_count": len([p for p in risk_penalties if 0.20 <= p < 0.40]),
                        "high_risk_count": len([p for p in risk_penalties if p >= 0.40])
                    },
                    "average_risk_penalty": np.mean(risk_penalties),
                    "max_risk_penalty": np.max(risk_penalties),
                    "average_confidence": np.mean(confidence_scores),
                    "min_confidence": np.min(confidence_scores)
                }
                
                # Portfolio risk metrics
                rays = [r.risk_adjusted_yield for r in ray_results]
                weights = [1/len(rays)] * len(rays)  # Equal weight for simplicity
                
                portfolio_ray = np.sum([r * w for r, w in zip(rays, weights)])
                portfolio_risk = np.sqrt(np.sum([w**2 * (r - portfolio_ray)**2 for r, w in zip(rays, weights)]))
                
                analytics_data["portfolio_metrics"] = {
                    "portfolio_ray": portfolio_ray,
                    "portfolio_risk": portfolio_risk,
                    "risk_adjusted_return": portfolio_ray / portfolio_risk if portfolio_risk > 0 else 0,
                    "diversification_ratio": len(set([r.risk_factors.protocol_reputation for r in ray_results])) / len(ray_results),
                    "concentration_risk": np.max(weights)
                }
                
                # Stress test scenarios
                stress_scenarios = {
                    "peg_break_scenario": self._calculate_stress_scenario(ray_results, "peg_stability", 0.5),
                    "liquidity_crisis_scenario": self._calculate_stress_scenario(ray_results, "liquidity", 0.3),
                    "protocol_hack_scenario": self._calculate_stress_scenario(ray_results, "counterparty", 0.2)
                }
                
                analytics_data["stress_tests"] = stress_scenarios
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            result = BatchAnalyticsResult(
                job_name=job_name,
                execution_timestamp=start_time,
                execution_duration_seconds=execution_time,
                success=True,
                records_processed=len(ray_results),
                data=analytics_data
            )
            
            self.job_results[job_name] = result
            self.last_execution_times[job_name] = start_time
            
            logger.info(f"✅ {job_name} completed: {len(ray_results)} yields analyzed in {execution_time:.2f}s")
            
        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"❌ {job_name} failed: {e}")
            
            result = BatchAnalyticsResult(
                job_name=job_name,
                execution_timestamp=start_time,
                execution_duration_seconds=execution_time,
                success=False,
                records_processed=0,
                data={},
                error_message=str(e)
            )
            
            self.job_results[job_name] = result
    
    def _calculate_stress_scenario(self, ray_results: List, risk_factor: str, stress_level: float) -> Dict[str, Any]:
        """Calculate impact of stress scenario on portfolio"""
        # Simulate stressed risk factors
        stressed_rays = []
        
        for result in ray_results:
            # Apply stress to specific risk factor
            if risk_factor == "peg_stability":
                stressed_peg = result.risk_factors.peg_stability_score * stress_level
                # Recalculate with stressed peg stability
                stressed_ray = result.base_apy * (1 - (1 - stressed_peg) * 0.5)  # Simplified calculation
            elif risk_factor == "liquidity":
                stressed_liquidity = result.risk_factors.liquidity_score * stress_level
                stressed_ray = result.base_apy * (1 - (1 - stressed_liquidity) * 0.4)
            elif risk_factor == "counterparty":
                stressed_counterparty = result.risk_factors.counterparty_score * stress_level
                stressed_ray = result.base_apy * (1 - (1 - stressed_counterparty) * 0.6)
            else:
                stressed_ray = result.risk_adjusted_yield
            
            stressed_rays.append(stressed_ray)
        
        # Calculate portfolio impact
        original_portfolio_ray = np.mean([r.risk_adjusted_yield for r in ray_results])
        stressed_portfolio_ray = np.mean(stressed_rays)
        
        return {
            "scenario": f"{risk_factor}_stress_{stress_level}",
            "original_portfolio_ray": original_portfolio_ray,
            "stressed_portfolio_ray": stressed_portfolio_ray,
            "impact_percentage": ((stressed_portfolio_ray - original_portfolio_ray) / original_portfolio_ray * 100) if original_portfolio_ray > 0 else 0,
            "absolute_impact": stressed_portfolio_ray - original_portfolio_ray
        }
    
    async def _run_performance_analytics(self):
        """Batch job for index performance analytics"""
        start_time = datetime.utcnow()
        job_name = "performance_analytics"
        
        try:
            logger.info(f"📊 Running {job_name}...")
            
            # Get current SYI composition
            current_yields = await self.yield_aggregator.get_all_yields()
            syi_composition = self.syi_compositor.compose_syi(current_yields) if current_yields else None
            
            # Store current index value in history
            if syi_composition:
                self.index_history.append({
                    "timestamp": start_time,
                    "index_value": syi_composition.index_value,
                    "constituent_count": syi_composition.constituent_count,
                    "quality_score": syi_composition.quality_metrics.get("overall_quality", 0)
                })
            
            # Calculate performance metrics
            analytics_data = {
                "analysis_timestamp": start_time.isoformat(),
                "current_index_value": syi_composition.index_value if syi_composition else 0,
                "performance_periods": {},
                "attribution_analysis": {},
                "risk_metrics": {}
            }
            
            # Performance analysis for different periods
            periods = {"1d": 1, "7d": 7, "30d": 30, "90d": 90}
            
            for period_name, days in periods.items():
                period_data = self._calculate_period_performance(days)
                if period_data:
                    analytics_data["performance_periods"][period_name] = period_data
            
            # Attribution analysis
            if syi_composition:
                analytics_data["attribution_analysis"] = {
                    "top_contributors": [
                        {
                            "symbol": c.stablecoin,
                            "protocol": c.protocol,
                            "weight": c.weight,
                            "ray": c.ray,
                            "contribution": c.ray * c.weight
                        }
                        for c in sorted(syi_composition.constituents, 
                                      key=lambda x: x.ray * x.weight, reverse=True)[:5]
                    ],
                    "weight_distribution": {
                        "max_weight": max([c.weight for c in syi_composition.constituents]) if syi_composition.constituents else 0,
                        "min_weight": min([c.weight for c in syi_composition.constituents]) if syi_composition.constituents else 0,
                        "weight_concentration": sum(c.weight for c in sorted(syi_composition.constituents, key=lambda x: x.weight, reverse=True)[:3])
                    }
                }
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            result = BatchAnalyticsResult(
                job_name=job_name,
                execution_timestamp=start_time,
                execution_duration_seconds=execution_time,
                success=True,
                records_processed=1,
                data=analytics_data
            )
            
            self.job_results[job_name] = result
            self.last_execution_times[job_name] = start_time
            
            logger.info(f"✅ {job_name} completed in {execution_time:.2f}s")
            
        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"❌ {job_name} failed: {e}")
            
            result = BatchAnalyticsResult(
                job_name=job_name,
                execution_timestamp=start_time,
                execution_duration_seconds=execution_time,
                success=False,
                records_processed=0,
                data={},
                error_message=str(e)
            )
            
            self.job_results[job_name] = result
    
    def _calculate_period_performance(self, days: int) -> Optional[Dict[str, Any]]:
        """Calculate performance metrics for a specific period"""
        if len(self.index_history) < 2:
            return None
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        period_data = [h for h in self.index_history if h["timestamp"] >= cutoff_date]
        
        if len(period_data) < 2:
            return None
        
        start_value = period_data[0]["index_value"]
        end_value = period_data[-1]["index_value"]
        values = [h["index_value"] for h in period_data]
        
        # Calculate performance metrics
        total_return = (end_value - start_value) / start_value if start_value > 0 else 0
        annualized_return = total_return * (365 / days) if days > 0 else 0
        volatility = np.std(values) if len(values) > 1 else 0
        
        # Max drawdown
        peak = values[0]
        max_drawdown = 0
        for value in values:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak if peak > 0 else 0
            max_drawdown = max(max_drawdown, drawdown)
        
        return {
            "period_days": days,
            "start_value": start_value,
            "end_value": end_value,
            "total_return": total_return,
            "annualized_return": annualized_return,
            "volatility": volatility,
            "sharpe_ratio": annualized_return / volatility if volatility > 0 else 0,
            "max_drawdown": max_drawdown,
            "data_points": len(period_data)
        }
    
    async def _run_compliance_report(self):
        """Daily compliance and regulatory report"""
        start_time = datetime.utcnow()
        job_name = "compliance_report"
        
        try:
            logger.info(f"📋 Running {job_name}...")
            
            # Generate comprehensive compliance report
            report_data = {
                "report_date": start_time.date().isoformat(),
                "report_timestamp": start_time.isoformat(),
                "data_quality": {},
                "risk_compliance": {},
                "operational_metrics": {},
                "audit_trail": {}
            }
            
            # Data quality metrics
            current_yields = await self.yield_aggregator.get_all_yields()
            if current_yields:
                report_data["data_quality"] = {
                    "total_data_sources": len(current_yields),
                    "data_freshness_violations": 0,  # Placeholder
                    "data_completeness_rate": 1.0,   # Placeholder
                    "outlier_detections": 0,         # Placeholder
                    "last_data_update": datetime.utcnow().isoformat()
                }
            
            # Risk compliance
            if hasattr(self, 'job_results') and 'risk_analytics' in self.job_results:
                risk_data = self.job_results['risk_analytics'].data
                report_data["risk_compliance"] = {
                    "risk_limit_breaches": 0,  # Placeholder
                    "concentration_violations": 0,  # Placeholder
                    "average_risk_penalty": risk_data.get("risk_assessment", {}).get("average_risk_penalty", 0),
                    "high_risk_positions": risk_data.get("risk_assessment", {}).get("risk_distribution", {}).get("high_risk_count", 0)
                }
            
            # Operational metrics
            successful_jobs = sum(1 for r in self.job_results.values() if r.success)
            total_jobs = len(self.job_results)
            
            report_data["operational_metrics"] = {
                "job_success_rate": successful_jobs / total_jobs if total_jobs > 0 else 1.0,
                "system_uptime": "99.9%",  # Placeholder
                "api_response_times": "< 100ms",  # Placeholder
                "data_processing_volume": sum(r.records_processed for r in self.job_results.values()),
                "last_system_restart": start_time.isoformat()  # Placeholder
            }
            
            # Save compliance report
            report_file = self.data_dir / f"compliance_report_{start_time.date().isoformat()}.json"
            with open(report_file, 'w') as f:
                json.dump(report_data, f, indent=2, default=str)
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            result = BatchAnalyticsResult(
                job_name=job_name,
                execution_timestamp=start_time,
                execution_duration_seconds=execution_time,
                success=True,
                records_processed=1,
                data=report_data
            )
            
            self.job_results[job_name] = result
            self.last_execution_times[job_name] = start_time
            
            logger.info(f"✅ {job_name} completed: Report saved to {report_file}")
            
        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"❌ {job_name} failed: {e}")
            
            result = BatchAnalyticsResult(
                job_name=job_name,
                execution_timestamp=start_time,
                execution_duration_seconds=execution_time,
                success=False,
                records_processed=0,
                data={},
                error_message=str(e)
            )
            
            self.job_results[job_name] = result
    
    async def _run_data_export(self):
        """Daily data export for external systems"""
        start_time = datetime.utcnow()
        job_name = "data_export"
        
        try:
            logger.info(f"📤 Running {job_name}...")
            
            # Export current yield data
            current_yields = await self.yield_aggregator.get_all_yields()
            
            # Export historical data
            export_data = {
                "export_timestamp": start_time.isoformat(),
                "current_yields": current_yields,
                "historical_data": self.historical_data[-1000:],  # Last 1000 records
                "index_history": self.index_history[-1000:],       # Last 1000 records
                "job_results": {k: asdict(v) for k, v in self.job_results.items()}
            }
            
            # Export in multiple formats
            export_files = []
            date_str = start_time.date().isoformat()
            
            # JSON export
            json_file = self.data_dir / f"stableyield_export_{date_str}.json"
            with open(json_file, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            export_files.append(str(json_file))
            
            # CSV export (yields only)
            if current_yields:
                csv_file = self.data_dir / f"yields_export_{date_str}.csv"
                df = pd.DataFrame(current_yields)
                df.to_csv(csv_file, index=False)
                export_files.append(str(csv_file))
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            result = BatchAnalyticsResult(
                job_name=job_name,
                execution_timestamp=start_time,
                execution_duration_seconds=execution_time,
                success=True,
                records_processed=len(export_files),
                data={"export_files": export_files, "records_exported": len(current_yields) + len(self.historical_data)}
            )
            
            self.job_results[job_name] = result
            self.last_execution_times[job_name] = start_time
            
            logger.info(f"✅ {job_name} completed: {len(export_files)} files exported")
            
        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"❌ {job_name} failed: {e}")
            
            result = BatchAnalyticsResult(
                job_name=job_name,
                execution_timestamp=start_time,
                execution_duration_seconds=execution_time,
                success=False,
                records_processed=0,
                data={},
                error_message=str(e)
            )
            
            self.job_results[job_name] = result
    
    async def _collect_historical_data(self):
        """Collect historical data points for analysis"""
        try:
            # Get current yield and RAY data
            current_yields = await self.yield_aggregator.get_all_yields()
            
            if current_yields:
                ray_results = self.ray_calculator.calculate_ray_batch(current_yields)
                
                # Store historical data points
                for yield_data, ray_result in zip(current_yields, ray_results):
                    data_point = HistoricalDataPoint(
                        timestamp=datetime.utcnow(),
                        symbol=yield_data.get('stablecoin', 'Unknown'),
                        apy=float(yield_data.get('currentYield', 0)),
                        ray=ray_result.risk_adjusted_yield,
                        risk_penalty=ray_result.risk_penalty,
                        confidence_score=ray_result.confidence_score,
                        peg_stability_score=ray_result.risk_factors.peg_stability_score,
                        liquidity_score=ray_result.risk_factors.liquidity_score
                    )
                    
                    self.historical_data.append(asdict(data_point))
                
                # Cleanup old data
                retention_cutoff = datetime.utcnow() - timedelta(days=self.config["historical_data_retention_days"])
                self.historical_data = [
                    d for d in self.historical_data 
                    if datetime.fromisoformat(d["timestamp"]) > retention_cutoff
                ]
                
        except Exception as e:
            logger.error(f"❌ Historical data collection failed: {e}")
    
    def get_job_status(self) -> Dict[str, Any]:
        """Get status of all batch jobs"""
        return {
            "service_running": self.is_running,
            "scheduled_jobs": len(self.scheduler.get_jobs()) if self.scheduler else 0,
            "job_results": {k: asdict(v) for k, v in self.job_results.items()},
            "last_execution_times": {k: v.isoformat() for k, v in self.last_execution_times.items()},
            "data_statistics": {
                "historical_records": len(self.historical_data),
                "index_history_records": len(self.index_history),
                "data_retention_days": self.config["historical_data_retention_days"]
            }
        }
    
    async def run_job_manually(self, job_name: str) -> BatchAnalyticsResult:
        """Manually trigger a specific batch job"""
        job_methods = {
            "peg_metrics_analytics": self._run_peg_metrics_analytics,
            "liquidity_metrics_analytics": self._run_liquidity_metrics_analytics,
            "risk_analytics": self._run_risk_analytics,
            "performance_analytics": self._run_performance_analytics,
            "compliance_report": self._run_compliance_report,
            "data_export": self._run_data_export
        }
        
        if job_name not in job_methods:
            raise ValueError(f"Unknown job: {job_name}")
        
        logger.info(f"🔧 Manually triggering job: {job_name}")
        await job_methods[job_name]()
        
        return self.job_results.get(job_name)

# Global batch analytics service instance
batch_analytics_service = None

async def start_batch_analytics():
    """Start the global batch analytics service"""
    global batch_analytics_service
    
    if batch_analytics_service is None:
        batch_analytics_service = BatchAnalyticsService()
        await batch_analytics_service.start()
        logger.info("🚀 Batch analytics service started")
    else:
        logger.info("⚠️ Batch analytics service already running")

async def stop_batch_analytics():
    """Stop the global batch analytics service"""
    global batch_analytics_service
    
    if batch_analytics_service:
        await batch_analytics_service.stop()
        batch_analytics_service = None
        logger.info("🛑 Batch analytics service stopped")

def get_batch_analytics_service() -> Optional[BatchAnalyticsService]:
    """Get the global batch analytics service"""
    return batch_analytics_service