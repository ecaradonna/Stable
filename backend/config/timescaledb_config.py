"""
TimescaleDB Configuration for StableYield Index Production Pipeline
Handles time-series database setup, table creation, and optimization
"""

import os
import asyncio
import logging
from typing import Dict, List, Optional
import asyncpg
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class TimescaleDBConfig:
    """TimescaleDB configuration and connection management"""
    
    def __init__(self):
        self.host = os.getenv('TIMESCALEDB_HOST', 'localhost')
        self.port = int(os.getenv('TIMESCALEDB_PORT', '5432'))
        self.database = os.getenv('TIMESCALEDB_DATABASE', 'stableyield')
        self.username = os.getenv('TIMESCALEDB_USER', 'postgres')
        self.password = os.getenv('TIMESCALEDB_PASSWORD', 'password')
        self.pool = None
    
    def get_connection_string(self) -> str:
        """Get PostgreSQL connection string"""
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
    
    async def create_connection_pool(self, min_size: int = 5, max_size: int = 20):
        """Create asyncpg connection pool"""
        try:
            self.pool = await asyncpg.create_pool(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.username,
                password=self.password,
                min_size=min_size,
                max_size=max_size,
                command_timeout=60
            )
            logger.info("✅ TimescaleDB connection pool created")
            return self.pool
        except Exception as e:
            logger.error(f"❌ Failed to create TimescaleDB connection pool: {e}")
            raise
    
    async def close_connection_pool(self):
        """Close connection pool"""
        if self.pool:
            await self.pool.close()
            logger.info("✅ TimescaleDB connection pool closed")

# SQL schema definitions for production time-series tables
TIMESCALE_SCHEMA = {
    "extensions": [
        "CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;",
        "CREATE EXTENSION IF NOT EXISTS pg_stat_statements;"
    ],
    
    "tables": {
        "index_values": """
            CREATE TABLE IF NOT EXISTS index_values (
                timestamp TIMESTAMPTZ NOT NULL,
                index_id VARCHAR(10) NOT NULL,
                value NUMERIC(10,6) NOT NULL,
                methodology_version VARCHAR(10) NOT NULL DEFAULT '1.0',
                metadata JSONB,
                constituent_count INTEGER,
                total_market_cap NUMERIC(18,2),
                calculation_duration_ms INTEGER,
                PRIMARY KEY (timestamp, index_id)
            );
        """,
        
        "ray_observations": """
            CREATE TABLE IF NOT EXISTS ray_observations (
                timestamp TIMESTAMPTZ NOT NULL,
                symbol VARCHAR(10) NOT NULL,
                raw_apy NUMERIC(8,4) NOT NULL,
                peg_score NUMERIC(5,4) NOT NULL CHECK (peg_score >= 0 AND peg_score <= 1),
                liquidity_score NUMERIC(5,4) NOT NULL CHECK (liquidity_score >= 0 AND liquidity_score <= 1),
                counterparty_score NUMERIC(5,4) NOT NULL CHECK (counterparty_score >= 0 AND counterparty_score <= 1),
                ray NUMERIC(8,4) NOT NULL,
                data_sources JSONB,
                PRIMARY KEY (timestamp, symbol)
            );
        """,
        
        "constituents": """
            CREATE TABLE IF NOT EXISTS constituents (
                timestamp TIMESTAMPTZ NOT NULL,
                symbol VARCHAR(10) NOT NULL,
                name VARCHAR(50) NOT NULL,
                market_cap NUMERIC(15,2) NOT NULL,
                weight NUMERIC(8,6) NOT NULL CHECK (weight >= 0 AND weight <= 1),
                price NUMERIC(12,6),
                circulating_supply NUMERIC(18,2),
                PRIMARY KEY (timestamp, symbol)
            );
        """,
        
        "price_data": """
            CREATE TABLE IF NOT EXISTS price_data (
                timestamp TIMESTAMPTZ NOT NULL,
                symbol VARCHAR(10) NOT NULL,
                venue VARCHAR(20) NOT NULL,
                price NUMERIC(12,6) NOT NULL,
                volume_24h NUMERIC(18,2),
                change_24h NUMERIC(8,4),
                bid NUMERIC(12,6),
                ask NUMERIC(12,6),
                spread_bps NUMERIC(8,2),
                PRIMARY KEY (timestamp, symbol, venue)
            );
        """,
        
        "liquidity_metrics": """
            CREATE TABLE IF NOT EXISTS liquidity_metrics (
                timestamp TIMESTAMPTZ NOT NULL,
                symbol VARCHAR(10) NOT NULL,
                venue VARCHAR(20) NOT NULL,
                depth_10bps NUMERIC(18,2),
                depth_50bps NUMERIC(18,2),
                depth_100bps NUMERIC(18,2),
                effective_spread NUMERIC(8,4),
                impact_1m NUMERIC(8,4),
                impact_5m NUMERIC(8,4),
                liquidity_score NUMERIC(5,4),
                PRIMARY KEY (timestamp, symbol, venue)
            );
        """,
        
        "peg_stability": """
            CREATE TABLE IF NOT EXISTS peg_stability (
                timestamp TIMESTAMPTZ NOT NULL,
                symbol VARCHAR(10) NOT NULL,
                price_deviation NUMERIC(8,6),
                volatility_1h NUMERIC(8,6),
                volatility_24h NUMERIC(8,6),
                deviation_duration_minutes INTEGER,
                max_deviation_24h NUMERIC(8,6),
                peg_score NUMERIC(5,4),
                PRIMARY KEY (timestamp, symbol)
            );
        """,
        
        "apy_sources": """
            CREATE TABLE IF NOT EXISTS apy_sources (
                timestamp TIMESTAMPTZ NOT NULL,
                symbol VARCHAR(10) NOT NULL,
                protocol VARCHAR(30) NOT NULL,
                apy NUMERIC(8,4) NOT NULL,
                tvl NUMERIC(18,2),
                pool_address VARCHAR(50),
                risk_score NUMERIC(5,4),
                chain VARCHAR(20),
                PRIMARY KEY (timestamp, symbol, protocol)
            );
        """,
        
        "tbill_rates": """
            CREATE TABLE IF NOT EXISTS tbill_rates (
                timestamp TIMESTAMPTZ NOT NULL,
                maturity VARCHAR(10) NOT NULL,
                rate NUMERIC(6,4) NOT NULL,
                source VARCHAR(20) NOT NULL DEFAULT 'FRED',
                PRIMARY KEY (timestamp, maturity)
            );
        """
    },
    
    "hypertables": [
        "SELECT create_hypertable('index_values', 'timestamp', if_not_exists => TRUE);",
        "SELECT create_hypertable('ray_observations', 'timestamp', if_not_exists => TRUE);",
        "SELECT create_hypertable('constituents', 'timestamp', if_not_exists => TRUE);",
        "SELECT create_hypertable('price_data', 'timestamp', if_not_exists => TRUE);",
        "SELECT create_hypertable('liquidity_metrics', 'timestamp', if_not_exists => TRUE);",
        "SELECT create_hypertable('peg_stability', 'timestamp', if_not_exists => TRUE);",
        "SELECT create_hypertable('apy_sources', 'timestamp', if_not_exists => TRUE);",
        "SELECT create_hypertable('tbill_rates', 'timestamp', if_not_exists => TRUE);"
    ],
    
    "indexes": [
        "CREATE INDEX IF NOT EXISTS idx_index_values_id ON index_values (index_id, timestamp DESC);",
        "CREATE INDEX IF NOT EXISTS idx_ray_observations_symbol ON ray_observations (symbol, timestamp DESC);",
        "CREATE INDEX IF NOT EXISTS idx_constituents_symbol ON constituents (symbol, timestamp DESC);",
        "CREATE INDEX IF NOT EXISTS idx_price_data_symbol_venue ON price_data (symbol, venue, timestamp DESC);",
        "CREATE INDEX IF NOT EXISTS idx_liquidity_metrics_symbol ON liquidity_metrics (symbol, timestamp DESC);",
        "CREATE INDEX IF NOT EXISTS idx_peg_stability_symbol ON peg_stability (symbol, timestamp DESC);",
        "CREATE INDEX IF NOT EXISTS idx_apy_sources_symbol_protocol ON apy_sources (symbol, protocol, timestamp DESC);",
        "CREATE INDEX IF NOT EXISTS idx_tbill_rates_maturity ON tbill_rates (maturity, timestamp DESC);"
    ],
    
    "retention_policies": [
        # Keep raw price data for 90 days
        "SELECT add_retention_policy('price_data', INTERVAL '90 days');",
        
        # Keep liquidity metrics for 180 days
        "SELECT add_retention_policy('liquidity_metrics', INTERVAL '180 days');",
        
        # Keep index values forever (these are the core product)
        # No retention policy for index_values, ray_observations, constituents
        
        # Keep APY sources for 1 year
        "SELECT add_retention_policy('apy_sources', INTERVAL '365 days');",
        
        # Keep T-Bill rates for 5 years
        "SELECT add_retention_policy('tbill_rates', INTERVAL '1825 days');"
    ],
    
    "continuous_aggregates": [
        # 5-minute aggregates for price data
        """
        CREATE MATERIALIZED VIEW IF NOT EXISTS price_data_5m
        WITH (timescaledb.continuous) AS
        SELECT 
            time_bucket('5 minutes', timestamp) AS bucket,
            symbol,
            venue,
            AVG(price) as avg_price,
            MAX(price) as high_price,
            MIN(price) as low_price,
            LAST(price, timestamp) as close_price,
            SUM(volume_24h) as total_volume
        FROM price_data
        GROUP BY bucket, symbol, venue;
        """,
        
        # Hourly index statistics
        """
        CREATE MATERIALIZED VIEW IF NOT EXISTS index_values_1h
        WITH (timescaledb.continuous) AS
        SELECT 
            time_bucket('1 hour', timestamp) AS bucket,
            index_id,
            AVG(value) as avg_value,
            MAX(value) as max_value,
            MIN(value) as min_value,
            LAST(value, timestamp) as close_value,
            STDDEV(value) as volatility
        FROM index_values
        GROUP BY bucket, index_id;
        """,
        
        # Daily risk metrics summary
        """
        CREATE MATERIALIZED VIEW IF NOT EXISTS risk_metrics_daily
        WITH (timescaledb.continuous) AS
        SELECT 
            time_bucket('1 day', timestamp) AS bucket,
            symbol,
            AVG(peg_score) as avg_peg_score,
            MIN(peg_score) as min_peg_score,
            AVG(liquidity_score) as avg_liquidity_score,
            MIN(liquidity_score) as min_liquidity_score,
            AVG(counterparty_score) as avg_counterparty_score,
            AVG(ray) as avg_ray
        FROM ray_observations
        GROUP BY bucket, symbol;
        """
    ]
}

class TimescaleDBMigration:
    """Handle database migration and setup"""
    
    def __init__(self, config: TimescaleDBConfig):
        self.config = config
    
    async def run_migration(self):
        """Run complete database migration"""
        try:
            pool = await self.config.create_connection_pool()
            
            async with pool.acquire() as conn:
                logger.info("🚀 Starting TimescaleDB migration...")
                
                # Create extensions
                await self._create_extensions(conn)
                
                # Create tables
                await self._create_tables(conn)
                
                # Create hypertables
                await self._create_hypertables(conn)
                
                # Create indexes
                await self._create_indexes(conn)
                
                # Set up retention policies
                await self._setup_retention_policies(conn)
                
                # Create continuous aggregates
                await self._create_continuous_aggregates(conn)
                
                logger.info("✅ TimescaleDB migration completed successfully")
                
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            raise
        finally:
            await self.config.close_connection_pool()
    
    async def _create_extensions(self, conn):
        """Create required PostgreSQL extensions"""
        for ext_sql in TIMESCALE_SCHEMA["extensions"]:
            try:
                await conn.execute(ext_sql)
                logger.info(f"✅ Extension created: {ext_sql[:50]}...")
            except Exception as e:
                logger.warning(f"⚠️ Extension creation failed: {e}")
    
    async def _create_tables(self, conn):
        """Create all tables"""
        for table_name, table_sql in TIMESCALE_SCHEMA["tables"].items():
            try:
                await conn.execute(table_sql)
                logger.info(f"✅ Table created: {table_name}")
            except Exception as e:
                logger.error(f"❌ Failed to create table {table_name}: {e}")
                raise
    
    async def _create_hypertables(self, conn):
        """Convert tables to hypertables"""
        for hypertable_sql in TIMESCALE_SCHEMA["hypertables"]:
            try:
                await conn.execute(hypertable_sql)
                logger.info(f"✅ Hypertable created: {hypertable_sql[:50]}...")
            except Exception as e:
                logger.warning(f"⚠️ Hypertable creation skipped (may already exist): {e}")
    
    async def _create_indexes(self, conn):
        """Create indexes for optimal query performance"""
        for index_sql in TIMESCALE_SCHEMA["indexes"]:
            try:
                await conn.execute(index_sql)
                logger.info(f"✅ Index created: {index_sql[:50]}...")
            except Exception as e:
                logger.warning(f"⚠️ Index creation skipped: {e}")
    
    async def _setup_retention_policies(self, conn):
        """Set up data retention policies"""
        for retention_sql in TIMESCALE_SCHEMA["retention_policies"]:
            try:
                await conn.execute(retention_sql)
                logger.info(f"✅ Retention policy set: {retention_sql[:50]}...")
            except Exception as e:
                logger.warning(f"⚠️ Retention policy skipped: {e}")
    
    async def _create_continuous_aggregates(self, conn):
        """Create continuous aggregates for performance"""
        for agg_sql in TIMESCALE_SCHEMA["continuous_aggregates"]:
            try:
                await conn.execute(agg_sql)
                logger.info(f"✅ Continuous aggregate created: {agg_sql[:50]}...")
            except Exception as e:
                logger.warning(f"⚠️ Continuous aggregate skipped: {e}")

# Utility functions for database operations
async def get_index_history(pool, index_id: str = "SYI", hours: int = 24) -> List[Dict]:
    """Get index history from TimescaleDB"""
    query = """
    SELECT timestamp, value, metadata
    FROM index_values
    WHERE index_id = $1 
    AND timestamp >= NOW() - INTERVAL '%s hours'
    ORDER BY timestamp DESC
    LIMIT 1000;
    """ % hours
    
    async with pool.acquire() as conn:
        rows = await conn.fetch(query, index_id)
        return [dict(row) for row in rows]

async def get_latest_ray_observations(pool) -> List[Dict]:
    """Get latest RAY observations for all symbols"""
    query = """
    SELECT DISTINCT ON (symbol) 
        symbol, ray, peg_score, liquidity_score, counterparty_score, timestamp
    FROM ray_observations
    ORDER BY symbol, timestamp DESC;
    """
    
    async with pool.acquire() as conn:
        rows = await conn.fetch(query)
        return [dict(row) for row in rows]

# TODO: PRODUCTION DEPLOYMENT CHECKLIST
# 1. Install TimescaleDB: https://docs.timescale.com/install/
# 2. Set proper environment variables for connection
# 3. Run migration script: python -m backend.config.timescaledb_config
# 4. Set up monitoring for database performance
# 5. Configure backup and disaster recovery
# 6. Tune PostgreSQL parameters for time-series workload
# 7. Set up connection pooling (PgBouncer recommended)
# 8. Monitor disk usage and plan for data growth