# PegCheck Enhanced Setup Guide - Phase 3 Data Persistence

This guide covers setting up the enhanced PegCheck system with comprehensive data persistence, analytics, and job scheduling.

## Overview

PegCheck Phase 3 provides:
- **Multi-source data integration**: CoinGecko, CryptoCompare, Chainlink, Uniswap v3 TWAP
- **Comprehensive data persistence**: PostgreSQL/TimescaleDB with memory fallback
- **Advanced analytics**: Trend analysis, market stability reports, risk scoring
- **Automated job scheduling**: Periodic peg checks, data cleanup, health monitoring

## Quick Start (Memory Storage)

The system works out-of-the-box with in-memory storage for development and testing:

```bash
# Test the enhanced system
curl "http://localhost:8001/api/peg/check?symbols=USDT,USDC,DAI&with_oracle=false&with_dex=false"

# Check storage health
curl "http://localhost:8001/api/peg/storage/health"

# View data sources status
curl "http://localhost:8001/api/peg/sources"
```

## Production Setup with PostgreSQL/TimescaleDB

### 1. Install PostgreSQL and TimescaleDB

**Ubuntu/Debian:**
```bash
# Install PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib

# Install TimescaleDB (optional but recommended)
echo "deb https://packagecloud.io/timescale/timescaledb/ubuntu/ $(lsb_release -c -s) main" | sudo tee /etc/apt/sources.list.d/timescaledb.list
wget --quiet -O - https://packagecloud.io/timescale/timescaledb/gpgkey | sudo apt-key add -
sudo apt update
sudo apt install timescaledb-2-postgresql-14
```

**macOS:**
```bash
# Using Homebrew
brew install postgresql
brew install timescaledb

# Start PostgreSQL
brew services start postgresql
```

**Docker:**
```bash
# Run TimescaleDB container
docker run -d --name timescaledb \
  -p 5432:5432 \
  -e POSTGRES_PASSWORD=password \
  timescale/timescaledb:latest-pg14
```

### 2. Create Database and User

```bash
# Connect to PostgreSQL
sudo -u postgres psql

# Create database and user
CREATE DATABASE pegcheck_db;
CREATE USER pegcheck_user WITH ENCRYPTED PASSWORD 'secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE pegcheck_db TO pegcheck_user;

# Enable TimescaleDB extension (if installed)
\c pegcheck_db;
CREATE EXTENSION IF NOT EXISTS timescaledb;

\q
```

### 3. Install Python Dependencies

```bash
# Install asyncpg for PostgreSQL connectivity
pip install asyncpg

# Or add to requirements.txt
echo "asyncpg>=0.28.0" >> requirements.txt
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Update `/app/backend/.env`:

```env
# PostgreSQL Configuration
POSTGRES_URL=postgresql://pegcheck_user:secure_password_here@localhost:5432/pegcheck_db

# Optional: Ethereum RPC for Chainlink/Uniswap (get from Infura, Alchemy, etc.)
ETH_RPC_URL=https://mainnet.infura.io/v3/YOUR_PROJECT_ID

# CryptoCompare API Key (already configured)
CRYPTOCOMPARE_API_KEY=49c985fa050c7ccc690c410257fdb403b752f38154e4c7e491ae2512029acf19
```

### 5. Test the Setup

```bash
# Restart the backend to pick up new configuration
sudo supervisorctl restart backend

# Test PostgreSQL connection
curl "http://localhost:8001/api/peg/storage/health"

# Run a comprehensive peg check with storage
curl "http://localhost:8001/api/peg/check?symbols=USDT,USDC,DAI&store_result=true"

# Check historical data
curl "http://localhost:8001/api/peg/history/USDT?hours=24"
```

## Enhanced Features

### Multi-Source Peg Analysis

```bash
# Basic analysis (CoinGecko + CryptoCompare)
curl "http://localhost:8001/api/peg/check?symbols=USDT,USDC,DAI"

# With Chainlink oracles (requires ETH_RPC_URL)
curl "http://localhost:8001/api/peg/check?symbols=USDT,USDC&with_oracle=true"

# With Uniswap v3 TWAP (requires ETH_RPC_URL)
curl "http://localhost:8001/api/peg/check?symbols=USDT,USDC&with_dex=true"

# Full multi-source analysis
curl "http://localhost:8001/api/peg/check?symbols=USDT,USDC,DAI&with_oracle=true&with_dex=true&store_result=true"
```

### Advanced Analytics

```bash
# Symbol trend analysis
curl "http://localhost:8001/api/peg/analytics/trends/USDT?hours=168"

# Market stability report
curl "http://localhost:8001/api/peg/analytics/market-stability?symbols=USDT,USDC,DAI,FRAX&hours=168"
```

### Job Management

```bash
# Manual peg check job
curl -X POST "http://localhost:8001/api/peg/jobs/run-peg-check?with_oracle=true&with_dex=true"

# Data cleanup
curl -X POST "http://localhost:8001/api/peg/jobs/cleanup?days_to_keep=30"
```

## API Endpoints Summary

### Core PegCheck Endpoints
- `GET /api/peg/health` - Service health check
- `GET /api/peg/check` - Enhanced peg analysis with multi-source support
- `GET /api/peg/summary` - Quick market overview
- `GET /api/peg/symbols` - Supported symbols
- `GET /api/peg/thresholds` - Peg monitoring configuration

### Enhanced Data Sources
- `GET /api/peg/sources` - Data source health and configuration
- `GET /api/peg/history/{symbol}` - Historical peg data
- `GET /api/peg/storage/health` - Storage backend status

### Analytics (Phase 3)
- `GET /api/peg/analytics/trends/{symbol}` - Symbol trend analysis
- `GET /api/peg/analytics/market-stability` - Market stability report

### Job Management (Phase 3)
- `POST /api/peg/jobs/run-peg-check` - Manual peg check execution
- `POST /api/peg/jobs/cleanup` - Data cleanup job

## Configuration Options

### Data Sources
- **CoinGecko**: Always enabled (primary CeFi source)
- **CryptoCompare**: Always enabled (secondary CeFi source, requires API key)
- **Chainlink**: Optional (requires ETH_RPC_URL)
- **Uniswap v3**: Optional (requires ETH_RPC_URL)

### Storage Backends
- **Memory**: Default, no configuration needed
- **PostgreSQL**: Production-grade, requires POSTGRES_URL
- **TimescaleDB**: Enhanced PostgreSQL for time-series data

### Thresholds
- **Warning**: 25 basis points (0.25%)
- **Depeg**: 50 basis points (0.50%)
- **Target Price**: $1.00

## Monitoring and Alerts

The system provides comprehensive monitoring:

1. **Real-time Peg Status**: Traffic light indicators (🟢🟡🔴)
2. **Historical Trends**: Price volatility, deviation episodes, stability grades
3. **Market Health**: Overall market assessment, risk scoring
4. **Data Source Reliability**: Uptime, response times, error rates
5. **Storage Health**: Connection status, record counts, performance metrics

## Troubleshooting

### Common Issues

**Storage connection fails:**
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Test connection manually
psql -h localhost -U pegcheck_user -d pegcheck_db -c "SELECT version();"
```

**Chainlink/Uniswap data not available:**
- Ensure ETH_RPC_URL is configured
- Check RPC endpoint is accessible
- Verify network connectivity

**High memory usage:**
- Configure PostgreSQL storage to persist data
- Adjust memory storage max_records limit
- Run regular cleanup jobs

### Logs

Check application logs for detailed information:
```bash
# Backend logs
tail -f /var/log/supervisor/backend.out.log

# PegCheck specific logs
grep "pegcheck" /var/log/supervisor/backend.out.log
```

## Production Recommendations

1. **Use PostgreSQL/TimescaleDB** for data persistence
2. **Configure ETH_RPC_URL** for maximum data source diversity
3. **Set up regular backups** of the pegcheck database
4. **Monitor storage usage** and run cleanup jobs regularly
5. **Set up alerting** for peg deviation events
6. **Use load balancing** for high-availability deployments

## Performance Optimization

- **Database Indexing**: Automatically created for time-series queries
- **Connection Pooling**: Built-in with asyncpg
- **Caching**: In-memory caching for recent peg checks
- **Batch Operations**: Efficient bulk data operations
- **Async Processing**: Non-blocking I/O for all operations

This completes the Phase 3 enhanced PegCheck system with comprehensive data persistence, analytics, and production-ready capabilities.