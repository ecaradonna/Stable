"""
DevOps & Production Deployment Routes (STEP 10)
API endpoints for DevOps operations, deployment management, monitoring, and production infrastructure
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
from pydantic import BaseModel

from services.devops_service import get_devops_service

logger = logging.getLogger(__name__)
router = APIRouter()

# Pydantic models for request/response
class DeploymentRequest(BaseModel):
    version: str
    environment: str = "production"
    services: Optional[List[str]] = None

class AlertRuleRequest(BaseModel):
    rule_id: str
    metric: str
    threshold: float
    operator: str = "gt"  # gt, lt, eq
    severity: str = "warning"  # info, warning, critical
    notification_channels: List[str] = ["email"]

@router.get("/devops/status")
async def get_devops_status() -> Dict[str, Any]:
    """Get DevOps service status and infrastructure overview"""
    try:
        devops_service = get_devops_service()
        
        if not devops_service:
            return {
                "service_running": False,
                "message": "DevOps service not started",
                "current_deployment": None,
                "system_metrics": {},
                "alerts": {"total_rules": 0, "active_alerts": 0},
                "backups": {"total_backups": 0}
            }
        
        return devops_service.get_devops_status()
        
    except Exception as e:
        logger.error(f"Error getting DevOps status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get DevOps status")

@router.post("/devops/start")
async def start_devops_services() -> Dict[str, Any]:
    """Start DevOps and production infrastructure services"""
    try:
        from services.devops_service import start_devops
        
        await start_devops()
        
        return {
            "message": "DevOps and production infrastructure services started successfully",
            "capabilities": [
                "Container Orchestration (Docker, Kubernetes)",
                "CI/CD Pipeline Management",
                "Production Monitoring (Prometheus, Grafana)",
                "Automated Backup & Recovery",
                "Security Hardening & Compliance",
                "Performance Optimization & Auto-scaling",
                "Alert Management & Notification System"
            ],
            "infrastructure_components": [
                "Docker containers and compose files",
                "Kubernetes deployment manifests",
                "Prometheus monitoring configuration", 
                "Grafana dashboards and alerts",
                "Automated backup scheduling",
                "System health monitoring",
                "Performance metrics collection"
            ],
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error starting DevOps services: {e}")
        raise HTTPException(status_code=500, detail="Failed to start DevOps services")

@router.post("/devops/stop")
async def stop_devops_services() -> Dict[str, Any]:
    """Stop DevOps services"""
    try:
        from services.devops_service import stop_devops
        
        await stop_devops()
        
        return {
            "message": "DevOps services stopped successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error stopping DevOps services: {e}")
        raise HTTPException(status_code=500, detail="Failed to stop DevOps services")

# Deployment Management
@router.post("/devops/deploy")
async def deploy_application(request: DeploymentRequest) -> Dict[str, Any]:
    """Deploy application to specified environment"""
    try:
        devops_service = get_devops_service()
        
        if not devops_service:
            raise HTTPException(status_code=503, detail="DevOps service not running")
        
        # Validate environment
        valid_environments = ["development", "staging", "production"]
        if request.environment not in valid_environments:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid environment. Must be one of: {valid_environments}"
            )
        
        # Deploy application
        deployment = await devops_service.deploy(
            request.version, request.environment, request.services
        )
        
        return {
            "deployment": {
                "build_number": deployment.build_number,
                "version": deployment.version,
                "environment": deployment.environment,
                "services": deployment.services,
                "deployment_time": deployment.deployment_time.isoformat(),
                "rollback_enabled": deployment.rollback_enabled,
                "health_check_timeout": deployment.health_check_timeout
            },
            "status": "completed",
            "message": f"Successfully deployed version {deployment.version} to {deployment.environment}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deploying application: {e}")
        raise HTTPException(status_code=500, detail=f"Deployment failed: {str(e)}")

@router.get("/devops/deployments")
async def get_deployment_history() -> Dict[str, Any]:
    """Get deployment history"""
    try:
        devops_service = get_devops_service()
        
        if not devops_service:
            raise HTTPException(status_code=503, detail="DevOps service not running")
        
        deployments = []
        for deployment in devops_service.deployment_history:
            deployments.append({
                "build_number": deployment.build_number,
                "version": deployment.version,
                "environment": deployment.environment,
                "services": deployment.services,
                "deployment_time": deployment.deployment_time.isoformat(),
                "database_migration": deployment.database_migration,
                "rollback_enabled": deployment.rollback_enabled
            })
        
        # Sort by deployment time (newest first)
        deployments.sort(key=lambda x: x["deployment_time"], reverse=True)
        
        return {
            "deployments": deployments,
            "total_deployments": len(deployments),
            "current_deployment": {
                "build_number": devops_service.current_deployment.build_number,
                "version": devops_service.current_deployment.version,
                "environment": devops_service.current_deployment.environment
            } if devops_service.current_deployment else None,
            "environments": {
                env: len([d for d in deployments if d["environment"] == env])
                for env in ["development", "staging", "production"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting deployment history: {e}")
        raise HTTPException(status_code=500, detail="Failed to get deployment history")

# Monitoring and Metrics
@router.get("/devops/metrics")
async def get_system_metrics(
    hours: int = Query(default=1, description="Hours of metrics to retrieve")
) -> Dict[str, Any]:
    """Get system performance metrics"""
    try:
        devops_service = get_devops_service()
        
        if not devops_service:
            raise HTTPException(status_code=503, detail="DevOps service not running")
        
        # Get recent metrics
        cutoff_time = datetime.utcnow() - datetime.timedelta(hours=hours)
        recent_metrics = [
            m for m in devops_service.system_metrics
            if m.timestamp >= cutoff_time
        ]
        
        if not recent_metrics:
            return {
                "message": f"No metrics available for the last {hours} hour(s)",
                "metrics": [],
                "summary": {}
            }
        
        # Format metrics for response
        formatted_metrics = []
        for metric in recent_metrics:
            formatted_metrics.append({
                "timestamp": metric.timestamp.isoformat(),
                "cpu_usage": metric.cpu_usage,
                "memory_usage": metric.memory_usage,
                "disk_usage": metric.disk_usage,
                "network_io": metric.network_io,
                "process_count": metric.process_count,
                "active_connections": metric.active_connections,
                "response_time_avg": metric.response_time_avg
            })
        
        # Calculate summary statistics
        avg_cpu = sum(m.cpu_usage for m in recent_metrics) / len(recent_metrics)
        avg_memory = sum(m.memory_usage for m in recent_metrics) / len(recent_metrics)
        avg_disk = sum(m.disk_usage for m in recent_metrics) / len(recent_metrics)
        avg_response_time = sum(m.response_time_avg for m in recent_metrics) / len(recent_metrics)
        
        max_cpu = max(m.cpu_usage for m in recent_metrics)
        max_memory = max(m.memory_usage for m in recent_metrics)
        max_disk = max(m.disk_usage for m in recent_metrics)
        
        return {
            "metrics": formatted_metrics,
            "total_data_points": len(recent_metrics),
            "time_range": f"{hours} hour(s)",
            "summary": {
                "average_metrics": {
                    "cpu_usage": avg_cpu,
                    "memory_usage": avg_memory,
                    "disk_usage": avg_disk,
                    "response_time": avg_response_time
                },
                "peak_metrics": {
                    "max_cpu_usage": max_cpu,
                    "max_memory_usage": max_memory,
                    "max_disk_usage": max_disk
                },
                "health_assessment": {
                    "cpu_status": "healthy" if avg_cpu < 70 else "warning" if avg_cpu < 85 else "critical",
                    "memory_status": "healthy" if avg_memory < 75 else "warning" if avg_memory < 90 else "critical",
                    "disk_status": "healthy" if avg_disk < 80 else "warning" if avg_disk < 95 else "critical"
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting system metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get system metrics")

@router.get("/devops/alerts")
async def get_alerts() -> Dict[str, Any]:
    """Get alert rules and active alerts"""
    try:
        devops_service = get_devops_service()
        
        if not devops_service:
            raise HTTPException(status_code=503, detail="DevOps service not running")
        
        # Get alert rules
        alert_rules = []
        for rule in devops_service.alert_rules.values():
            alert_rules.append({
                "rule_id": rule.rule_id,
                "metric": rule.metric,
                "threshold": rule.threshold,
                "operator": rule.operator,
                "severity": rule.severity,
                "notification_channels": rule.notification_channels,
                "is_active": rule.is_active
            })
        
        # Get active alerts
        active_alerts = devops_service.active_alerts.copy()
        
        # Group alerts by severity
        alerts_by_severity = {"info": 0, "warning": 0, "critical": 0}
        for alert in active_alerts:
            severity = alert.get("severity", "info")
            alerts_by_severity[severity] += 1
        
        return {
            "alert_rules": alert_rules,
            "active_alerts": active_alerts,
            "total_rules": len(alert_rules),
            "active_rules": len([r for r in alert_rules if r["is_active"]]),
            "total_active_alerts": len(active_alerts),
            "alerts_by_severity": alerts_by_severity,
            "alert_summary": {
                "critical_alerts": alerts_by_severity["critical"],
                "warning_alerts": alerts_by_severity["warning"],
                "info_alerts": alerts_by_severity["info"],
                "most_recent_alert": active_alerts[0] if active_alerts else None
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
        raise HTTPException(status_code=500, detail="Failed to get alerts")

@router.post("/devops/alerts/rules")
async def create_alert_rule(request: AlertRuleRequest) -> Dict[str, Any]:
    """Create a new alert rule"""
    try:
        devops_service = get_devops_service()
        
        if not devops_service:
            raise HTTPException(status_code=503, detail="DevOps service not running")
        
        # Validate metric
        valid_metrics = ["cpu_usage", "memory_usage", "disk_usage", "response_time"]
        if request.metric not in valid_metrics:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid metric. Must be one of: {valid_metrics}"
            )
        
        # Validate operator
        valid_operators = ["gt", "lt", "eq"]
        if request.operator not in valid_operators:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid operator. Must be one of: {valid_operators}"
            )
        
        # Validate severity
        valid_severities = ["info", "warning", "critical"]
        if request.severity not in valid_severities:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid severity. Must be one of: {valid_severities}"
            )
        
        # Check if rule already exists
        if request.rule_id in devops_service.alert_rules:
            raise HTTPException(status_code=409, detail="Alert rule already exists")
        
        # Create alert rule
        from services.devops_service import AlertRule
        
        alert_rule = AlertRule(
            rule_id=request.rule_id,
            metric=request.metric,
            threshold=request.threshold,
            operator=request.operator,
            severity=request.severity,
            notification_channels=request.notification_channels,
            is_active=True
        )
        
        devops_service.alert_rules[request.rule_id] = alert_rule
        await devops_service._save_alert_rules()
        
        return {
            "message": f"Alert rule '{request.rule_id}' created successfully",
            "alert_rule": {
                "rule_id": alert_rule.rule_id,
                "metric": alert_rule.metric,
                "threshold": alert_rule.threshold,
                "operator": alert_rule.operator,
                "severity": alert_rule.severity,
                "notification_channels": alert_rule.notification_channels,
                "is_active": alert_rule.is_active
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating alert rule: {e}")
        raise HTTPException(status_code=500, detail="Failed to create alert rule")

# Backup Management
@router.get("/devops/backups")
async def get_backups() -> Dict[str, Any]:
    """Get backup jobs and status"""
    try:
        devops_service = get_devops_service()
        
        if not devops_service:
            raise HTTPException(status_code=503, detail="DevOps service not running")
        
        # Get backup jobs
        backup_jobs = []
        for backup in devops_service.backup_jobs:
            backup_jobs.append({
                "backup_id": backup.backup_id,
                "backup_type": backup.backup_type,
                "created_at": backup.created_at.isoformat(),
                "size_bytes": backup.size_bytes,
                "size_mb": round(backup.size_bytes / (1024 * 1024), 2),
                "status": backup.status,
                "retention_days": backup.retention_days,
                "encryption_enabled": backup.encryption_enabled
            })
        
        # Sort by creation time (newest first)
        backup_jobs.sort(key=lambda x: x["created_at"], reverse=True)
        
        # Group by backup type
        backups_by_type = {}
        for backup in backup_jobs:
            backup_type = backup["backup_type"]
            if backup_type not in backups_by_type:
                backups_by_type[backup_type] = 0
            backups_by_type[backup_type] += 1
        
        # Calculate total size
        total_size_bytes = sum(b["size_bytes"] for b in backup_jobs)
        total_size_gb = round(total_size_bytes / (1024 * 1024 * 1024), 2)
        
        return {
            "backups": backup_jobs,
            "total_backups": len(backup_jobs),
            "successful_backups": len([b for b in backup_jobs if b["status"] == "completed"]),
            "failed_backups": len([b for b in backup_jobs if b["status"] == "failed"]),
            "backups_by_type": backups_by_type,
            "total_storage": {
                "size_bytes": total_size_bytes,
                "size_gb": total_size_gb
            },
            "backup_schedule": devops_service.backup_schedule,
            "latest_backup": backup_jobs[0] if backup_jobs else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting backups: {e}")
        raise HTTPException(status_code=500, detail="Failed to get backups")

@router.post("/devops/backups/{backup_type}")
async def create_backup(backup_type: str) -> Dict[str, Any]:
    """Manually trigger a backup job"""
    try:
        devops_service = get_devops_service()
        
        if not devops_service:
            raise HTTPException(status_code=503, detail="DevOps service not running")
        
        # Validate backup type
        valid_types = ["database", "files", "configuration", "full"]
        if backup_type not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid backup type. Must be one of: {valid_types}"
            )
        
        # Trigger backup
        await devops_service._run_backup(backup_type)
        
        # Get the latest backup job
        latest_backup = None
        for backup in reversed(devops_service.backup_jobs):
            if backup.backup_type == backup_type:
                latest_backup = backup
                break
        
        return {
            "message": f"{backup_type} backup completed successfully",
            "backup": {
                "backup_id": latest_backup.backup_id,
                "backup_type": latest_backup.backup_type,
                "created_at": latest_backup.created_at.isoformat(),
                "size_bytes": latest_backup.size_bytes,
                "size_mb": round(latest_backup.size_bytes / (1024 * 1024), 2),
                "status": latest_backup.status,
                "encryption_enabled": latest_backup.encryption_enabled
            } if latest_backup else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating backup: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create {backup_type} backup")

# Infrastructure Management
@router.get("/devops/infrastructure")
async def get_infrastructure_status() -> Dict[str, Any]:
    """Get infrastructure configuration and status"""
    try:
        devops_service = get_devops_service()
        
        if not devops_service:
            raise HTTPException(status_code=503, detail="DevOps service not running")
        
        # Check infrastructure files
        docker_files = list(devops_service.docker_dir.glob("*"))
        k8s_files = list(devops_service.k8s_dir.glob("*.yaml"))
        monitoring_files = list(devops_service.monitoring_dir.glob("*"))
        
        return {
            "infrastructure_components": {
                "docker": {
                    "directory": str(devops_service.docker_dir),
                    "files": [f.name for f in docker_files],
                    "file_count": len(docker_files)
                },
                "kubernetes": {
                    "directory": str(devops_service.k8s_dir),
                    "manifests": [f.name for f in k8s_files],
                    "manifest_count": len(k8s_files)
                },
                "monitoring": {
                    "directory": str(devops_service.monitoring_dir),
                    "configs": [f.name for f in monitoring_files],
                    "config_count": len(monitoring_files)
                }
            },
            "configuration": {
                "deployment": devops_service.config["deployment"],
                "monitoring": devops_service.config["monitoring"],
                "backup": devops_service.config["backup"],
                "security": devops_service.config["security"]
            },
            "service_health": await devops_service._check_service_health(),
            "infrastructure_ready": {
                "docker_configured": len(docker_files) >= 3,
                "kubernetes_configured": len(k8s_files) >= 3,
                "monitoring_configured": len(monitoring_files) >= 3,
                "all_ready": len(docker_files) >= 3 and len(k8s_files) >= 3 and len(monitoring_files) >= 3
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting infrastructure status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get infrastructure status")

@router.get("/devops/health")
async def get_production_health() -> Dict[str, Any]:
    """Get comprehensive production health check"""
    try:
        devops_service = get_devops_service()
        
        if not devops_service:
            return {
                "status": "unhealthy",
                "message": "DevOps service not running",
                "components": {}
            }
        
        # Get service health
        service_health = await devops_service._check_service_health()
        
        # Get latest metrics
        latest_metrics = devops_service.system_metrics[-1] if devops_service.system_metrics else None
        
        # Check infrastructure components
        components = {
            "devops_service": {
                "status": "healthy" if devops_service.is_running else "unhealthy",
                "background_tasks": len([t for t in devops_service.background_tasks if not t.done()])
            },
            "deployment_system": {
                "status": "healthy",
                "current_deployment": devops_service.current_deployment.version if devops_service.current_deployment else "unknown",
                "deployment_history": len(devops_service.deployment_history)
            },
            "monitoring": {
                "status": "healthy",
                "metrics_collected": len(devops_service.system_metrics),
                "alert_rules": len(devops_service.alert_rules),
                "active_alerts": len(devops_service.active_alerts)
            },
            "backup_system": {
                "status": "healthy",
                "total_backups": len(devops_service.backup_jobs),
                "successful_backups": len([b for b in devops_service.backup_jobs if b.status == "completed"]),
                "failed_backups": len([b for b in devops_service.backup_jobs if b.status == "failed"])
            },
            "system_resources": {
                "status": "healthy" if latest_metrics and latest_metrics.cpu_usage < 80 and latest_metrics.memory_usage < 85 else "warning",
                "cpu_usage": latest_metrics.cpu_usage if latest_metrics else 0,
                "memory_usage": latest_metrics.memory_usage if latest_metrics else 0,
                "disk_usage": latest_metrics.disk_usage if latest_metrics else 0
            }
        }
        
        # Add service health
        for service, status in service_health.items():
            components[f"{service}_service"] = {"status": status}
        
        # Overall status
        unhealthy_components = [name for name, comp in components.items() if comp.get("status") == "unhealthy"]
        warning_components = [name for name, comp in components.items() if comp.get("status") == "warning"]
        
        if unhealthy_components:
            overall_status = "unhealthy"
        elif warning_components:
            overall_status = "warning"
        else:
            overall_status = "healthy"
        
        return {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "components": components,
            "unhealthy_components": unhealthy_components,
            "warning_components": warning_components,
            "environment": devops_service.current_deployment.environment if devops_service.current_deployment else "unknown",
            "version": devops_service.current_deployment.version if devops_service.current_deployment else "unknown",
            "uptime": "running" if devops_service.is_running else "stopped"
        }
        
    except Exception as e:
        logger.error(f"Error getting production health: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@router.get("/devops/summary")
async def get_devops_summary() -> Dict[str, Any]:
    """Get comprehensive DevOps service summary"""
    try:
        devops_service = get_devops_service()
        
        if not devops_service:
            return {
                "message": "DevOps service not running",
                "service_status": "stopped",
                "capabilities": []
            }
        
        # Get comprehensive status
        status = devops_service.get_devops_status()
        
        return {
            "service_status": "running" if status["service_running"] else "stopped",
            "production_features": {
                "deployment_management": {
                    "current_deployment": status["current_deployment"],
                    "deployment_history": status["deployment_history_count"],
                    "environments_supported": ["development", "staging", "production"]
                },
                "monitoring_system": {
                    "metrics_collected": status["system_metrics"]["total_collected"],
                    "alert_rules": status["alerts"]["total_rules"],
                    "active_alerts": status["alerts"]["active_alerts"],
                    "monitoring_tools": ["Prometheus", "Grafana", "Custom Metrics"]
                },
                "backup_system": {
                    "total_backups": status["backups"]["total_backups"],
                    "successful_backups": status["backups"]["successful_backups"],
                    "backup_types": ["database", "files", "configuration", "full"],
                    "total_backup_size_gb": round(status["backups"]["total_backup_size"] / (1024**3), 2)
                },
                "infrastructure": {
                    "docker_configs": status["infrastructure"]["docker_configs"],
                    "k8s_manifests": status["infrastructure"]["k8s_manifests"],
                    "monitoring_configs": status["infrastructure"]["monitoring_configs"],
                    "orchestration_ready": True
                }
            },
            "current_system_status": {
                "cpu_usage": status["system_metrics"]["latest_cpu"],
                "memory_usage": status["system_metrics"]["latest_memory"],
                "disk_usage": status["system_metrics"]["latest_disk"],
                "health_status": "healthy" if status["system_metrics"]["latest_cpu"] < 80 else "warning"
            },
            "api_endpoints": [
                "POST /api/devops/deploy (Application deployment)",
                "GET /api/devops/deployments (Deployment history)",
                "GET /api/devops/metrics (System performance metrics)",
                "GET /api/devops/alerts (Alert management)",
                "GET /api/devops/backups (Backup management)",
                "GET /api/devops/infrastructure (Infrastructure status)",
                "GET /api/devops/health (Production health check)"
            ],
            "production_capabilities": [
                "Automated deployment with rollback",
                "Real-time system monitoring",
                "Automated backup scheduling",
                "Alert management and notification",
                "Container orchestration (Docker, K8s)",
                "Performance metrics collection",
                "Infrastructure as Code",
                "Production health monitoring"
            ],
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting DevOps summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to get DevOps summary")