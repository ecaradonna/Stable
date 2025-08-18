# StableYield Index - Production Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying the StableYield Index production architecture, transforming the current MVP into an institutional-grade system.

## 🎯 Current Status vs Production Target

### ✅ Current MVP (Phase 1)
- **Index Calculation**: 1-minute updates via Python APScheduler  
- **Data Sources**: Demo APIs (CryptoCompare, DefiLlama, Binance demo)
- **Storage**: MongoDB time-series collections
- **API**: REST endpoints (`/api/index/*`)
- **Frontend**: Live ticker + dashboard
- **Performance**: 0.9158% current index value, 6 constituents

### 🚀 Production Target (Phase 2)
- **Real-time Pipeline**: Kafka + Flink/Spark streaming
- **Data Sources**: Production APIs + WebSocket streams
- **Storage**: TimescaleDB + ClickHouse + IPFS audit trail
- **API**: REST + WebSocket streaming
- **Observability**: Full monitoring stack
- **Performance**: Sub-second latency, 99.9% availability

## 📋 Infrastructure Requirements

### Minimum Production Setup
```yaml
Kafka Cluster:
  - 3 brokers (4 CPU, 16GB RAM, 500GB SSD each)
  - Zookeeper: 3 nodes (2 CPU, 8GB RAM, 100GB SSD each)

Flink Cluster:
  - JobManager: 1 node (4 CPU, 8GB RAM, 100GB SSD)
  - TaskManager: 3 nodes (8 CPU, 16GB RAM, 200GB SSD each)

Databases:
  - TimescaleDB: 1 primary + 1 replica (8 CPU, 32GB RAM, 1TB SSD each)
  - ClickHouse: 3 nodes (8 CPU, 32GB RAM, 2TB SSD each)

API Layer:
  - FastAPI: 3 instances (4 CPU, 8GB RAM each)
  - WebSocket: 2 instances (4 CPU, 8GB RAM each)
  - Load Balancer: 1 node (2 CPU, 4GB RAM)

Monitoring:
  - Prometheus: 1 node (4 CPU, 16GB RAM, 500GB SSD)
  - Grafana: 1 node (2 CPU, 8GB RAM, 100GB SSD)
  - ELK Stack: 3 nodes (4 CPU, 16GB RAM, 1TB SSD each)
```

## 🚀 Deployment Steps

### Step 1: Infrastructure Setup

#### 1.1 Kafka Cluster Deployment
```bash
# Deploy Kafka using Confluent Platform
kubectl apply -f k8s/kafka/
kubectl apply -f k8s/zookeeper/

# Create topics
kafka-topics --bootstrap-server kafka:9092 --create --topic cc.prices --partitions 12 --replication-factor 3
kafka-topics --bootstrap-server kafka:9092 --create --topic cc.orderbook --partitions 12 --replication-factor 3
kafka-topics --bootstrap-server kafka:9092 --create --topic dl.apy --partitions 6 --replication-factor 3
kafka-topics --bootstrap-server kafka:9092 --create --topic ex.mktcap --partitions 3 --replication-factor 3
kafka-topics --bootstrap-server kafka:9092 --create --topic trad.tbill --partitions 1 --replication-factor 3
kafka-topics --bootstrap-server kafka:9092 --create --topic syi.calculated --partitions 1 --replication-factor 3
```

#### 1.2 Database Setup
```bash
# Deploy TimescaleDB
kubectl apply -f k8s/timescaledb/
python -c "from backend.config.timescaledb_config import TimescaleDBMigration, TimescaleDBConfig; 
import asyncio; 
asyncio.run(TimescaleDBMigration(TimescaleDBConfig()).run_migration())"

# Deploy ClickHouse
kubectl apply -f k8s/clickhouse/
clickhouse-client --query "CREATE DATABASE stableyield_analytics"
```

#### 1.3 Flink Cluster Deployment
```bash
# Deploy Flink
kubectl apply -f k8s/flink/
kubectl port-forward svc/flink-jobmanager 8081:8081

# Submit streaming jobs
flink run --class com.stableyield.PegStabilityProcessor jobs/peg-stability-processor.jar
flink run --class com.stableyield.LiquidityMetricsProcessor jobs/liquidity-metrics-processor.jar
flink run --class com.stableyield.RAYCalculator jobs/ray-calculator.jar
flink run --class com.stableyield.SYIIndexCalculator jobs/syi-index-calculator.jar
```

### Step 2: Data Pipeline Setup

#### 2.1 External API Integration
```bash
# Set up production API keys
kubectl create secret generic api-keys \
  --from-literal=BINANCE_API_KEY=${BINANCE_API_KEY} \
  --from-literal=BINANCE_API_SECRET=${BINANCE_API_SECRET} \
  --from-literal=CC_API_KEY_STABLEYIELD=${CC_API_KEY_STABLEYIELD} \
  --from-literal=FRED_API_KEY=${FRED_API_KEY}

# Deploy ingestion services
kubectl apply -f k8s/ingestion/
```

#### 2.2 WebSocket Streaming
```bash
# Deploy WebSocket servers
kubectl apply -f k8s/websocket/
kubectl expose deployment websocket-server --port=8002 --type=LoadBalancer
```

### Step 3: Monitoring & Observability

#### 3.1 Prometheus Setup
```bash
# Deploy Prometheus
kubectl apply -f k8s/monitoring/prometheus/
kubectl apply -f k8s/monitoring/grafana/

# Import dashboards
curl -X POST \
  http://grafana:3000/api/dashboards/db \
  -H 'Content-Type: application/json' \
  -d @monitoring/dashboards/stableyield-index.json
```

#### 3.2 Logging Setup
```bash
# Deploy ELK Stack
kubectl apply -f k8s/logging/elasticsearch/
kubectl apply -f k8s/logging/logstash/
kubectl apply -f k8s/logging/kibana/
```

### Step 4: API & Frontend Deployment

#### 4.1 API Deployment
```bash
# Deploy FastAPI services
kubectl apply -f k8s/api/
kubectl apply -f k8s/ingress/

# Configure auto-scaling
kubectl autoscale deployment api-server --cpu-percent=70 --min=3 --max=10
```

#### 4.2 Frontend Deployment
```bash
# Build and deploy React frontend
docker build -t stableyield/frontend:v2.0.0 frontend/
kubectl apply -f k8s/frontend/
```

## 📊 Monitoring & Alerting

### Key Metrics to Monitor

#### SYI Index Metrics
```yaml
- syi_calculation_latency_p95 < 5s
- syi_freshness < 90s
- syi_accuracy_deviation < 0.1%
- constituent_data_completeness > 95%
```

#### Infrastructure Metrics
```yaml
- kafka_consumer_lag < 1000 messages
- flink_checkpoint_duration < 30s
- timescaledb_connection_pool_usage < 80%
- api_response_time_p95 < 500ms
- websocket_active_connections
```

#### Business Metrics
```yaml
- index_updates_per_minute
- websocket_subscribers
- api_requests_per_second
- data_quality_score
```

### Alert Configuration
```yaml
SYI Index Stale:
  condition: syi_freshness > 300s
  severity: critical
  action: page_oncall

High Consumer Lag:
  condition: kafka_consumer_lag > 5000
  severity: warning
  action: slack_notification

Database Connection Issues:
  condition: db_connection_errors > 10/5m
  severity: critical
  action: auto_restart_service
```

## 🔒 Security & Compliance

### Security Configuration
```bash
# Enable TLS for all services
kubectl apply -f k8s/security/tls-certificates.yaml

# Set up RBAC
kubectl apply -f k8s/security/rbac.yaml

# Configure network policies
kubectl apply -f k8s/security/network-policies.yaml
```

### Data Protection
- Encryption at rest (AES-256)
- TLS 1.3 for data in transit
- API authentication (JWT + API keys)
- Rate limiting and DDoS protection

## 🔄 Migration Strategy

### Phase 1: Parallel Deployment
1. Deploy production pipeline alongside current MVP
2. Run both systems in parallel for 2 weeks
3. Compare outputs for consistency and accuracy
4. Gradually route traffic to production system

### Phase 2: Cutover
1. Start routing 10% of traffic to production
2. Monitor for 48 hours, increase to 50%
3. Monitor for 24 hours, increase to 100%
4. Decommission MVP system after 1 week

### Phase 3: Optimization
1. Fine-tune streaming job parameters
2. Optimize database queries and indexes
3. Implement advanced caching strategies
4. Add machine learning enhancements

## 📈 Scaling Considerations

### Auto-Scaling Configuration
```yaml
HPA (Horizontal Pod Autoscaler):
  - API servers: CPU > 70%
  - WebSocket servers: Connection count > 1000
  - Ingestion services: Message lag > 1000

VPA (Vertical Pod Autoscaler):
  - Flink TaskManagers: Memory usage optimization
  - Database pods: Resource optimization
```

### Performance Targets
- **Latency**: p95 < 100ms for API calls
- **Throughput**: 10k+ requests/second
- **Availability**: 99.9% uptime
- **Data Freshness**: < 60 seconds for index updates

## 🚨 Disaster Recovery

### Backup Strategy
```bash
# Database backups
pg_dump -h timescaledb -U postgres stableyield > backup-$(date +%Y%m%d).sql
clickhouse-backup create backup-$(date +%Y%m%d)

# Kafka topic backups
kafka-mirror-maker --consumer.config consumer.properties --producer.config producer.properties --whitelist=".*"

# Application state backups
flink savepoint create job-id s3://stableyield-savepoints/
```

### Recovery Procedures
1. **Database Recovery**: Restore from latest backup + WAL replay
2. **Kafka Recovery**: Restore topics from backup cluster
3. **Flink Recovery**: Resume from latest savepoint
4. **Application Recovery**: Deploy from versioned containers

## 📋 Production Readiness Checklist

### Pre-Production
- [ ] Load testing completed (10x expected traffic)
- [ ] Security audit passed
- [ ] Disaster recovery tested
- [ ] Monitoring and alerting configured
- [ ] Documentation updated
- [ ] Team training completed

### Go-Live
- [ ] Production data sources configured
- [ ] API keys and certificates installed
- [ ] Monitoring dashboards operational
- [ ] Support procedures documented
- [ ] Rollback plan tested

### Post-Production
- [ ] Performance metrics within SLAs
- [ ] No critical alerts for 48 hours
- [ ] Data quality validation passed
- [ ] User acceptance testing completed

## 🔧 Troubleshooting Guide

### Common Issues

#### Index Calculation Delays
```bash
# Check Flink job status
kubectl logs -f deployment/flink-taskmanager
flink list -r

# Check Kafka consumer lag
kafka-consumer-groups --bootstrap-server kafka:9092 --describe --group syi-calculator
```

#### WebSocket Connection Issues
```bash
# Check WebSocket server logs
kubectl logs -f deployment/websocket-server

# Test WebSocket connectivity
wscat -c ws://stableyield.com/stream/syi/live
```

#### Database Performance Issues
```bash
# Check TimescaleDB performance
psql -h timescaledb -c "SELECT * FROM pg_stat_activity WHERE state = 'active';"

# Check ClickHouse performance  
clickhouse-client --query "SHOW PROCESSLIST"
```

## 📞 Support & Maintenance

### 24/7 Operations
- **Monitoring**: Grafana dashboards + PagerDuty alerts
- **Logs**: Centralized logging via ELK stack
- **Metrics**: Prometheus + custom business metrics
- **Health Checks**: Automated health checks every 30 seconds

### Maintenance Windows
- **Database maintenance**: Sunday 2-4 AM UTC
- **Kafka maintenance**: Sunday 4-6 AM UTC
- **Application deployments**: Blue-green deployments (zero downtime)

---

**Production Deployment Timeline**: 6-8 weeks
**Go-Live Target**: Q2 2025  
**Migration Completion**: Q3 2025

For technical support: ops@stableyield.com  
For escalation: oncall@stableyield.com