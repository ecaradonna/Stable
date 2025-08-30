"""
PostgreSQL/TimescaleDB storage backend for pegcheck data persistence
"""

import asyncio
import asyncpg
import os
import json
from typing import List, Dict, Optional, Tuple, Union
from datetime import datetime, timedelta
import logging

from .base import BaseStorage
from ..core.models import PegCheckPayload, PegReport, PegStatus

logger = logging.getLogger(__name__)

class PostgreSQLStorage(BaseStorage):
    """PostgreSQL/TimescaleDB storage implementation"""
    
    def __init__(self, connection_string: Optional[str] = None):
        self.connection_string = connection_string or os.getenv(
            "POSTGRES_URL", 
            "postgresql://postgres:password@localhost:5432/pegcheck"
        )
        self.pool = None
        
    async def initialize(self):
        """Initialize database connection pool and create tables"""
        try:
            self.pool = await asyncpg.create_pool(
                self.connection_string,
                min_size=2,
                max_size=10,
                command_timeout=30
            )
            
            # Create tables if they don't exist
            await self._create_tables()
            
            logger.info("PostgreSQL storage initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQL storage: {e}")
            raise
    
    async def _create_tables(self):
        """Create database tables with TimescaleDB hypertables if available"""
        async with self.pool.acquire() as conn:
            # Create main peg_checks table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS peg_checks (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMPTZ NOT NULL,
                    as_of INTEGER NOT NULL,
                    symbols TEXT[] NOT NULL,
                    coingecko_data JSONB,
                    cryptocompare_data JSONB,
                    chainlink_data JSONB,
                    uniswap_data JSONB,
                    cefi_consistency JSONB,
                    config JSONB,
                    errors TEXT[],
                    created_at TIMESTAMPTZ DEFAULT NOW()
                )
            """)
            
            # Create peg_reports table for individual symbol reports  
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS peg_reports (
                    id SERIAL PRIMARY KEY,
                    peg_check_id INTEGER REFERENCES peg_checks(id),
                    timestamp TIMESTAMPTZ NOT NULL,
                    symbol VARCHAR(20) NOT NULL,
                    avg_ref DECIMAL(18, 8),
                    abs_diff DECIMAL(18, 8),
                    pct_diff DECIMAL(10, 6),
                    bps_diff DECIMAL(10, 2),
                    is_depeg BOOLEAN NOT NULL,
                    status VARCHAR(20) NOT NULL,
                    confidence DECIMAL(3, 2),
                    sources_used TEXT[],
                    report_timestamp INTEGER NOT NULL,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                )
            """)
            
            # Create source_metrics table for tracking source reliability
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS source_metrics (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMPTZ NOT NULL,
                    source VARCHAR(50) NOT NULL,
                    symbol VARCHAR(20) NOT NULL,
                    price DECIMAL(18, 8),
                    success BOOLEAN NOT NULL,
                    response_time_ms INTEGER,
                    error_message TEXT,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                )
            """)
            
            # Create indexes
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_peg_checks_timestamp 
                ON peg_checks(timestamp DESC)
            """)
            
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_peg_reports_symbol_timestamp 
                ON peg_reports(symbol, timestamp DESC)
            """)
            
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_source_metrics_source_symbol_timestamp
                ON source_metrics(source, symbol, timestamp DESC)
            """)
            
            # Try to create TimescaleDB hypertables (will fail silently if TimescaleDB not available)
            try:
                await conn.execute("""
                    SELECT create_hypertable('peg_checks', 'timestamp', if_not_exists => TRUE)
                """)
                await conn.execute("""
                    SELECT create_hypertable('peg_reports', 'timestamp', if_not_exists => TRUE)
                """)
                await conn.execute("""
                    SELECT create_hypertable('source_metrics', 'timestamp', if_not_exists => TRUE)
                """)
                logger.info("TimescaleDB hypertables created successfully")
            except Exception as e:
                logger.info(f"TimescaleDB not available or hypertables already exist: {e}")
    
    async def store_peg_check(self, payload: PegCheckPayload) -> bool:
        """Store a complete peg check payload"""
        if not self.pool:
            await self.initialize()
            
        try:
            async with self.pool.acquire() as conn:
                async with conn.transaction():
                    # Insert main peg check record
                    peg_check_id = await conn.fetchval("""
                        INSERT INTO peg_checks (
                            timestamp, as_of, symbols, coingecko_data, 
                            cryptocompare_data, chainlink_data, uniswap_data,
                            cefi_consistency, config, errors
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                        RETURNING id
                    """, 
                        datetime.fromtimestamp(payload.as_of),
                        payload.as_of,
                        payload.symbols,
                        json.dumps(payload.coingecko),
                        json.dumps(payload.cryptocompare),
                        json.dumps(payload.chainlink) if payload.chainlink else None,
                        json.dumps(payload.uniswap) if payload.uniswap else None,
                        json.dumps(payload.cefi_consistency),
                        json.dumps(payload.config) if payload.config else None,
                        payload.errors or []
                    )
                    
                    # Insert individual reports
                    for report in payload.reports:
                        await conn.execute("""
                            INSERT INTO peg_reports (
                                peg_check_id, timestamp, symbol, avg_ref, abs_diff,
                                pct_diff, bps_diff, is_depeg, status, confidence,
                                sources_used, report_timestamp
                            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                        """,
                            peg_check_id,
                            datetime.fromtimestamp(report.timestamp),
                            report.symbol,
                            float(report.avg_ref) if not str(report.avg_ref).lower() == 'nan' else None,
                            float(report.abs_diff) if not str(report.abs_diff).lower() == 'nan' else None,
                            float(report.pct_diff) if not str(report.pct_diff).lower() == 'nan' else None,
                            float(report.bps_diff) if not str(report.bps_diff).lower() == 'nan' else None,
                            report.is_depeg,
                            report.status.value,
                            float(report.confidence),
                            report.sources_used,
                            report.timestamp
                        )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to store peg check: {e}")
            return False
    
    async def get_peg_history(self, symbol: str, hours: int = 24) -> List[Tuple[datetime, float, str]]:
        """Get peg history for a symbol"""
        if not self.pool:
            await self.initialize()
            
        try:
            async with self.pool.acquire() as conn:
                since_time = datetime.utcnow() - timedelta(hours=hours)
                
                rows = await conn.fetch("""
                    SELECT timestamp, avg_ref, status
                    FROM peg_reports
                    WHERE symbol = $1 AND timestamp >= $2 AND avg_ref IS NOT NULL
                    ORDER BY timestamp ASC
                """, symbol, since_time)
                
                return [(row['timestamp'], float(row['avg_ref']), row['status']) for row in rows]
                
        except Exception as e:
            logger.error(f"Failed to get peg history for {symbol}: {e}")
            return []
    
    async def get_latest_peg_check(self, symbols: Optional[List[str]] = None) -> Optional[PegCheckPayload]:
        """Get the latest peg check data"""
        if not self.pool:
            await self.initialize()
            
        try:
            async with self.pool.acquire() as conn:
                # Get latest peg check
                row = await conn.fetchrow("""
                    SELECT * FROM peg_checks
                    ORDER BY timestamp DESC
                    LIMIT 1
                """)
                
                if not row:
                    return None
                
                # Get associated reports
                reports_rows = await conn.fetch("""
                    SELECT * FROM peg_reports
                    WHERE peg_check_id = $1
                    ORDER BY symbol
                """, row['id'])
                
                # Filter symbols if specified
                if symbols:
                    reports_rows = [r for r in reports_rows if r['symbol'] in symbols]
                
                # Reconstruct PegReport objects
                reports = []
                for r in reports_rows:
                    report = PegReport(
                        symbol=r['symbol'],
                        avg_ref=float(r['avg_ref']) if r['avg_ref'] else float('nan'),
                        abs_diff=float(r['abs_diff']) if r['abs_diff'] else float('nan'),
                        pct_diff=float(r['pct_diff']) if r['pct_diff'] else float('nan'),
                        bps_diff=float(r['bps_diff']) if r['bps_diff'] else float('nan'),
                        is_depeg=r['is_depeg'],
                        status=PegStatus(r['status']),
                        confidence=float(r['confidence']),
                        sources_used=r['sources_used'],
                        timestamp=r['report_timestamp']
                    )
                    reports.append(report)
                
                # Reconstruct PegCheckPayload
                payload = PegCheckPayload(
                    as_of=row['as_of'],
                    symbols=row['symbols'] if not symbols else symbols,
                    reports=reports,
                    coingecko=json.loads(row['coingecko_data']) if row['coingecko_data'] else {},
                    cryptocompare=json.loads(row['cryptocompare_data']) if row['cryptocompare_data'] else {},
                    chainlink=json.loads(row['chainlink_data']) if row['chainlink_data'] else None,
                    uniswap=json.loads(row['uniswap_data']) if row['uniswap_data'] else None,
                    cefi_consistency=json.loads(row['cefi_consistency']) if row['cefi_consistency'] else {},
                    config=json.loads(row['config']) if row['config'] else None,
                    errors=row['errors']
                )
                
                return payload
                
        except Exception as e:
            logger.error(f"Failed to get latest peg check: {e}")
            return None
    
    async def get_source_reliability(self, source: str, hours: int = 168) -> Dict[str, float]:
        """Get source reliability metrics"""
        if not self.pool:
            await self.initialize()
            
        try:
            async with self.pool.acquire() as conn:
                since_time = datetime.utcnow() - timedelta(hours=hours)
                
                rows = await conn.fetch("""
                    SELECT 
                        symbol,
                        COUNT(*) as total_requests,
                        SUM(CASE WHEN success THEN 1 ELSE 0 END) as successful_requests,
                        AVG(response_time_ms) as avg_response_time
                    FROM source_metrics
                    WHERE source = $1 AND timestamp >= $2
                    GROUP BY symbol
                """, source, since_time)
                
                reliability = {}
                for row in rows:
                    success_rate = row['successful_requests'] / row['total_requests'] if row['total_requests'] > 0 else 0
                    reliability[row['symbol']] = {
                        'success_rate': success_rate,
                        'avg_response_time_ms': float(row['avg_response_time']) if row['avg_response_time'] else 0,
                        'total_requests': row['total_requests']
                    }
                
                return reliability
                
        except Exception as e:
            logger.error(f"Failed to get source reliability for {source}: {e}")
            return {}
    
    async def cleanup_old_data(self, days_to_keep: int = 30) -> int:
        """Clean up old data"""
        if not self.pool:
            await self.initialize()
            
        try:
            async with self.pool.acquire() as conn:
                cutoff_time = datetime.utcnow() - timedelta(days=days_to_keep)
                
                # Delete old peg reports first (foreign key constraint)
                await conn.execute("""
                    DELETE FROM peg_reports
                    WHERE timestamp < $1
                """, cutoff_time)
                
                # Delete old peg checks
                result = await conn.fetchval("""
                    DELETE FROM peg_checks
                    WHERE timestamp < $1
                    RETURNING COUNT(*)
                """, cutoff_time)
                
                # Delete old source metrics
                await conn.execute("""
                    DELETE FROM source_metrics
                    WHERE timestamp < $1
                """, cutoff_time)
                
                return result or 0
                
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")
            return 0
    
    async def health_check(self) -> Dict[str, any]:
        """Check storage backend health"""
        if not self.pool:
            try:
                await self.initialize()
            except Exception as e:
                return {
                    "status": "error",
                    "backend": "postgresql",
                    "error": str(e),
                    "connected": False
                }
        
        try:
            async with self.pool.acquire() as conn:
                # Test connection
                await conn.fetchval("SELECT 1")
                
                # Get database info
                db_version = await conn.fetchval("SELECT version()")
                
                # Check if TimescaleDB is available
                timescale_available = False
                try:
                    await conn.fetchval("SELECT extversion FROM pg_extension WHERE extname = 'timescaledb'")
                    timescale_available = True
                except:
                    pass
                
                # Get record counts
                peg_checks_count = await conn.fetchval("SELECT COUNT(*) FROM peg_checks")
                peg_reports_count = await conn.fetchval("SELECT COUNT(*) FROM peg_reports")
                
                return {
                    "status": "healthy",
                    "backend": "postgresql",
                    "connected": True,
                    "database_version": db_version,
                    "timescaledb_available": timescale_available,
                    "records": {
                        "peg_checks": peg_checks_count,
                        "peg_reports": peg_reports_count
                    },
                    "connection_pool": {
                        "size": self.pool.get_size(),
                        "idle": self.pool.get_idle_size()
                    }
                }
                
        except Exception as e:
            return {
                "status": "error",
                "backend": "postgresql",
                "error": str(e),
                "connected": False
            }
    
    async def close(self):
        """Close database connections"""
        if self.pool:
            await self.pool.close()