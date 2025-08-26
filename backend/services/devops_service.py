"""
DevOps & Production Deployment Service (STEP 10)
Production infrastructure, monitoring, deployment automation, and DevOps capabilities
"""

import asyncio
import logging
import os
import json
import yaml
import subprocess
import psutil
import datetime
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import aiofiles
import tarfile
import shutil

logger = logging.getLogger(__name__)

@dataclass
class DeploymentConfig:
    environment: str  # "development", "staging", "production"
    version: str
    build_number: int
    deployment_time: datetime.datetime
    services: List[str]
    database_migration: bool
    rollback_enabled: bool
    health_check_timeout: int

@dataclass
class SystemMetrics:
    timestamp: datetime.datetime
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: Dict[str, int]
    process_count: int
    active_connections: int
    response_time_avg: float

@dataclass
class BackupJob:
    backup_id: str
    backup_type: str  # "database", "files", "configuration", "full"
    created_at: datetime.datetime
    size_bytes: int
    status: str  # "completed", "failed", "in_progress"
    retention_days: int
    encryption_enabled: bool

@dataclass
class AlertRule:
    rule_id: str
    metric: str
    threshold: float
    operator: str  # "gt", "lt", "eq"
    severity: str  # "info", "warning", "critical"
    notification_channels: List[str]
    is_active: bool

class DevOpsService:
    """Production DevOps and infrastructure management service"""
    
    def __init__(self):
        # Deployment configuration
        self.current_deployment: Optional[DeploymentConfig] = None
        self.deployment_history: List[DeploymentConfig] = []
        
        # Monitoring and metrics
        self.system_metrics: List[SystemMetrics] = []
        self.alert_rules: Dict[str, AlertRule] = {}
        self.active_alerts: List[Dict[str, Any]] = []
        
        # Backup management
        self.backup_jobs: List[BackupJob] = []
        self.backup_schedule = {
            "database": {"frequency": "daily", "time": "03:00", "retention": 30},
            "files": {"frequency": "weekly", "time": "04:00", "retention": 14},
            "configuration": {"frequency": "daily", "time": "02:00", "retention": 7}
        }
        
        # Infrastructure paths
        self.devops_dir = Path("/app/devops")
        self.devops_dir.mkdir(parents=True, exist_ok=True)
        
        self.docker_dir = self.devops_dir / "docker"
        self.k8s_dir = self.devops_dir / "kubernetes"
        self.monitoring_dir = self.devops_dir / "monitoring"
        self.backup_dir = Path("/app/data/backups")
        
        for dir_path in [self.docker_dir, self.k8s_dir, self.monitoring_dir, self.backup_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Configuration
        self.config = {
            "deployment": {
                "max_deployment_time": 600,  # 10 minutes
                "health_check_retries": 5,
                "rollback_timeout": 300,  # 5 minutes
                "pre_deployment_checks": True
            },
            "monitoring": {
                "metrics_retention_days": 30,
                "alert_cooldown_minutes": 15,
                "system_check_interval": 60,
                "performance_baseline_days": 7
            },
            "backup": {
                "compression_enabled": True,
                "encryption_key": "stableyield_backup_key_2025",
                "max_backup_size_gb": 10,
                "parallel_backups": 2
            },
            "security": {
                "ssl_enabled": True,
                "rate_limiting": True,
                "audit_logging": True,
                "vulnerability_scanning": True
            }
        }
        
        self.is_running = False
        self.background_tasks = []
    
    async def start(self):
        """Start the DevOps service"""
        if self.is_running:
            return
        
        self.is_running = True
        logger.info("🚀 Starting DevOps Service...")
        
        # Initialize infrastructure
        await self._initialize_infrastructure()
        
        # Load existing data
        await self._load_deployment_history()
        await self._load_alert_rules()
        
        # Start background tasks
        self.background_tasks = [
            asyncio.create_task(self._system_monitor()),
            asyncio.create_task(self._alert_processor()),
            asyncio.create_task(self._backup_scheduler()),
            asyncio.create_task(self._health_checker()),
            asyncio.create_task(self._metrics_aggregator())
        ]
        
        logger.info("✅ DevOps Service started")
    
    async def stop(self):
        """Stop the DevOps service"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()
        
        await asyncio.gather(*self.background_tasks, return_exceptions=True)
        
        # Save data
        await self._save_deployment_history()
        await self._save_alert_rules()
        
        logger.info("🛑 DevOps Service stopped")
    
    # Infrastructure Setup
    async def _initialize_infrastructure(self):
        """Initialize DevOps infrastructure files"""
        try:
            # Create Docker configurations
            await self._create_docker_configs()
            
            # Create Kubernetes manifests
            await self._create_k8s_manifests()
            
            # Create monitoring configurations
            await self._create_monitoring_configs()
            
            # Setup default alert rules
            await self._setup_default_alerts()
            
            logger.info("🏗️ DevOps infrastructure initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize infrastructure: {e}")
    
    async def _create_docker_configs(self):
        """Create Docker configuration files"""
        # Dockerfile for backend
        dockerfile_backend = """FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    build-essential \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ ./backend/
COPY data/ ./data/

# Create non-root user
RUN useradd -m -u 1000 stableyield && chown -R stableyield:stableyield /app
USER stableyield

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \\
  CMD curl -f http://localhost:8001/api/health || exit 1

EXPOSE 8001

CMD ["python", "backend/server.py"]
"""
        
        # Dockerfile for frontend
        dockerfile_frontend = """FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY frontend/package*.json ./
RUN npm ci --only=production

# Copy application code
COPY frontend/ .

# Build the application
RUN npm run build

# Use nginx to serve the built app
FROM nginx:alpine
COPY --from=0 /app/build /usr/share/nginx/html
COPY devops/nginx/nginx.conf /etc/nginx/nginx.conf

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]
"""
        
        # Docker Compose for development
        docker_compose = """version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: devops/docker/Dockerfile.backend
    ports:
      - "8001:8001"
    environment:
      - MONGO_URL=mongodb://mongodb:27017/stableyield
      - ENVIRONMENT=production
    depends_on:
      - mongodb
      - redis
    volumes:
      - ./data:/app/data
    restart: unless-stopped
    
  frontend:
    build:
      context: .
      dockerfile: devops/docker/Dockerfile.frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
    restart: unless-stopped
    
  mongodb:
    image: mongo:7.0
    ports:
      - "27017:27017"
    environment:
      - MONGO_INITDB_ROOT_USERNAME=stableyield
      - MONGO_INITDB_ROOT_PASSWORD=stableyield_prod_2025
    volumes:
      - mongodb_data:/data/db
      - ./devops/mongodb/init.js:/docker-entrypoint-initdb.d/init.js
    restart: unless-stopped
    
  redis:
    image: redis:7.2-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped
    
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./devops/nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./devops/ssl:/etc/nginx/ssl
    depends_on:
      - frontend
      - backend
    restart: unless-stopped
    
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./devops/monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
    restart: unless-stopped
    
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=stableyield_admin_2025
    volumes:
      - grafana_data:/var/lib/grafana
      - ./devops/monitoring/grafana:/etc/grafana/provisioning
    restart: unless-stopped

volumes:
  mongodb_data:
  redis_data:
  prometheus_data:
  grafana_data:
"""
        
        # Write Docker files
        async with aiofiles.open(self.docker_dir / "Dockerfile.backend", 'w') as f:
            await f.write(dockerfile_backend)
        
        async with aiofiles.open(self.docker_dir / "Dockerfile.frontend", 'w') as f:
            await f.write(dockerfile_frontend)
        
        async with aiofiles.open(self.devops_dir / "docker-compose.yml", 'w') as f:
            await f.write(docker_compose)
    
    async def _create_k8s_manifests(self):
        """Create Kubernetes deployment manifests"""
        # Backend deployment
        backend_deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "stableyield-backend",
                "labels": {"app": "stableyield-backend"}
            },
            "spec": {
                "replicas": 3,
                "selector": {"matchLabels": {"app": "stableyield-backend"}},
                "template": {
                    "metadata": {"labels": {"app": "stableyield-backend"}},
                    "spec": {
                        "containers": [{
                            "name": "backend",
                            "image": "stableyield/backend:latest",
                            "ports": [{"containerPort": 8001}],
                            "env": [
                                {"name": "MONGO_URL", "value": "mongodb://mongodb:27017/stableyield"},
                                {"name": "ENVIRONMENT", "value": "production"},
                                {"name": "REDIS_URL", "value": "redis://redis:6379"}
                            ],
                            "resources": {
                                "requests": {"memory": "512Mi", "cpu": "250m"},
                                "limits": {"memory": "1Gi", "cpu": "500m"}
                            },
                            "livenessProbe": {
                                "httpGet": {"path": "/api/health", "port": 8001},
                                "initialDelaySeconds": 30,
                                "periodSeconds": 10
                            },
                            "readinessProbe": {
                                "httpGet": {"path": "/api/health", "port": 8001},
                                "initialDelaySeconds": 5,
                                "periodSeconds": 5
                            }
                        }]
                    }
                }
            }
        }
        
        # Backend service
        backend_service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {"name": "stableyield-backend-service"},
            "spec": {
                "selector": {"app": "stableyield-backend"},
                "ports": [{"port": 8001, "targetPort": 8001}],
                "type": "ClusterIP"
            }
        }
        
        # Frontend deployment
        frontend_deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "stableyield-frontend",
                "labels": {"app": "stableyield-frontend"}
            },
            "spec": {
                "replicas": 2,
                "selector": {"matchLabels": {"app": "stableyield-frontend"}},
                "template": {
                    "metadata": {"labels": {"app": "stableyield-frontend"}},
                    "spec": {
                        "containers": [{
                            "name": "frontend",
                            "image": "stableyield/frontend:latest",
                            "ports": [{"containerPort": 3000}],
                            "resources": {
                                "requests": {"memory": "256Mi", "cpu": "100m"},
                                "limits": {"memory": "512Mi", "cpu": "200m"}
                            }
                        }]
                    }
                }
            }
        }
        
        # Ingress configuration
        ingress = {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "Ingress",
            "metadata": {
                "name": "stableyield-ingress",
                "annotations": {
                    "kubernetes.io/ingress.class": "nginx",
                    "cert-manager.io/cluster-issuer": "letsencrypt-prod",
                    "nginx.ingress.kubernetes.io/rate-limit": "100"
                }
            },
            "spec": {
                "tls": [{
                    "hosts": ["stableyield.com", "api.stableyield.com"],
                    "secretName": "stableyield-tls"
                }],
                "rules": [
                    {
                        "host": "stableyield.com",
                        "http": {
                            "paths": [{
                                "path": "/",
                                "pathType": "Prefix",
                                "backend": {
                                    "service": {
                                        "name": "stableyield-frontend-service",
                                        "port": {"number": 3000}
                                    }
                                }
                            }]
                        }
                    },
                    {
                        "host": "api.stableyield.com",
                        "http": {
                            "paths": [{
                                "path": "/",
                                "pathType": "Prefix",
                                "backend": {
                                    "service": {
                                        "name": "stableyield-backend-service",
                                        "port": {"number": 8001}
                                    }
                                }
                            }]
                        }
                    }
                ]
            }
        }
        
        # Write Kubernetes manifests
        manifests = {
            "backend-deployment.yaml": backend_deployment,
            "backend-service.yaml": backend_service,
            "frontend-deployment.yaml": frontend_deployment,
            "ingress.yaml": ingress
        }
        
        for filename, manifest in manifests.items():
            async with aiofiles.open(self.k8s_dir / filename, 'w') as f:
                await f.write(yaml.dump(manifest, default_flow_style=False))
    
    async def _create_monitoring_configs(self):
        """Create monitoring configuration files"""
        # Prometheus configuration
        prometheus_config = """
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  - job_name: 'stableyield-backend'
    static_configs:
      - targets: ['backend:8001']
    metrics_path: '/api/metrics'
    
  - job_name: 'stableyield-system'
    static_configs:
      - targets: ['node-exporter:9100']
    
  - job_name: 'mongodb'
    static_configs:
      - targets: ['mongodb-exporter:9216']
    
  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']
"""
        
        # Alert rules
        alert_rules = """
groups:
  - name: stableyield.rules
    rules:
      - alert: HighCPUUsage
        expr: cpu_usage_percent > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage detected"
          description: "CPU usage is above 80% for more than 5 minutes"
          
      - alert: HighMemoryUsage
        expr: memory_usage_percent > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High Memory usage detected"
          description: "Memory usage is above 85% for more than 5 minutes"
          
      - alert: ServiceDown
        expr: up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Service is down"
          description: "{{ $labels.instance }} of job {{ $labels.job }} has been down for more than 1 minute"
          
      - alert: HighResponseTime
        expr: http_request_duration_seconds{quantile="0.95"} > 1
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High response time"
          description: "95th percentile response time is above 1 second"
"""
        
        # Grafana dashboard
        grafana_dashboard = {
            "dashboard": {
                "id": None,
                "title": "StableYield Production Dashboard",
                "tags": ["stableyield", "production"],
                "timezone": "UTC",
                "panels": [
                    {
                        "id": 1,
                        "title": "Request Rate",
                        "type": "graph",
                        "targets": [{
                            "expr": "rate(http_requests_total[5m])",
                            "legendFormat": "{{method}} {{status}}"
                        }]
                    },
                    {
                        "id": 2,
                        "title": "Response Time",
                        "type": "graph",
                        "targets": [{
                            "expr": "histogram_quantile(0.95, http_request_duration_seconds_bucket)",
                            "legendFormat": "95th percentile"
                        }]
                    },
                    {
                        "id": 3,
                        "title": "System Resources",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "cpu_usage_percent",
                                "legendFormat": "CPU %"
                            },
                            {
                                "expr": "memory_usage_percent",
                                "legendFormat": "Memory %"
                            }
                        ]
                    }
                ],
                "time": {"from": "now-1h", "to": "now"},
                "refresh": "10s"
            }
        }
        
        # Write monitoring configs
        async with aiofiles.open(self.monitoring_dir / "prometheus.yml", 'w') as f:
            await f.write(prometheus_config)
        
        async with aiofiles.open(self.monitoring_dir / "alert_rules.yml", 'w') as f:
            await f.write(alert_rules)
        
        async with aiofiles.open(self.monitoring_dir / "dashboard.json", 'w') as f:
            await f.write(json.dumps(grafana_dashboard, indent=2))
    
    # Deployment Management
    async def deploy(self, version: str, environment: str = "production", services: List[str] = None) -> DeploymentConfig:
        """Deploy application to specified environment"""
        if services is None:
            services = ["backend", "frontend", "mongodb", "redis"]
        
        deployment = DeploymentConfig(
            environment=environment,
            version=version,
            build_number=len(self.deployment_history) + 1,
            deployment_time=datetime.datetime.utcnow(),
            services=services,
            database_migration=True,
            rollback_enabled=True,
            health_check_timeout=300
        )
        
        try:
            logger.info(f"🚀 Starting deployment {deployment.build_number} to {environment}")
            
            # Pre-deployment checks
            if self.config["deployment"]["pre_deployment_checks"]:
                await self._run_pre_deployment_checks()
            
            # Create deployment backup
            await self._create_deployment_backup(deployment)
            
            # Deploy services
            for service in services:
                await self._deploy_service(service, version, environment)
            
            # Post-deployment health checks
            await self._run_post_deployment_checks(deployment)
            
            # Update current deployment
            self.current_deployment = deployment
            self.deployment_history.append(deployment)
            
            logger.info(f"✅ Deployment {deployment.build_number} completed successfully")
            return deployment
            
        except Exception as e:
            logger.error(f"❌ Deployment {deployment.build_number} failed: {e}")
            
            if deployment.rollback_enabled:
                await self._rollback_deployment(deployment)
            
            raise
    
    async def _run_pre_deployment_checks(self):
        """Run pre-deployment health and readiness checks"""
        logger.info("🔍 Running pre-deployment checks...")
        
        # Check system resources
        cpu_usage = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        if cpu_usage > 90:
            raise Exception(f"CPU usage too high: {cpu_usage}%")
        
        if memory.percent > 90:
            raise Exception(f"Memory usage too high: {memory.percent}%")
        
        if disk.percent > 90:
            raise Exception(f"Disk usage too high: {disk.percent}%")
        
        # Check database connectivity
        # This would be implemented with actual database checks
        
        logger.info("✅ Pre-deployment checks passed")
    
    async def _deploy_service(self, service: str, version: str, environment: str):
        """Deploy a specific service"""
        logger.info(f"📦 Deploying {service} version {version} to {environment}")
        
        # This would implement actual deployment logic
        # For example, using kubectl, docker compose, or CI/CD tools
        
        await asyncio.sleep(2)  # Simulate deployment time
        logger.info(f"✅ {service} deployed successfully")
    
    async def _run_post_deployment_checks(self, deployment: DeploymentConfig):
        """Run post-deployment health checks"""
        logger.info("🏥 Running post-deployment health checks...")
        
        # Check service health endpoints
        # This would implement actual health check logic
        
        await asyncio.sleep(3)  # Simulate health check time
        logger.info("✅ Post-deployment checks passed")
    
    async def _rollback_deployment(self, failed_deployment: DeploymentConfig):
        """Rollback failed deployment"""
        logger.warning(f"🔄 Rolling back deployment {failed_deployment.build_number}")
        
        # This would implement actual rollback logic
        
        await asyncio.sleep(5)  # Simulate rollback time
        logger.info("✅ Rollback completed")
    
    # Monitoring and Metrics
    async def _system_monitor(self):
        """Background task for system monitoring"""
        while self.is_running:
            try:
                # Collect system metrics
                cpu_usage = psutil.cpu_percent()
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                network = psutil.net_io_counters()
                
                metrics = SystemMetrics(
                    timestamp=datetime.datetime.utcnow(),
                    cpu_usage=cpu_usage,
                    memory_usage=memory.percent,
                    disk_usage=disk.percent,
                    network_io={
                        "bytes_sent": network.bytes_sent,
                        "bytes_recv": network.bytes_recv
                    },
                    process_count=len(psutil.pids()),
                    active_connections=len(psutil.net_connections()),
                    response_time_avg=0.1  # Would be calculated from actual metrics
                )
                
                self.system_metrics.append(metrics)
                
                # Keep only recent metrics
                if len(self.system_metrics) > 10000:
                    self.system_metrics = self.system_metrics[-5000:]
                
                # Check alert conditions
                await self._check_alert_conditions(metrics)
                
                await asyncio.sleep(self.config["monitoring"]["system_check_interval"])
                
            except Exception as e:
                logger.error(f"❌ System monitor error: {e}")
                await asyncio.sleep(60)
    
    async def _check_alert_conditions(self, metrics: SystemMetrics):
        """Check metrics against alert rules"""
        for rule_id, rule in self.alert_rules.items():
            if not rule.is_active:
                continue
            
            # Get metric value
            if rule.metric == "cpu_usage":
                value = metrics.cpu_usage
            elif rule.metric == "memory_usage":
                value = metrics.memory_usage
            elif rule.metric == "disk_usage":
                value = metrics.disk_usage
            elif rule.metric == "response_time":
                value = metrics.response_time_avg
            else:
                continue
            
            # Check threshold
            triggered = False
            if rule.operator == "gt" and value > rule.threshold:
                triggered = True
            elif rule.operator == "lt" and value < rule.threshold:
                triggered = True
            elif rule.operator == "eq" and value == rule.threshold:
                triggered = True
            
            if triggered:
                await self._trigger_alert(rule, value, metrics.timestamp)
    
    async def _trigger_alert(self, rule: AlertRule, value: float, timestamp: datetime.datetime):
        """Trigger an alert"""
        # Check cooldown
        recent_alerts = [
            alert for alert in self.active_alerts
            if alert["rule_id"] == rule.rule_id and
            (timestamp - datetime.datetime.fromisoformat(alert["timestamp"])).total_seconds() < 
            self.config["monitoring"]["alert_cooldown_minutes"] * 60
        ]
        
        if recent_alerts:
            return  # Still in cooldown
        
        alert = {
            "alert_id": f"alert_{len(self.active_alerts) + 1}",
            "rule_id": rule.rule_id,
            "metric": rule.metric,
            "value": value,
            "threshold": rule.threshold,
            "severity": rule.severity,
            "timestamp": timestamp.isoformat(),
            "status": "active"
        }
        
        self.active_alerts.append(alert)
        
        logger.warning(f"🚨 Alert triggered: {rule.metric} = {value} (threshold: {rule.threshold})")
        
        # Send notifications (would implement actual notification logic)
        for channel in rule.notification_channels:
            await self._send_notification(channel, alert)
    
    async def _send_notification(self, channel: str, alert: Dict[str, Any]):
        """Send alert notification"""
        # This would implement actual notification sending
        logger.info(f"📧 Notification sent to {channel}: {alert['metric']} alert")
    
    # Backup Management
    async def _backup_scheduler(self):
        """Background task for scheduled backups"""
        while self.is_running:
            try:
                current_time = datetime.datetime.utcnow()
                
                # Check each backup type
                for backup_type, schedule in self.backup_schedule.items():
                    if self._should_run_backup(backup_type, current_time, schedule):
                        await self._run_backup(backup_type)
                
                await asyncio.sleep(3600)  # Check every hour
                
            except Exception as e:
                logger.error(f"❌ Backup scheduler error: {e}")
                await asyncio.sleep(3600)
    
    def _should_run_backup(self, backup_type: str, current_time: datetime.datetime, schedule: Dict[str, str]) -> bool:
        """Check if backup should run based on schedule"""
        # Simplified scheduling logic
        if schedule["frequency"] == "daily":
            return current_time.hour == int(schedule["time"].split(":")[0])
        elif schedule["frequency"] == "weekly":
            return current_time.weekday() == 0 and current_time.hour == int(schedule["time"].split(":")[0])
        
        return False
    
    async def _run_backup(self, backup_type: str):
        """Run a backup job"""
        backup_id = f"backup_{backup_type}_{datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            logger.info(f"💾 Starting {backup_type} backup: {backup_id}")
            
            backup_path = self.backup_dir / f"{backup_id}.tar.gz"
            
            # Create backup based on type
            if backup_type == "database":
                await self._backup_database(backup_path)
            elif backup_type == "files":
                await self._backup_files(backup_path)
            elif backup_type == "configuration":
                await self._backup_configuration(backup_path)
            
            # Get backup size
            size_bytes = backup_path.stat().st_size if backup_path.exists() else 0
            
            # Create backup job record
            backup_job = BackupJob(
                backup_id=backup_id,
                backup_type=backup_type,
                created_at=datetime.datetime.utcnow(),
                size_bytes=size_bytes,
                status="completed",
                retention_days=self.backup_schedule[backup_type]["retention"],
                encryption_enabled=self.config["backup"]["compression_enabled"]
            )
            
            self.backup_jobs.append(backup_job)
            
            # Cleanup old backups
            await self._cleanup_old_backups(backup_type)
            
            logger.info(f"✅ {backup_type} backup completed: {backup_id} ({size_bytes} bytes)")
            
        except Exception as e:
            logger.error(f"❌ {backup_type} backup failed: {e}")
            
            backup_job = BackupJob(
                backup_id=backup_id,
                backup_type=backup_type,
                created_at=datetime.datetime.utcnow(),
                size_bytes=0,
                status="failed",
                retention_days=self.backup_schedule[backup_type]["retention"],
                encryption_enabled=False
            )
            
            self.backup_jobs.append(backup_job)
    
    async def _backup_database(self, backup_path: Path):
        """Backup database"""
        # This would implement actual database backup logic
        await asyncio.sleep(5)  # Simulate backup time
        
        # Create dummy backup file
        with open(backup_path, 'w') as f:
            f.write(f"Database backup created at {datetime.datetime.utcnow()}")
    
    async def _backup_files(self, backup_path: Path):
        """Backup application files"""
        # Create tar archive of important files
        with tarfile.open(backup_path, 'w:gz') as tar:
            tar.add('/app/data', arcname='data')
            tar.add('/app/backend', arcname='backend')
    
    async def _backup_configuration(self, backup_path: Path):
        """Backup configuration files"""
        with tarfile.open(backup_path, 'w:gz') as tar:
            tar.add('/app/devops', arcname='devops')
            tar.add('/app/backend/.env', arcname='backend.env')
            tar.add('/app/frontend/.env', arcname='frontend.env')
    
    async def _cleanup_old_backups(self, backup_type: str):
        """Cleanup old backup files"""
        retention_days = self.backup_schedule[backup_type]["retention"]
        cutoff_date = datetime.datetime.utcnow() - datetime.timedelta(days=retention_days)
        
        for backup_job in self.backup_jobs[:]:
            if (backup_job.backup_type == backup_type and 
                backup_job.created_at < cutoff_date):
                
                # Remove backup file
                backup_path = self.backup_dir / f"{backup_job.backup_id}.tar.gz"
                if backup_path.exists():
                    backup_path.unlink()
                
                # Remove from records
                self.backup_jobs.remove(backup_job)
                
                logger.info(f"🗑️ Cleaned up old backup: {backup_job.backup_id}")
    
    # Background Tasks
    async def _alert_processor(self):
        """Process and manage alerts"""
        while self.is_running:
            try:
                # Clean up resolved alerts
                current_time = datetime.datetime.utcnow()
                self.active_alerts = [
                    alert for alert in self.active_alerts
                    if (current_time - datetime.datetime.fromisoformat(alert["timestamp"])).total_seconds() < 3600  # 1 hour
                ]
                
                await asyncio.sleep(300)  # Every 5 minutes
                
            except Exception as e:
                logger.error(f"❌ Alert processor error: {e}")
                await asyncio.sleep(300)
    
    async def _health_checker(self):
        """Continuous health monitoring"""
        while self.is_running:
            try:
                # Check service health
                health_status = await self._check_service_health()
                
                # Log health status changes
                # This would implement health status tracking
                
                await asyncio.sleep(30)  # Every 30 seconds
                
            except Exception as e:
                logger.error(f"❌ Health checker error: {e}")
                await asyncio.sleep(30)
    
    async def _check_service_health(self) -> Dict[str, str]:
        """Check health of all services"""
        health_status = {
            "backend": "healthy",
            "frontend": "healthy",
            "database": "healthy",
            "redis": "healthy",
            "monitoring": "healthy"
        }
        
        # This would implement actual health checks
        return health_status
    
    async def _metrics_aggregator(self):
        """Aggregate and store metrics"""
        while self.is_running:
            try:
                # Aggregate recent metrics
                if len(self.system_metrics) > 100:
                    recent_metrics = self.system_metrics[-100:]
                    
                    # Calculate aggregations
                    avg_cpu = sum(m.cpu_usage for m in recent_metrics) / len(recent_metrics)
                    avg_memory = sum(m.memory_usage for m in recent_metrics) / len(recent_metrics)
                    avg_response_time = sum(m.response_time_avg for m in recent_metrics) / len(recent_metrics)
                    
                    # Store aggregated metrics
                    aggregated = {
                        "timestamp": datetime.datetime.utcnow().isoformat(),
                        "avg_cpu_usage": avg_cpu,
                        "avg_memory_usage": avg_memory,
                        "avg_response_time": avg_response_time,
                        "data_points": len(recent_metrics)
                    }
                    
                    # Save to file (would be database in production)
                    metrics_file = self.devops_dir / f"metrics_{datetime.datetime.utcnow().strftime('%Y%m%d_%H')}.json"
                    async with aiofiles.open(metrics_file, 'w') as f:
                        await f.write(json.dumps(aggregated, indent=2))
                
                await asyncio.sleep(3600)  # Every hour
                
            except Exception as e:
                logger.error(f"❌ Metrics aggregator error: {e}")
                await asyncio.sleep(3600)
    
    async def _setup_default_alerts(self):
        """Setup default alert rules"""
        default_rules = [
            AlertRule(
                rule_id="high_cpu",
                metric="cpu_usage",
                threshold=80.0,
                operator="gt",
                severity="warning",
                notification_channels=["email", "slack"],
                is_active=True
            ),
            AlertRule(
                rule_id="high_memory",
                metric="memory_usage",
                threshold=85.0,
                operator="gt",
                severity="warning",
                notification_channels=["email", "slack"],
                is_active=True
            ),
            AlertRule(
                rule_id="high_response_time",
                metric="response_time",
                threshold=1.0,
                operator="gt",
                severity="warning",
                notification_channels=["email"],
                is_active=True
            )
        ]
        
        for rule in default_rules:
            self.alert_rules[rule.rule_id] = rule
    
    # Data Persistence
    async def _load_deployment_history(self):
        """Load deployment history from storage"""
        try:
            history_file = self.devops_dir / "deployment_history.json"
            if history_file.exists():
                async with aiofiles.open(history_file, 'r') as f:
                    data = json.loads(await f.read())
                
                for deployment_data in data:
                    deployment = DeploymentConfig(**deployment_data)
                    deployment.deployment_time = datetime.datetime.fromisoformat(deployment_data["deployment_time"])
                    self.deployment_history.append(deployment)
                
                logger.info(f"📂 Loaded {len(self.deployment_history)} deployment records")
        except Exception as e:
            logger.error(f"❌ Error loading deployment history: {e}")
    
    async def _save_deployment_history(self):
        """Save deployment history to storage"""
        try:
            history_file = self.devops_dir / "deployment_history.json"
            data = []
            
            for deployment in self.deployment_history:
                deployment_data = asdict(deployment)
                deployment_data["deployment_time"] = deployment.deployment_time.isoformat()
                data.append(deployment_data)
            
            async with aiofiles.open(history_file, 'w') as f:
                await f.write(json.dumps(data, indent=2))
        except Exception as e:
            logger.error(f"❌ Error saving deployment history: {e}")
    
    async def _load_alert_rules(self):
        """Load alert rules from storage"""
        try:
            rules_file = self.devops_dir / "alert_rules.json"
            if rules_file.exists():
                async with aiofiles.open(rules_file, 'r') as f:
                    data = json.loads(await f.read())
                
                for rule_data in data:
                    rule = AlertRule(**rule_data)
                    self.alert_rules[rule.rule_id] = rule
                
                logger.info(f"📂 Loaded {len(self.alert_rules)} alert rules")
        except Exception as e:
            logger.error(f"❌ Error loading alert rules: {e}")
    
    async def _save_alert_rules(self):
        """Save alert rules to storage"""
        try:
            rules_file = self.devops_dir / "alert_rules.json"
            data = [asdict(rule) for rule in self.alert_rules.values()]
            
            async with aiofiles.open(rules_file, 'w') as f:
                await f.write(json.dumps(data, indent=2))
        except Exception as e:
            logger.error(f"❌ Error saving alert rules: {e}")
    
    async def _create_deployment_backup(self, deployment: DeploymentConfig):
        """Create backup before deployment"""
        backup_id = f"pre_deploy_{deployment.build_number}_{datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            logger.info(f"💾 Creating pre-deployment backup: {backup_id}")
            
            backup_path = self.backup_dir / f"{backup_id}.tar.gz"
            
            # Create full backup
            with tarfile.open(backup_path, 'w:gz') as tar:
                tar.add('/app/data', arcname='data')
                tar.add('/app/backend', arcname='backend')
                tar.add('/app/devops', arcname='devops')
            
            size_bytes = backup_path.stat().st_size
            
            backup_job = BackupJob(
                backup_id=backup_id,
                backup_type="pre_deployment",
                created_at=datetime.datetime.utcnow(),
                size_bytes=size_bytes,
                status="completed",
                retention_days=7,
                encryption_enabled=True
            )
            
            self.backup_jobs.append(backup_job)
            
            logger.info(f"✅ Pre-deployment backup completed: {backup_id}")
            
        except Exception as e:
            logger.error(f"❌ Pre-deployment backup failed: {e}")
            raise
    
    # Status and Management
    def get_devops_status(self) -> Dict[str, Any]:
        """Get DevOps service status"""
        return {
            "service_running": self.is_running,
            "current_deployment": asdict(self.current_deployment) if self.current_deployment else None,
            "deployment_history_count": len(self.deployment_history),
            "system_metrics": {
                "total_collected": len(self.system_metrics),
                "latest_cpu": self.system_metrics[-1].cpu_usage if self.system_metrics else 0,
                "latest_memory": self.system_metrics[-1].memory_usage if self.system_metrics else 0,
                "latest_disk": self.system_metrics[-1].disk_usage if self.system_metrics else 0
            },
            "alerts": {
                "total_rules": len(self.alert_rules),
                "active_alerts": len(self.active_alerts),
                "active_rules": len([r for r in self.alert_rules.values() if r.is_active])
            },
            "backups": {
                "total_backups": len(self.backup_jobs),
                "successful_backups": len([b for b in self.backup_jobs if b.status == "completed"]),
                "failed_backups": len([b for b in self.backup_jobs if b.status == "failed"]),
                "total_backup_size": sum(b.size_bytes for b in self.backup_jobs)
            },
            "infrastructure": {
                "docker_configs": len(list(self.docker_dir.glob("*"))),
                "k8s_manifests": len(list(self.k8s_dir.glob("*.yaml"))),
                "monitoring_configs": len(list(self.monitoring_dir.glob("*")))
            },
            "last_updated": datetime.datetime.utcnow().isoformat()
        }

# Global DevOps service instance
devops_service = None

async def start_devops():
    """Start the global DevOps service"""
    global devops_service
    
    if devops_service is None:
        devops_service = DevOpsService()
        await devops_service.start()
        logger.info("🚀 DevOps service started")
    else:
        logger.info("⚠️ DevOps service already running")

async def stop_devops():
    """Stop the global DevOps service"""
    global devops_service
    
    if devops_service:
        await devops_service.stop()
        devops_service = None
        logger.info("🛑 DevOps service stopped")

def get_devops_service() -> Optional[DevOpsService]:
    """Get the global DevOps service"""
    return devops_service