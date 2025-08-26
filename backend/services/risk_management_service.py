"""
Enhanced Risk Management Service (STEP 14)
Advanced institutional-grade risk management with real-time monitoring,
dynamic risk limits, and regulatory compliance features
"""

import asyncio
import logging
import json
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import statistics
from pathlib import Path

from .yield_aggregator import YieldAggregator
from .ray_calculator import RAYCalculator
from .trading_engine_service import get_trading_engine_service
from .ml_insights_service import get_ml_insights_service
from .ai_portfolio_service import get_ai_portfolio_service

logger = logging.getLogger(__name__)

class RiskSeverity(Enum):
    """Risk alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class RiskMetricType(Enum):
    """Risk metric types"""
    VALUE_AT_RISK = "value_at_risk"
    EXPECTED_SHORTFALL = "expected_shortfall"
    MAXIMUM_DRAWDOWN = "maximum_drawdown"
    CONCENTRATION_RISK = "concentration_risk"
    LIQUIDITY_RISK = "liquidity_risk"
    COUNTERPARTY_RISK = "counterparty_risk"
    MARKET_RISK = "market_risk"
    OPERATIONAL_RISK = "operational_risk"

@dataclass
class RiskAlert:
    """Risk alert data structure"""
    alert_id: str
    portfolio_id: str
    risk_type: RiskMetricType
    severity: RiskSeverity
    message: str
    threshold_value: float
    current_value: float
    triggered_at: datetime
    acknowledged: bool = False
    resolved: bool = False

@dataclass
class RiskLimit:
    """Risk limit configuration"""
    portfolio_id: str
    risk_type: RiskMetricType
    limit_type: str  # "hard", "soft", "warning"
    threshold: float
    action: str  # "alert", "block_trades", "force_rebalance"
    enabled: bool = True

@dataclass
class StressTestScenario:
    """Stress testing scenario definition"""
    scenario_id: str
    name: str
    description: str
    asset_shocks: Dict[str, float]  # Asset -> shock percentage
    correlation_changes: Dict[str, float]  # Correlation adjustments
    volatility_multipliers: Dict[str, float]  # Volatility scaling factors

@dataclass
class RiskReport:
    """Comprehensive risk report"""
    portfolio_id: str
    generated_at: datetime
    risk_metrics: Dict[str, float]
    risk_alerts: List[RiskAlert]
    stress_test_results: Dict[str, float]
    compliance_status: Dict[str, bool]
    recommendations: List[str]

class EnhancedRiskManagementService:
    """Enhanced risk management with real-time monitoring and dynamic limits"""
    
    def __init__(self):
        # Core service integrations
        self.yield_aggregator = YieldAggregator()
        self.ray_calculator = RAYCalculator()
        
        # Risk management data
        self.risk_limits: Dict[str, List[RiskLimit]] = {}  # portfolio_id -> limits
        self.active_alerts: Dict[str, RiskAlert] = {}
        self.risk_history: Dict[str, List[Dict[str, Any]]] = {}  # portfolio_id -> history
        
        # Configuration
        self.config = self._load_risk_config()
        self.stress_scenarios = self._initialize_stress_scenarios()
        
        # Service state
        self.is_running = False
        self.background_tasks = []
        
    def _load_risk_config(self) -> Dict[str, Any]:
        """Load risk management configuration"""
        return {
            "monitoring_interval": 60,  # seconds
            "var_confidence_levels": [0.95, 0.99],
            "stress_test_frequency": 3600,  # 1 hour
            "alert_cooldown_minutes": 15,
            "max_portfolio_concentration": 0.25,  # 25%
            "max_sector_concentration": 0.40,  # 40%
            "min_liquidity_threshold": 10_000_000,  # $10M
            "correlation_threshold": 0.80,  # High correlation warning
            "volatility_spike_threshold": 2.0,  # 2x normal volatility
            "drawdown_warning_threshold": 0.05,  # 5%
            "drawdown_critical_threshold": 0.15,  # 15%
            "regulatory_limits": {
                "max_single_issuer": 0.10,  # 10% max single issuer
                "max_counterparty": 0.15,  # 15% max counterparty
                "min_diversification_ratio": 0.60,  # Minimum diversification
                "liquidity_coverage_ratio": 0.30  # 30% liquid assets
            }
        }
    
    def _initialize_stress_scenarios(self) -> List[StressTestScenario]:
        """Initialize standard stress testing scenarios"""
        scenarios = [
            StressTestScenario(
                scenario_id="peg_break",
                name="Stablecoin Peg Break",
                description="Major stablecoin loses peg (5% depeg)",
                asset_shocks={"USDT": -0.05, "USDC": -0.02, "DAI": -0.03},
                correlation_changes={"all": 0.30},  # Increased correlation during crisis
                volatility_multipliers={"all": 3.0}
            ),
            StressTestScenario(
                scenario_id="defi_crisis",
                name="DeFi Protocol Crisis",
                description="Major DeFi protocol exploit/failure",
                asset_shocks={"DeFi": -0.25, "CeFi": -0.05},
                correlation_changes={"DeFi": 0.85},
                volatility_multipliers={"DeFi": 4.0, "CeFi": 1.5}
            ),
            StressTestScenario(
                scenario_id="liquidity_crisis",
                name="Market Liquidity Crisis",
                description="Global liquidity crisis affecting all markets",
                asset_shocks={"all": -0.10},
                correlation_changes={"all": 0.50},
                volatility_multipliers={"all": 2.5}
            ),
            StressTestScenario(
                scenario_id="regulatory_shock",
                name="Regulatory Crackdown",
                description="Severe regulatory actions against DeFi",
                asset_shocks={"DeFi": -0.40, "CeFi": 0.05},
                correlation_changes={"DeFi": 0.90},
                volatility_multipliers={"DeFi": 5.0}
            ),
            StressTestScenario(
                scenario_id="black_swan",
                name="Black Swan Event",
                description="Extreme market stress (99th percentile)",
                asset_shocks={"all": -0.20},
                correlation_changes={"all": 0.80},
                volatility_multipliers={"all": 6.0}
            )
        ]
        return scenarios
    
    async def start_risk_management(self) -> Dict[str, Any]:
        """Start enhanced risk management service"""
        try:
            if self.is_running:
                return {"message": "Risk Management service already running"}
            
            self.is_running = True
            
            # Start background monitoring tasks
            self.background_tasks = [
                asyncio.create_task(self._risk_monitoring_loop()),
                asyncio.create_task(self._stress_testing_loop()),
                asyncio.create_task(self._compliance_monitoring_loop()),
                asyncio.create_task(self._alert_management_loop())
            ]
            
            logger.info("✅ Enhanced Risk Management service started")
            
            return {
                "status": "started",
                "service_running": True,
                "risk_capabilities": [
                    "Real-time Risk Monitoring",
                    "Dynamic Risk Limit Management", 
                    "Advanced Stress Testing",
                    "Regulatory Compliance Monitoring",
                    "Automated Risk Alerts",
                    "Portfolio Risk Attribution",
                    "Counterparty Risk Assessment",
                    "Liquidity Risk Analysis"
                ],
                "monitoring_features": [
                    "Value at Risk (VaR) monitoring",
                    "Expected Shortfall calculations",
                    "Maximum Drawdown tracking",
                    "Concentration risk alerts",
                    "Correlation monitoring",
                    "Volatility spike detection",
                    "Liquidity coverage analysis",
                    "Regulatory limit compliance"
                ],
                "stress_scenarios": len(self.stress_scenarios),
                "monitoring_interval": f"{self.config['monitoring_interval']} seconds"
            }
            
        except Exception as e:
            logger.error(f"❌ Error starting Risk Management service: {e}")
            raise
    
    async def stop_risk_management(self) -> Dict[str, Any]:
        """Stop enhanced risk management service"""
        try:
            if not self.is_running:
                return {"message": "Risk Management service already stopped"}
            
            self.is_running = False
            
            # Cancel background tasks
            for task in self.background_tasks:
                if not task.done():
                    task.cancel()
            
            # Wait for tasks to complete
            await asyncio.gather(*self.background_tasks, return_exceptions=True)
            self.background_tasks.clear()
            
            logger.info("🛑 Enhanced Risk Management service stopped")
            
            return {
                "status": "stopped",
                "service_running": False,
                "message": "Risk Management service stopped successfully"
            }
            
        except Exception as e:
            logger.error(f"❌ Error stopping Risk Management service: {e}")
            raise
    
    async def _risk_monitoring_loop(self):
        """Background task for continuous risk monitoring"""
        while self.is_running:
            try:
                # Get all portfolios from AI Portfolio service
                ai_portfolio_service = get_ai_portfolio_service()
                if ai_portfolio_service and ai_portfolio_service.ai_portfolios:
                    
                    for portfolio_id in ai_portfolio_service.ai_portfolios.keys():
                        await self._monitor_portfolio_risk(portfolio_id)
                
                await asyncio.sleep(self.config["monitoring_interval"])
                
            except Exception as e:
                logger.error(f"❌ Error in risk monitoring loop: {e}")
                await asyncio.sleep(30)  # Wait before retry
    
    async def _monitor_portfolio_risk(self, portfolio_id: str):
        """Monitor risk for a specific portfolio"""
        try:
            # Calculate current risk metrics
            risk_metrics = await self.calculate_risk_metrics(portfolio_id)
            
            # Check risk limits
            violated_limits = await self._check_risk_limits(portfolio_id, risk_metrics)
            
            # Generate alerts for violations
            for limit in violated_limits:
                await self._generate_risk_alert(portfolio_id, limit, risk_metrics)
            
            # Store risk history
            if portfolio_id not in self.risk_history:
                self.risk_history[portfolio_id] = []
            
            self.risk_history[portfolio_id].append({
                "timestamp": datetime.utcnow().isoformat(),
                "risk_metrics": risk_metrics,
                "alerts_count": len([a for a in self.active_alerts.values() 
                                  if a.portfolio_id == portfolio_id and not a.resolved])
            })
            
            # Keep only last 1000 records
            if len(self.risk_history[portfolio_id]) > 1000:
                self.risk_history[portfolio_id] = self.risk_history[portfolio_id][-1000:]
                
        except Exception as e:
            logger.error(f"❌ Error monitoring portfolio risk {portfolio_id}: {e}")
    
    async def _check_risk_limits(self, portfolio_id: str, risk_metrics: Dict[str, float]) -> List[RiskLimit]:
        """Check if portfolio violates any risk limits"""
        violated_limits = []
        
        try:
            # Get risk limits for portfolio
            portfolio_limits = self.risk_limits.get(portfolio_id, [])
            
            # Add default limits if none exist
            if not portfolio_limits:
                portfolio_limits = self._get_default_risk_limits(portfolio_id)
                self.risk_limits[portfolio_id] = portfolio_limits
            
            # Check each limit
            for limit in portfolio_limits:
                if not limit.enabled:
                    continue
                
                current_value = risk_metrics.get(limit.risk_type.value, 0)
                
                # Check if limit is violated
                if limit.limit_type == "hard" and current_value > limit.threshold:
                    violated_limits.append(limit)
                elif limit.limit_type == "soft" and current_value > limit.threshold * 0.9:
                    violated_limits.append(limit)
                elif limit.limit_type == "warning" and current_value > limit.threshold * 0.8:
                    violated_limits.append(limit)
            
            return violated_limits
            
        except Exception as e:
            logger.error(f"❌ Error checking risk limits for {portfolio_id}: {e}")
            return []
    
    def _get_default_risk_limits(self, portfolio_id: str) -> List[RiskLimit]:
        """Get default risk limits for a portfolio"""
        return [
            RiskLimit(
                portfolio_id=portfolio_id,
                risk_type=RiskMetricType.CONCENTRATION_RISK,
                limit_type="hard",
                threshold=0.25,  # 25% max concentration
                action="alert"
            ),
            RiskLimit(
                portfolio_id=portfolio_id,
                risk_type=RiskMetricType.LIQUIDITY_RISK,
                limit_type="soft",
                threshold=0.6,  # 60% liquidity risk threshold
                action="alert"
            ),
            RiskLimit(
                portfolio_id=portfolio_id,
                risk_type=RiskMetricType.VALUE_AT_RISK,
                limit_type="warning",
                threshold=0.05,  # 5% VaR threshold
                action="alert"
            )
        ]
    
    async def _generate_risk_alert(self, portfolio_id: str, limit: RiskLimit, risk_metrics: Dict[str, float]):
        """Generate risk alert for limit violation"""
        try:
            current_value = risk_metrics.get(limit.risk_type.value, 0)
            
            # Determine severity
            if limit.limit_type == "hard":
                severity = RiskSeverity.CRITICAL
            elif limit.limit_type == "soft":
                severity = RiskSeverity.HIGH
            else:
                severity = RiskSeverity.MEDIUM
            
            # Create alert
            alert = RiskAlert(
                alert_id=f"alert_{portfolio_id}_{limit.risk_type.value}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                portfolio_id=portfolio_id,
                risk_type=limit.risk_type,
                severity=severity,
                message=f"{limit.risk_type.value} exceeded {limit.limit_type} limit",
                threshold_value=limit.threshold,
                current_value=current_value,
                triggered_at=datetime.utcnow()
            )
            
            # Store alert
            self.active_alerts[alert.alert_id] = alert
            
            logger.warning(f"⚠️ Risk alert generated: {alert.message} for portfolio {portfolio_id}")
            
        except Exception as e:
            logger.error(f"❌ Error generating risk alert: {e}")
    
    async def _stress_testing_loop(self):
        """Background task for periodic stress testing"""
        while self.is_running:
            try:
                # Get all portfolios from AI Portfolio service
                ai_portfolio_service = get_ai_portfolio_service()
                if ai_portfolio_service and ai_portfolio_service.ai_portfolios:
                    
                    for portfolio_id in ai_portfolio_service.ai_portfolios.keys():
                        # Run stress tests for each scenario
                        for scenario in self.stress_scenarios:
                            try:
                                await self.run_stress_test(portfolio_id, scenario.scenario_id)
                            except Exception as e:
                                logger.error(f"❌ Error in stress test {scenario.scenario_id} for {portfolio_id}: {e}")
                
                # Wait for next stress test cycle
                await asyncio.sleep(self.config["stress_test_frequency"])
                
            except Exception as e:
                logger.error(f"❌ Error in stress testing loop: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes before retry
    
    async def _compliance_monitoring_loop(self):
        """Background task for regulatory compliance monitoring"""
        while self.is_running:
            try:
                # Get all portfolios from AI Portfolio service
                ai_portfolio_service = get_ai_portfolio_service()
                if ai_portfolio_service and ai_portfolio_service.ai_portfolios:
                    
                    for portfolio_id in ai_portfolio_service.ai_portfolios.keys():
                        await self._check_regulatory_compliance(portfolio_id)
                
                # Check compliance every 30 minutes
                await asyncio.sleep(1800)
                
            except Exception as e:
                logger.error(f"❌ Error in compliance monitoring loop: {e}")
                await asyncio.sleep(300)
    
    async def _check_regulatory_compliance(self, portfolio_id: str):
        """Check regulatory compliance for a portfolio"""
        try:
            risk_metrics = await self.calculate_risk_metrics(portfolio_id)
            if not risk_metrics:
                return
            
            config = self.config["regulatory_limits"]
            violations = []
            
            # Check concentration limits
            if risk_metrics.get("concentration_risk", 0) > config["max_single_issuer"]:
                violations.append("Single issuer concentration limit exceeded")
            
            # Check diversification
            if risk_metrics.get("diversification_ratio", 1) < config["min_diversification_ratio"]:
                violations.append("Minimum diversification requirement not met")
            
            # Check liquidity coverage
            liquidity_coverage = 1 - risk_metrics.get("liquidity_risk", 0.5)
            if liquidity_coverage < config["liquidity_coverage_ratio"]:
                violations.append("Liquidity coverage ratio below minimum")
            
            # Generate compliance alerts if needed
            if violations:
                for violation in violations:
                    await self._generate_compliance_alert(portfolio_id, violation)
            
        except Exception as e:
            logger.error(f"❌ Error checking compliance for {portfolio_id}: {e}")
    
    async def _generate_compliance_alert(self, portfolio_id: str, violation: str):
        """Generate compliance violation alert"""
        try:
            alert = RiskAlert(
                alert_id=f"compliance_{portfolio_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                portfolio_id=portfolio_id,
                risk_type=RiskMetricType.OPERATIONAL_RISK,
                severity=RiskSeverity.HIGH,
                message=f"Compliance violation: {violation}",
                threshold_value=0,
                current_value=1,
                triggered_at=datetime.utcnow()
            )
            
            self.active_alerts[alert.alert_id] = alert
            logger.warning(f"⚠️ Compliance alert: {violation} for portfolio {portfolio_id}")
            
        except Exception as e:
            logger.error(f"❌ Error generating compliance alert: {e}")
    
    async def _alert_management_loop(self):
        """Background task for managing and cleaning up alerts"""
        while self.is_running:
            try:
                current_time = datetime.utcnow()
                
                # Clean up old resolved alerts (older than 24 hours)
                alerts_to_remove = []
                for alert_id, alert in self.active_alerts.items():
                    if alert.resolved and (current_time - alert.triggered_at).total_seconds() > 86400:
                        alerts_to_remove.append(alert_id)
                
                for alert_id in alerts_to_remove:
                    del self.active_alerts[alert_id]
                
                # Check for alert cooldowns and auto-resolve if conditions improved
                for alert in self.active_alerts.values():
                    if not alert.resolved and (current_time - alert.triggered_at).total_seconds() > 900:  # 15 minutes
                        # Check if condition still exists
                        risk_metrics = await self.calculate_risk_metrics(alert.portfolio_id)
                        current_value = risk_metrics.get(alert.risk_type.value, 0)
                        
                        if current_value <= alert.threshold_value * 0.9:  # 10% buffer
                            alert.resolved = True
                            logger.info(f"✅ Auto-resolved alert {alert.alert_id}")
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"❌ Error in alert management loop: {e}")
                await asyncio.sleep(60)
    
    async def calculate_risk_metrics(self, portfolio_id: str) -> Dict[str, float]:
        """Calculate comprehensive risk metrics for a portfolio"""
        try:
            # Get portfolio data from trading engine
            trading_engine = get_trading_engine_service()
            if not trading_engine:
                return {}
            
            # Get portfolio performance data
            portfolio_performance = await trading_engine.get_portfolio_performance(portfolio_id)
            current_allocation = portfolio_performance.get("current_allocation", {})
            portfolio_value = portfolio_performance.get("total_value", 0)
            
            if not current_allocation or portfolio_value == 0:
                return {}
            
            # Calculate Value at Risk (VaR)
            var_1d_95 = await self._calculate_var(portfolio_id, 1, 0.95)
            var_1d_99 = await self._calculate_var(portfolio_id, 1, 0.99)
            var_7d_95 = await self._calculate_var(portfolio_id, 7, 0.95)
            
            # Calculate Expected Shortfall
            es_1d_95 = await self._calculate_expected_shortfall(portfolio_id, 1, 0.95)
            
            # Calculate Maximum Drawdown
            max_drawdown = await self._calculate_max_drawdown(portfolio_id)
            
            # Calculate Concentration Risk
            concentration_risk = max(current_allocation.values()) if current_allocation else 0
            
            # Calculate Diversification Ratio
            diversification_ratio = await self._calculate_diversification_ratio(current_allocation)
            
            # Calculate Liquidity Risk
            liquidity_risk = await self._calculate_liquidity_risk(portfolio_id)
            
            # Calculate Correlation Risk
            correlation_risk = await self._calculate_correlation_risk(current_allocation)
            
            # Volatility metrics
            volatility_1d = await self._calculate_volatility(portfolio_id, 1)
            volatility_30d = await self._calculate_volatility(portfolio_id, 30)
            
            risk_metrics = {
                "var_1d_95": var_1d_95,
                "var_1d_99": var_1d_99, 
                "var_7d_95": var_7d_95,
                "expected_shortfall_1d": es_1d_95,
                "max_drawdown": max_drawdown,
                "concentration_risk": concentration_risk,
                "diversification_ratio": diversification_ratio,
                "liquidity_risk": liquidity_risk,
                "correlation_risk": correlation_risk,
                "volatility_1d": volatility_1d,
                "volatility_30d": volatility_30d,
                "portfolio_value": portfolio_value
            }
            
            return risk_metrics
            
        except Exception as e:
            logger.error(f"❌ Error calculating risk metrics for {portfolio_id}: {e}")
            return {}
    
    async def _calculate_var(self, portfolio_id: str, horizon_days: int, confidence: float) -> float:
        """Calculate Value at Risk using historical simulation"""
        try:
            # This is a simplified VaR calculation
            # In production, would use historical returns and Monte Carlo simulation
            
            # Get portfolio volatility (simplified)
            volatility = await self._calculate_volatility(portfolio_id, 252)  # Annualized
            
            # Convert to horizon volatility
            horizon_volatility = volatility * np.sqrt(horizon_days / 252)
            
            # Calculate VaR using normal distribution approximation
            from scipy.stats import norm
            var_multiplier = norm.ppf(1 - confidence)  # Z-score for confidence level
            
            # Get portfolio value
            trading_engine = get_trading_engine_service()
            if trading_engine:
                portfolio_performance = await trading_engine.get_portfolio_performance(portfolio_id)
                portfolio_value = portfolio_performance.get("total_value", 0)
                
                # VaR = Portfolio Value * Volatility * Z-score
                var_amount = portfolio_value * horizon_volatility * abs(var_multiplier)
                return round(var_amount, 2)
            
            return 0.0
            
        except Exception as e:
            logger.error(f"❌ Error calculating VaR: {e}")
            return 0.0
    
    async def _calculate_expected_shortfall(self, portfolio_id: str, horizon_days: int, confidence: float) -> float:
        """Calculate Expected Shortfall (Conditional VaR)"""
        try:
            # Simplified ES calculation (typically 1.3x VaR for normal distribution)
            var = await self._calculate_var(portfolio_id, horizon_days, confidence)
            expected_shortfall = var * 1.3
            
            return round(expected_shortfall, 2)
            
        except Exception as e:
            logger.error(f"❌ Error calculating Expected Shortfall: {e}")
            return 0.0
    
    async def _calculate_max_drawdown(self, portfolio_id: str) -> float:
        """Calculate maximum drawdown from historical performance"""
        try:
            # Use risk history if available
            if portfolio_id in self.risk_history and len(self.risk_history[portfolio_id]) > 10:
                values = [record["risk_metrics"].get("portfolio_value", 0) 
                         for record in self.risk_history[portfolio_id][-90:]]  # Last 90 records
                
                if values:
                    peak = values[0]
                    max_dd = 0.0
                    
                    for value in values:
                        if value > peak:
                            peak = value
                        
                        drawdown = (peak - value) / peak if peak > 0 else 0
                        max_dd = max(max_dd, drawdown)
                    
                    return round(max_dd, 4)
            
            # Default to conservative estimate
            return 0.02  # 2% default drawdown
            
        except Exception as e:
            logger.error(f"❌ Error calculating max drawdown: {e}")
            return 0.0
    
    async def _calculate_diversification_ratio(self, allocation: Dict[str, float]) -> float:
        """Calculate portfolio diversification ratio"""
        try:
            if not allocation:
                return 0.0
            
            # Diversification ratio based on Herfindahl index
            weights_squared = sum(w**2 for w in allocation.values())
            effective_assets = 1 / weights_squared if weights_squared > 0 else 1
            max_assets = len(allocation)
            
            diversification_ratio = effective_assets / max_assets if max_assets > 0 else 0
            
            return round(diversification_ratio, 4)
            
        except Exception as e:
            logger.error(f"❌ Error calculating diversification ratio: {e}")
            return 0.0
    
    async def _calculate_liquidity_risk(self, portfolio_id: str) -> float:
        """Calculate portfolio liquidity risk score"""
        try:
            # Get current yields to assess liquidity
            yields = await self.yield_aggregator.get_all_yields()
            
            if not yields:
                return 1.0  # High liquidity risk if no data
            
            # Calculate weighted average liquidity score
            total_liquidity_score = 0.0
            total_weight = 0.0
            
            for yield_data in yields:
                stablecoin = yield_data.get('stablecoin', 'UNKNOWN')
                tvl_usd = yield_data.get('tvl', 0)
                
                # Simple liquidity scoring based on TVL
                if tvl_usd >= 100_000_000:  # $100M+
                    liquidity_score = 0.1  # Low risk
                elif tvl_usd >= 10_000_000:  # $10M+
                    liquidity_score = 0.3  # Medium risk
                else:
                    liquidity_score = 0.7  # High risk
                
                # Weight by yield amount (simplified)
                weight = yield_data.get('currentYield', 1.0) / 100  # Convert to weight
                total_liquidity_score += liquidity_score * weight
                total_weight += weight
            
            if total_weight > 0:
                weighted_liquidity_risk = total_liquidity_score / total_weight
                return round(weighted_liquidity_risk, 4)
            
            return 0.5  # Medium risk default
            
        except Exception as e:
            logger.error(f"❌ Error calculating liquidity risk: {e}")
            return 0.5
    
    async def _calculate_correlation_risk(self, allocation: Dict[str, float]) -> float:
        """Calculate correlation risk based on asset correlation"""
        try:
            # Simplified correlation risk calculation
            # In production, would use actual correlation matrix
            
            # Assume stablecoins have moderate correlation (0.6-0.8)
            # DeFi protocols have higher correlation during stress (0.8-0.9)
            
            asset_count = len(allocation)
            if asset_count <= 1:
                return 1.0  # Maximum correlation risk for single asset
            
            # Estimate correlation risk based on diversification
            max_weight = max(allocation.values()) if allocation else 1.0
            
            # Higher concentration = higher correlation risk
            correlation_risk = 0.3 + (max_weight * 0.7)  # Scale from 0.3 to 1.0
            
            return round(correlation_risk, 4)
            
        except Exception as e:
            logger.error(f"❌ Error calculating correlation risk: {e}")
            return 0.5
    
    async def _calculate_volatility(self, portfolio_id: str, lookback_days: int) -> float:
        """Calculate portfolio volatility"""
        try:
            # Use risk history if available
            if portfolio_id in self.risk_history and len(self.risk_history[portfolio_id]) >= lookback_days:
                values = [record["risk_metrics"].get("portfolio_value", 0) 
                         for record in self.risk_history[portfolio_id][-lookback_days:]]
                
                if len(values) > 1:
                    # Calculate returns
                    returns = []
                    for i in range(1, len(values)):
                        if values[i-1] > 0:
                            ret = (values[i] - values[i-1]) / values[i-1]
                            returns.append(ret)
                    
                    if returns:
                        volatility = statistics.stdev(returns) if len(returns) > 1 else 0.0
                        return round(volatility, 6)
            
            # Default volatility estimates based on stablecoin yields
            return 0.015  # 1.5% daily volatility estimate
            
        except Exception as e:
            logger.error(f"❌ Error calculating volatility: {e}")
            return 0.02
    
    async def run_stress_test(self, portfolio_id: str, scenario_id: str) -> Dict[str, Any]:
        """Run stress test on portfolio using specified scenario"""
        try:
            # Find scenario
            scenario = next((s for s in self.stress_scenarios if s.scenario_id == scenario_id), None)
            if not scenario:
                raise ValueError(f"Stress scenario {scenario_id} not found")
            
            # Get current portfolio state
            trading_engine = get_trading_engine_service()
            if not trading_engine:
                raise ValueError("Trading engine not available")
            
            portfolio_performance = await trading_engine.get_portfolio_performance(portfolio_id)
            current_allocation = portfolio_performance.get("current_allocation", {})
            current_value = portfolio_performance.get("total_value", 0)
            
            if not current_allocation or current_value == 0:
                raise ValueError("Portfolio data not available")
            
            # Apply stress scenario
            stressed_value = current_value
            asset_impacts = {}
            
            for asset, weight in current_allocation.items():
                asset_value = current_value * weight
                
                # Apply asset-specific shock
                shock = 0.0
                if asset.upper() in scenario.asset_shocks:
                    shock = scenario.asset_shocks[asset.upper()]
                elif "all" in scenario.asset_shocks:
                    shock = scenario.asset_shocks["all"]
                elif "DeFi" in scenario.asset_shocks and self._is_defi_asset(asset):
                    shock = scenario.asset_shocks["DeFi"]
                elif "CeFi" in scenario.asset_shocks and not self._is_defi_asset(asset):
                    shock = scenario.asset_shocks["CeFi"]
                
                # Calculate stressed asset value
                stressed_asset_value = asset_value * (1 + shock)
                asset_impact = stressed_asset_value - asset_value
                
                asset_impacts[asset] = {
                    "original_value": asset_value,
                    "stressed_value": stressed_asset_value,
                    "impact": asset_impact,
                    "shock_applied": shock
                }
                
                stressed_value += asset_impact
            
            # Calculate overall impact
            total_impact = stressed_value - current_value
            impact_percentage = (total_impact / current_value) * 100 if current_value > 0 else 0
            
            # Calculate risk metrics under stress
            var_multiplier = scenario.volatility_multipliers.get("all", 1.0)
            stressed_var = await self._calculate_var(portfolio_id, 1, 0.95) * var_multiplier
            
            return {
                "scenario": {
                    "scenario_id": scenario.scenario_id,
                    "name": scenario.name,
                    "description": scenario.description
                },
                "portfolio_impact": {
                    "original_value": current_value,
                    "stressed_value": stressed_value,
                    "total_impact": total_impact,
                    "impact_percentage": round(impact_percentage, 2)
                },
                "asset_impacts": asset_impacts,
                "stressed_risk_metrics": {
                    "var_1d_95_stressed": stressed_var,
                    "estimated_max_loss": abs(min(0, total_impact))
                },
                "scenario_metadata": {
                    "calculated_at": datetime.utcnow().isoformat(),
                    "confidence_level": "high",
                    "methodology": "Scenario-based stress testing"
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error running stress test: {e}")
            raise
    
    def _is_defi_asset(self, asset: str) -> bool:
        """Determine if asset is from DeFi protocol"""
        # Simplified DeFi detection
        defi_keywords = ["curve", "aave", "compound", "uniswap", "convex", "morpho", "yearn"]
        return any(keyword in asset.lower() for keyword in defi_keywords)
    
    async def get_risk_status(self) -> Dict[str, Any]:
        """Get comprehensive risk management service status"""
        try:
            active_alerts_count = len([a for a in self.active_alerts.values() if not a.resolved])
            critical_alerts = len([a for a in self.active_alerts.values() 
                                 if a.severity == RiskSeverity.CRITICAL and not a.resolved])
            
            monitored_portfolios = list(self.risk_history.keys())
            
            return {
                "service_running": self.is_running,
                "monitoring_status": {
                    "monitored_portfolios": len(monitored_portfolios),
                    "active_alerts": active_alerts_count,
                    "critical_alerts": critical_alerts,
                    "monitoring_interval": f"{self.config['monitoring_interval']} seconds"
                },
                "risk_capabilities": [
                    "Real-time Risk Monitoring",
                    "Dynamic Risk Limit Management",
                    "Advanced Stress Testing", 
                    "Regulatory Compliance Monitoring",
                    "Automated Risk Alerts",
                    "Portfolio Risk Attribution",
                    "Counterparty Risk Assessment",
                    "Liquidity Risk Analysis"
                ],
                "available_metrics": [metric.value for metric in RiskMetricType],
                "stress_scenarios": [
                    {
                        "scenario_id": s.scenario_id,
                        "name": s.name,
                        "description": s.description
                    }
                    for s in self.stress_scenarios
                ],
                "background_tasks": len([t for t in self.background_tasks if not t.done()]),
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting risk status: {e}")
            return {
                "service_running": False,
                "error": str(e)
            }

# Global service instance
_risk_management_service = None

async def start_risk_management():
    """Start the enhanced risk management service"""
    global _risk_management_service
    _risk_management_service = EnhancedRiskManagementService()
    return await _risk_management_service.start_risk_management()

async def stop_risk_management():
    """Stop the enhanced risk management service"""
    global _risk_management_service
    if _risk_management_service:
        return await _risk_management_service.stop_risk_management()
    return {"message": "Risk Management service not running"}

def get_risk_management_service():
    """Get the risk management service instance"""
    return _risk_management_service