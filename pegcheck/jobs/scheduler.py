"""
Scheduled jobs for pegcheck data management and analytics
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, List
import json

from ..core.config import DEFAULT_SYMBOLS
from ..core.compute import compute_peg_analysis
from ..sources import coingecko, cryptocompare, chainlink, uniswap
from ..analytics.trend_analyzer import TrendAnalyzer

logger = logging.getLogger(__name__)

class PegCheckScheduler:
    """Scheduler for automated pegcheck operations"""
    
    def __init__(self, storage_backend, enable_oracle: bool = False, enable_dex: bool = False):
        self.storage = storage_backend
        self.enable_oracle = enable_oracle
        self.enable_dex = enable_dex
        self.trend_analyzer = TrendAnalyzer(storage_backend)
        self.running = False
        self._tasks = []
    
    async def start(self):
        """Start the scheduler"""
        if self.running:
            logger.warning("Scheduler already running")
            return
        
        self.running = True
        logger.info("Starting PegCheck scheduler")
        
        # Schedule different jobs
        self._tasks = [
            asyncio.create_task(self._run_periodic_peg_checks()),
            asyncio.create_task(self._run_data_cleanup()),
            asyncio.create_task(self._run_trend_analysis()),
            asyncio.create_task(self._run_health_monitoring())
        ]
        
        # Wait for all tasks
        try:
            await asyncio.gather(*self._tasks)
        except asyncio.CancelledError:
            logger.info("Scheduler tasks cancelled")
    
    async def stop(self):
        """Stop the scheduler"""
        if not self.running:
            return
        
        self.running = False
        logger.info("Stopping PegCheck scheduler")
        
        # Cancel all tasks
        for task in self._tasks:
            task.cancel()
        
        # Wait for tasks to complete cancellation
        await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks.clear()
    
    async def _run_periodic_peg_checks(self):
        """Run peg checks every 5 minutes"""
        while self.running:
            try:
                await self.run_peg_check_job()
                await asyncio.sleep(300)  # 5 minutes
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in periodic peg checks: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retry
    
    async def _run_data_cleanup(self):
        """Run data cleanup every 24 hours"""
        while self.running:
            try:
                await asyncio.sleep(86400)  # 24 hours
                await self.run_cleanup_job()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in data cleanup: {e}")
    
    async def _run_trend_analysis(self):
        """Run trend analysis every 6 hours"""
        while self.running:
            try:
                await asyncio.sleep(21600)  # 6 hours
                await self.run_trend_analysis_job()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in trend analysis: {e}")
    
    async def _run_health_monitoring(self):
        """Run health monitoring every hour"""
        while self.running:
            try:
                await asyncio.sleep(3600)  # 1 hour
                await self.run_health_monitoring_job()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health monitoring: {e}")
    
    async def run_peg_check_job(self) -> bool:
        """Execute a single peg check job"""
        try:
            logger.info("Running scheduled peg check")
            
            # Fetch data from all sources
            cg_prices = coingecko.fetch(DEFAULT_SYMBOLS)
            cc_prices = cryptocompare.fetch(DEFAULT_SYMBOLS)
            
            chainlink_prices = None
            if self.enable_oracle:
                try:
                    chainlink_prices = chainlink.fetch(DEFAULT_SYMBOLS)
                except Exception as e:
                    logger.warning(f"Chainlink fetch failed: {e}")
            
            uniswap_prices = None
            if self.enable_dex:
                try:
                    uniswap_prices = uniswap.fetch(DEFAULT_SYMBOLS)
                except Exception as e:
                    logger.warning(f"Uniswap fetch failed: {e}")
            
            # Compute peg analysis
            payload = compute_peg_analysis(
                coingecko_prices=cg_prices,
                cryptocompare_prices=cc_prices,
                chainlink_prices=chainlink_prices,
                uniswap_prices=uniswap_prices,
                symbols=DEFAULT_SYMBOLS
            )
            
            # Store result
            success = await self.storage.store_peg_check(payload)
            
            if success:
                depegs = payload.total_depegs
                max_deviation = payload.max_deviation_bps
                logger.info(f"Peg check completed: {depegs} depegs detected, max deviation: {max_deviation:.1f} bps")
                
                # Log any significant depegs
                for report in payload.reports:
                    if report.is_depeg:
                        logger.warning(f"DEPEG ALERT: {report.symbol} at ${report.avg_ref:.4f} ({report.bps_diff:.1f} bps deviation)")
            else:
                logger.error("Failed to store peg check result")
            
            return success
            
        except Exception as e:
            logger.error(f"Peg check job failed: {e}")
            return False
    
    async def run_cleanup_job(self) -> int:
        """Execute data cleanup job"""
        try:
            logger.info("Running data cleanup job")
            
            # Clean up old data (keep last 30 days)
            deleted_count = await self.storage.cleanup_old_data(days_to_keep=30)
            logger.info(f"Data cleanup completed: {deleted_count} old records deleted")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"Data cleanup job failed: {e}")
            return 0
    
    async def run_trend_analysis_job(self) -> Optional[dict]:
        """Execute trend analysis job"""
        try:
            logger.info("Running trend analysis job")
            
            # Analyze trends for major stablecoins
            major_symbols = ["USDT", "USDC", "DAI", "FRAX", "BUSD"]
            report = await self.trend_analyzer.get_market_stability_report(major_symbols, hours=168)
            
            # Log key findings
            if "market_summary" in report:
                summary = report["market_summary"]
                logger.info(f"Market analysis: {summary['market_health']} health, "
                           f"avg risk score: {summary['avg_risk_score']}, "
                           f"avg deviation: {summary['avg_deviation_bps']:.1f} bps")
                
                # Log alerts
                alerts = report.get("alerts", {})
                if alerts.get("high_risk_symbols"):
                    logger.warning(f"High risk symbols detected: {alerts['high_risk_symbols']}")
                if alerts.get("deteriorating_symbols"):
                    logger.warning(f"Deteriorating symbols: {alerts['deteriorating_symbols']}")
            
            return report
            
        except Exception as e:
            logger.error(f"Trend analysis job failed: {e}")
            return None
    
    async def run_health_monitoring_job(self) -> dict:
        """Execute health monitoring job"""
        try:
            logger.debug("Running health monitoring job")
            
            # Check storage health
            storage_health = await self.storage.health_check()
            
            # Check data source health
            sources_health = {}
            
            try:
                test_result = coingecko.fetch(["USDT"])
                sources_health["coingecko"] = "healthy" if test_result.get("USDT", 0) > 0 else "degraded"
            except Exception as e:
                sources_health["coingecko"] = f"error: {str(e)}"
            
            try:
                test_result = cryptocompare.fetch(["USDT"])
                sources_health["cryptocompare"] = "healthy" if test_result.get("USDT", 0) > 0 else "degraded"
            except Exception as e:
                sources_health["cryptocompare"] = f"error: {str(e)}"
            
            if self.enable_oracle:
                try:
                    chainlink_health = chainlink.health_check()
                    sources_health["chainlink"] = chainlink_health["status"]
                except Exception as e:
                    sources_health["chainlink"] = f"error: {str(e)}"
            
            if self.enable_dex:
                try:
                    uniswap_health = uniswap.health_check()
                    sources_health["uniswap"] = uniswap_health["status"]
                except Exception as e:
                    sources_health["uniswap"] = f"error: {str(e)}"
            
            health_report = {
                "timestamp": datetime.utcnow().isoformat(),
                "storage": storage_health,
                "data_sources": sources_health,
                "overall_status": "healthy" if storage_health.get("status") == "healthy" else "degraded"
            }
            
            # Log any issues
            unhealthy_sources = [source for source, status in sources_health.items() 
                               if "error" in str(status) or status == "degraded"]
            if unhealthy_sources:
                logger.warning(f"Unhealthy data sources detected: {unhealthy_sources}")
            
            return health_report
            
        except Exception as e:
            logger.error(f"Health monitoring job failed: {e}")
            return {"error": str(e), "timestamp": datetime.utcnow().isoformat()}