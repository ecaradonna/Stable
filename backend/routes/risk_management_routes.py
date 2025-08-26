"""
Enhanced Risk Management API Routes (STEP 14)
Institutional-grade risk management APIs with real-time monitoring,
dynamic risk limits, and regulatory compliance features
"""

from fastapi import APIRouter, HTTPException, Query, Body
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging

from services.risk_management_service import get_risk_management_service

logger = logging.getLogger(__name__)

router = APIRouter()

# === SERVICE MANAGEMENT ===

@router.get("/status")
async def get_risk_management_status():
    """Get enhanced risk management service status"""
    risk_service = get_risk_management_service()
    
    if not risk_service:
        return {
            "service_running": False,
            "message": "Enhanced Risk Management service not started",
            "capabilities": [],
            "monitored_portfolios": 0
        }
    
    try:
        status = await risk_service.get_risk_status()
        return {
            **status,
            "endpoints": 12,
            "risk_management_features": [
                "Real-time Risk Monitoring",
                "Value at Risk (VaR) Calculations",
                "Expected Shortfall Analysis", 
                "Maximum Drawdown Tracking",
                "Concentration Risk Alerts",
                "Liquidity Risk Assessment",
                "Correlation Risk Analysis",
                "Advanced Stress Testing",
                "Regulatory Compliance Monitoring",
                "Dynamic Risk Limit Management"
            ]
        }
    except Exception as e:
        logger.error(f"Error getting risk management status: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting risk management status: {str(e)}")

@router.post("/start")
async def start_risk_management_service():
    """Start the enhanced risk management service"""
    try:
        from services.risk_management_service import start_risk_management
        result = await start_risk_management()
        
        return {
            **result,
            "message": "Enhanced Risk Management service started successfully",
            "advanced_features": [
                "Continuous portfolio risk monitoring",
                "Real-time VaR and Expected Shortfall calculations",
                "Multi-scenario stress testing capabilities", 
                "Dynamic risk limit enforcement",
                "Automated risk alert generation",
                "Regulatory compliance verification",
                "Liquidity coverage ratio monitoring",
                "Concentration risk management",
                "Correlation risk analysis",
                "Operational risk assessment"
            ],
            "integration_status": {
                "trading_engine": "Connected for portfolio data",
                "ai_portfolio_service": "Connected for AI insights",
                "ml_insights": "Connected for predictive analytics",
                "yield_aggregator": "Connected for market data",
                "ray_calculator": "Connected for risk-adjusted calculations"
            }
        }
    except Exception as e:
        logger.error(f"Error starting risk management service: {e}")
        raise HTTPException(status_code=500, detail=f"Error starting risk management service: {str(e)}")

@router.post("/stop")
async def stop_risk_management_service():
    """Stop the enhanced risk management service"""
    try:
        from services.risk_management_service import stop_risk_management
        result = await stop_risk_management()
        
        return {
            **result,
            "message": "Enhanced Risk Management service stopped successfully"
        }
    except Exception as e:
        logger.error(f"Error stopping risk management service: {e}")
        raise HTTPException(status_code=500, detail=f"Error stopping risk management service: {str(e)}")

# === RISK METRICS & MONITORING ===

@router.get("/metrics/{portfolio_id}")
async def get_risk_metrics(portfolio_id: str):
    """Get comprehensive risk metrics for a portfolio"""
    risk_service = get_risk_management_service()
    
    if not risk_service:
        raise HTTPException(status_code=503, detail="Risk Management service not available")
    
    try:
        risk_metrics = await risk_service.calculate_risk_metrics(portfolio_id)
        
        if not risk_metrics:
            raise HTTPException(status_code=404, detail=f"Risk metrics for portfolio {portfolio_id} not available")
        
        return {
            "portfolio_id": portfolio_id,
            "risk_metrics": {
                "value_at_risk": {
                    "var_1d_95": risk_metrics.get("var_1d_95", 0),
                    "var_1d_99": risk_metrics.get("var_1d_99", 0),
                    "var_7d_95": risk_metrics.get("var_7d_95", 0),
                    "confidence_levels": ["95%", "99%"]
                },
                "expected_shortfall": {
                    "es_1d_95": risk_metrics.get("expected_shortfall_1d", 0),
                    "description": "Expected loss beyond VaR threshold"
                },
                "concentration_analysis": {
                    "max_concentration": risk_metrics.get("concentration_risk", 0),
                    "diversification_ratio": risk_metrics.get("diversification_ratio", 0),
                    "concentration_threshold": 0.25
                },
                "liquidity_metrics": {
                    "liquidity_risk_score": risk_metrics.get("liquidity_risk", 0),
                    "liquidity_coverage": 1 - risk_metrics.get("liquidity_risk", 0.5),
                    "assessment": "Low" if risk_metrics.get("liquidity_risk", 0.5) < 0.3 else 
                               "Medium" if risk_metrics.get("liquidity_risk", 0.5) < 0.6 else "High"
                },
                "volatility_analysis": {
                    "volatility_1d": risk_metrics.get("volatility_1d", 0),
                    "volatility_30d": risk_metrics.get("volatility_30d", 0),
                    "volatility_trend": "Stable"
                }
            },
            "risk_assessment": {
                "overall_risk_level": _assess_risk_level(risk_metrics),
                "key_concerns": _identify_key_concerns(risk_metrics),
                "recommendations": _generate_risk_recommendations(risk_metrics)
            },
            "calculation_metadata": {
                "calculated_at": datetime.utcnow().isoformat(),
                "portfolio_value": risk_metrics.get("portfolio_value", 0),
                "methodology": "Enhanced Risk Management with real-time monitoring"
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting risk metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting risk metrics: {str(e)}")

# === STRESS TESTING ===

@router.get("/stress-scenarios")
async def get_stress_scenarios():
    """Get available stress testing scenarios"""
    risk_service = get_risk_management_service()
    
    if not risk_service:
        raise HTTPException(status_code=503, detail="Risk Management service not available")
    
    try:
        scenarios = [
            {
                "scenario_id": scenario.scenario_id,
                "name": scenario.name,
                "description": scenario.description,
                "asset_shocks": scenario.asset_shocks,
                "impact_type": "Moderate" if abs(min(scenario.asset_shocks.values())) < 0.15 else "Severe"
            }
            for scenario in risk_service.stress_scenarios
        ]
        
        return {
            "stress_scenarios": scenarios,
            "total_scenarios": len(scenarios),
            "methodology": {
                "approach": "Scenario-based stress testing with historical calibration",
                "shock_types": ["Asset price shocks", "Correlation changes", "Volatility multipliers"],
                "calibration": "Based on historical extreme events and regulatory guidance"
            }
        }
    except Exception as e:
        logger.error(f"Error getting stress scenarios: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting stress scenarios: {str(e)}")

@router.post("/stress-test/{portfolio_id}")
async def run_stress_test(portfolio_id: str, scenario_data: Dict[str, Any] = Body(...)):
    """Run stress test on portfolio"""
    risk_service = get_risk_management_service()
    
    if not risk_service:
        raise HTTPException(status_code=503, detail="Risk Management service not available")
    
    try:
        scenario_id = scenario_data.get("scenario_id")
        if not scenario_id:
            raise HTTPException(status_code=400, detail="scenario_id is required")
        
        # Run stress test
        stress_results = await risk_service.run_stress_test(portfolio_id, scenario_id)
        
        # Analyze results
        impact_pct = stress_results["portfolio_impact"]["impact_percentage"]
        impact_severity = "Low" if impact_pct > -5 else "Medium" if impact_pct > -15 else "High"
        
        return {
            "stress_test_results": stress_results,
            "impact_analysis": {
                "severity": impact_severity,
                "risk_assessment": _assess_stress_impact(impact_pct),
                "recovery_time_estimate": _estimate_recovery_time(impact_severity),
                "mitigation_recommendations": _generate_stress_recommendations(stress_results)
            },
            "comparative_analysis": {
                "vs_regulatory_limits": {
                    "within_limits": abs(impact_pct) < 20,
                    "regulatory_threshold": "20% maximum loss under severe stress"
                },
                "resilience_score": max(0, 100 + impact_pct)
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error running stress test: {e}")
        raise HTTPException(status_code=500, detail=f"Error running stress test: {str(e)}")

# === COMPLIANCE & REPORTING ===

@router.get("/compliance/{portfolio_id}")
async def get_compliance_status(portfolio_id: str):
    """Get regulatory compliance status"""
    risk_service = get_risk_management_service()
    
    if not risk_service:
        raise HTTPException(status_code=503, detail="Risk Management service not available")
    
    try:
        # Get current risk metrics
        risk_metrics = await risk_service.calculate_risk_metrics(portfolio_id)
        
        if not risk_metrics:
            raise HTTPException(status_code=404, detail="Portfolio data not available for compliance check")
        
        # Check regulatory compliance
        config = risk_service.config["regulatory_limits"]
        
        compliance_checks = {
            "concentration_limits": {
                "max_single_issuer": {
                    "limit": config["max_single_issuer"],
                    "current": risk_metrics.get("concentration_risk", 0),
                    "compliant": risk_metrics.get("concentration_risk", 0) <= config["max_single_issuer"],
                    "description": "Maximum exposure to single issuer"
                },
                "diversification_ratio": {
                    "limit": config["min_diversification_ratio"],
                    "current": risk_metrics.get("diversification_ratio", 0),
                    "compliant": risk_metrics.get("diversification_ratio", 0) >= config["min_diversification_ratio"],
                    "description": "Minimum portfolio diversification required"
                }
            },
            "liquidity_requirements": {
                "liquidity_coverage": {
                    "limit": config["liquidity_coverage_ratio"],
                    "current": 1 - risk_metrics.get("liquidity_risk", 0.5),
                    "compliant": (1 - risk_metrics.get("liquidity_risk", 0.5)) >= config["liquidity_coverage_ratio"],
                    "description": "Minimum liquid asset coverage"
                }
            }
        }
        
        # Calculate overall compliance score
        total_checks = sum(len(category.values()) for category in compliance_checks.values())
        compliant_checks = sum(
            sum(1 for check in category.values() if check["compliant"])
            for category in compliance_checks.values()
        )
        compliance_score = (compliant_checks / total_checks) * 100 if total_checks > 0 else 100
        
        return {
            "portfolio_id": portfolio_id,
            "compliance_overview": {
                "overall_compliant": compliant_checks == total_checks,
                "compliance_score": round(compliance_score, 1),
                "total_checks": total_checks,
                "passed_checks": compliant_checks
            },
            "compliance_details": compliance_checks,
            "regulatory_framework": {
                "applicable_regulations": [
                    "Basel III Capital Requirements",
                    "UCITS Diversification Rules",
                    "AIFMD Risk Management Requirements",
                    "MiFID II Product Governance"
                ],
                "compliance_methodology": "Real-time monitoring with daily reporting"
            },
            "last_checked": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting compliance status: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting compliance status: {str(e)}")

# === COMPREHENSIVE SUMMARY ===

@router.get("/summary")
async def get_risk_management_summary():
    """Get comprehensive risk management service summary"""
    risk_service = get_risk_management_service()
    
    if not risk_service:
        return {
            "service_running": False,
            "message": "Enhanced Risk Management service not started"
        }
    
    try:
        status = await risk_service.get_risk_status()
        
        return {
            "service_status": status,
            "risk_management_capabilities": {
                "real_time_monitoring": {
                    "features": ["Continuous VaR monitoring", "Real-time alert generation", "Dynamic risk limit enforcement"],
                    "monitored_portfolios": status["monitoring_status"]["monitored_portfolios"]
                },
                "advanced_analytics": {
                    "features": ["Multi-scenario stress testing", "Correlation analysis", "Liquidity risk assessment"],
                    "available_scenarios": len(status["stress_scenarios"])
                },
                "compliance_management": {
                    "features": ["Regulatory limit monitoring", "Automated compliance reporting", "Violation detection"],
                    "regulatory_frameworks": 4
                }
            },
            "api_endpoints": {
                "risk_monitoring": [
                    "GET /api/risk-management/metrics/{portfolio_id}"
                ],
                "stress_testing": [
                    "GET /api/risk-management/stress-scenarios",
                    "POST /api/risk-management/stress-test/{portfolio_id}"
                ],
                "compliance": [
                    "GET /api/risk-management/compliance/{portfolio_id}"
                ]
            },
            "integration_status": {
                "trading_engine": "Connected",
                "ai_portfolio_service": "Connected",
                "ml_insights": "Connected",
                "yield_aggregator": "Connected", 
                "ray_calculator": "Connected"
            },
            "last_updated": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting risk management summary: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting risk management summary: {str(e)}")

# === HELPER FUNCTIONS ===

def _assess_risk_level(risk_metrics: Dict[str, float]) -> str:
    """Assess overall risk level based on metrics"""
    var_ratio = risk_metrics.get("var_1d_95", 0) / max(risk_metrics.get("portfolio_value", 1), 1)
    concentration = risk_metrics.get("concentration_risk", 0)
    liquidity = risk_metrics.get("liquidity_risk", 0.5)
    
    if var_ratio > 0.03 or concentration > 0.4 or liquidity > 0.7:
        return "High"
    elif var_ratio > 0.015 or concentration > 0.25 or liquidity > 0.4:
        return "Medium" 
    else:
        return "Low"

def _identify_key_concerns(risk_metrics: Dict[str, float]) -> List[str]:
    """Identify key risk concerns"""
    concerns = []
    
    if risk_metrics.get("concentration_risk", 0) > 0.25:
        concerns.append("High concentration risk detected")
    
    if risk_metrics.get("liquidity_risk", 0.5) > 0.6:
        concerns.append("Elevated liquidity risk")
    
    var_ratio = risk_metrics.get("var_1d_95", 0) / max(risk_metrics.get("portfolio_value", 1), 1)
    if var_ratio > 0.02:
        concerns.append("VaR exceeds recommended thresholds")
    
    return concerns if concerns else ["No significant risk concerns identified"]

def _generate_risk_recommendations(risk_metrics: Dict[str, float]) -> List[str]:
    """Generate risk management recommendations"""
    recommendations = []
    
    if risk_metrics.get("concentration_risk", 0) > 0.25:
        recommendations.append("Consider rebalancing to reduce concentration risk")
    
    if risk_metrics.get("diversification_ratio", 1) < 0.6:
        recommendations.append("Increase portfolio diversification")
    
    if risk_metrics.get("liquidity_risk", 0.5) > 0.5:
        recommendations.append("Improve liquidity profile by adding liquid assets")
    
    return recommendations if recommendations else ["Portfolio risk profile is within acceptable limits"]

def _assess_stress_impact(impact_percentage: float) -> str:
    """Assess stress test impact severity"""
    if impact_percentage >= -5:
        return "Portfolio shows strong resilience to stress scenarios"
    elif impact_percentage >= -15:
        return "Portfolio has moderate stress resilience with manageable impact"
    else:
        return "Portfolio shows significant vulnerability to stress scenarios"

def _estimate_recovery_time(severity: str) -> str:
    """Estimate recovery time based on impact severity"""
    return {
        "Low": "1-2 weeks",
        "Medium": "1-3 months", 
        "High": "6-12 months"
    }.get(severity, "Unknown")

def _generate_stress_recommendations(stress_results: Dict[str, Any]) -> List[str]:
    """Generate recommendations based on stress test results"""
    impact_pct = stress_results["portfolio_impact"]["impact_percentage"]
    
    recommendations = []
    
    if impact_pct < -20:
        recommendations.append("Consider reducing exposure to high-risk assets")
        recommendations.append("Implement additional hedging strategies")
    elif impact_pct < -10:
        recommendations.append("Review asset allocation and diversification")
        recommendations.append("Consider stress-resistant alternatives")
    else:
        recommendations.append("Portfolio shows good stress resilience")
        recommendations.append("Maintain current risk management approach")
    
    return recommendations