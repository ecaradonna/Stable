import asyncio
import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import signal
import sys

from services.index_calculator import StableYieldIndexCalculator
from services.index_storage import IndexStorageService

logger = logging.getLogger(__name__)

class IndexSchedulerService:
    """
    Background service for calculating and storing StableYield Index values
    Runs calculations every 1 minute (configurable)
    """
    
    def __init__(self, db):
        self.db = db
        self.calculator = StableYieldIndexCalculator()
        self.storage = IndexStorageService(db)
        self.scheduler = AsyncIOScheduler()
        self.is_running = False
        
        # Configuration
        self.update_interval_minutes = 1  # TODO: Make configurable
        self.max_retries = 3
        self.retry_delay = 30  # seconds
    
    async def start(self):
        """Start the index calculation scheduler"""
        try:
            await self.storage.initialize_collections()
            
            # Schedule regular index calculations
            self.scheduler.add_job(
                self._calculate_and_store_index,
                trigger=IntervalTrigger(minutes=self.update_interval_minutes),
                id='stableyield_index_calculation',
                name='StableYield Index Calculation',
                replace_existing=True,
                max_instances=1  # Prevent overlapping calculations
            )
            
            # Calculate initial index value
            await self._calculate_and_store_index()
            
            # Start scheduler
            self.scheduler.start()
            self.is_running = True
            
            logger.info(f"Index scheduler started - updating every {self.update_interval_minutes} minute(s)")
            
            # Setup graceful shutdown
            signal.signal(signal.SIGTERM, self._signal_handler)
            signal.signal(signal.SIGINT, self._signal_handler)
            
        except Exception as e:
            logger.error(f"Failed to start index scheduler: {e}")
            raise
    
    async def stop(self):
        """Stop the index calculation scheduler"""
        try:
            if self.scheduler.running:
                self.scheduler.shutdown(wait=True)
            self.is_running = False
            logger.info("Index scheduler stopped")
        except Exception as e:
            logger.error(f"Error stopping scheduler: {e}")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down...")
        asyncio.create_task(self.stop())
    
    async def _calculate_and_store_index(self):
        """Calculate and store a new index value with retry logic"""
        attempt = 0
        
        while attempt < self.max_retries:
            try:
                logger.info(f"Starting index calculation (attempt {attempt + 1})")
                
                # Calculate new index value
                index_value = await self.calculator.calculate_index()
                
                # Store in database
                success = await self.storage.store_index_value(index_value)
                
                if success:
                    logger.info(f"✅ StableYield Index updated: {index_value.value}% ({len(index_value.constituents)} constituents)")
                    
                    # Log constituent details
                    for constituent in index_value.constituents:
                        logger.debug(f"  {constituent.symbol}: {constituent.ray}% RAY (weight: {constituent.weight:.3f})")
                    
                    return index_value
                else:
                    raise Exception("Failed to store index value")
                    
            except Exception as e:
                attempt += 1
                logger.error(f"Index calculation failed (attempt {attempt}/{self.max_retries}): {e}")
                
                if attempt < self.max_retries:
                    logger.info(f"Retrying in {self.retry_delay} seconds...")
                    await asyncio.sleep(self.retry_delay)
                else:
                    logger.error("Max retries exceeded, skipping this calculation cycle")
                    break
        
        return None
    
    async def get_scheduler_status(self) -> dict:
        """Get current scheduler status"""
        try:
            jobs = []
            for job in self.scheduler.get_jobs():
                jobs.append({
                    "id": job.id,
                    "name": job.name,
                    "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                    "trigger": str(job.trigger)
                })
            
            return {
                "running": self.is_running,
                "scheduler_running": self.scheduler.running if hasattr(self.scheduler, 'running') else False,
                "update_interval_minutes": self.update_interval_minutes,
                "jobs": jobs,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting scheduler status: {e}")
            return {"error": str(e)}
    
    async def force_calculation(self):
        """Force an immediate index calculation (for testing/debugging)"""
        logger.info("Forcing immediate index calculation...")
        return await self._calculate_and_store_index()

# Global scheduler instance
_scheduler_instance = None

async def get_scheduler_instance(db) -> IndexSchedulerService:
    """Get or create global scheduler instance"""
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = IndexSchedulerService(db)
    return _scheduler_instance

async def start_index_scheduler(db):
    """Start the global index scheduler"""
    scheduler = await get_scheduler_instance(db)
    if not scheduler.is_running:
        await scheduler.start()
    return scheduler

async def stop_index_scheduler():
    """Stop the global index scheduler"""
    global _scheduler_instance
    if _scheduler_instance and _scheduler_instance.is_running:
        await _scheduler_instance.stop()

# TODO: PRODUCTION UPGRADES NEEDED
# 1. Add monitoring and alerting for failed calculations
# 2. Implement distributed scheduling for high availability
# 3. Add configuration management (environment variables)
# 4. Implement health checks and auto-recovery
# 5. Add performance metrics and logging
# 6. Consider using Redis/RabbitMQ for job queueing in production