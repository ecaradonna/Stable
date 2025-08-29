#!/usr/bin/env python3
"""
StableYield Backend API Test Suite - Steps 13 & 14 Integration Testing
Comprehensive testing for AI-Powered Portfolio Management (Step 13) and Enhanced Risk Management (Step 14)
"""

import asyncio
import aiohttp
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment - use production URL for testing
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://yield-index-dash.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class StableYieldStep13_14Tester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.test_portfolio_id = None
        self.test_signal_id = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    Details: {details}")
        if response_data and not success:
            print(f"    Response: {response_data}")
        
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    # ========================================
    # STEP 13: AI-POWERED PORTFOLIO MANAGEMENT TESTS
    # ========================================
    
    async def test_ai_portfolio_status(self):
        """Test GET /api/ai-portfolio/status endpoint"""
        try:
            async with self.session.get(f"{API_BASE}/ai-portfolio/status") as response:
                if response.status == 200:
                    data = await response.json()
                    required_fields = ['service_running', 'ai_portfolios', 'capabilities']
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if not missing_fields:
                        service_running = data.get('service_running', False)
                        ai_portfolios = data.get('ai_portfolios', 0)
                        capabilities = data.get('capabilities', [])
                        self.log_test("AI Portfolio Status", True, 
                                    f"Service: {service_running}, Portfolios: {ai_portfolios}, Capabilities: {len(capabilities)}")
                    else:
                        self.log_test("AI Portfolio Status", False, f"Missing fields: {missing_fields}")
                else:
                    self.log_test("AI Portfolio Status", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("AI Portfolio Status", False, f"Exception: {str(e)}")
    
    async def test_ai_portfolio_start(self):
        """Test POST /api/ai-portfolio/start endpoint"""
        try:
            async with self.session.post(f"{API_BASE}/ai-portfolio/start") as response:
                if response.status == 200:
                    data = await response.json()
                    if 'message' in data and 'ai_capabilities' in data:
                        capabilities = data.get('ai_capabilities', [])
                        strategies = data.get('optimization_strategies', [])
                        triggers = data.get('rebalancing_triggers', [])
                        self.log_test("AI Portfolio Start", True, 
                                    f"Started with {len(capabilities)} capabilities, {len(strategies)} strategies, {len(triggers)} triggers")
                    else:
                        self.log_test("AI Portfolio Start", False, f"Invalid response structure: {data}")
                else:
                    self.log_test("AI Portfolio Start", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("AI Portfolio Start", False, f"Exception: {str(e)}")
    
    async def test_ai_portfolio_create(self):
        """Test POST /api/ai-portfolio/portfolios endpoint (portfolio creation)"""
        try:
            portfolio_data = {
                "portfolio_id": f"ai_portfolio_{uuid.uuid4().hex[:8]}",
                "client_id": f"institutional_client_{uuid.uuid4().hex[:8]}",
                "optimization_strategy": "ai_enhanced",
                "risk_tolerance": 0.6,
                "performance_target": 0.08,
                "max_drawdown_limit": 0.15,
                "rebalancing_frequency": "weekly",
                "ai_confidence_threshold": 0.7,
                "use_sentiment_analysis": True,
                "use_market_regime_detection": True,
                "use_predictive_rebalancing": True
            }
            
            async with self.session.post(f"{API_BASE}/ai-portfolio/portfolios", json=portfolio_data) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'ai_portfolio' in data and 'ai_features' in data:
                        ai_portfolio = data['ai_portfolio']
                        ai_features = data['ai_features']
                        
                        # Store portfolio ID for later tests
                        self.test_portfolio_id = ai_portfolio.get('portfolio_id')
                        
                        self.log_test("AI Portfolio Create", True, 
                                    f"Created portfolio: {ai_portfolio.get('portfolio_id')}, Strategy: {ai_portfolio.get('optimization_strategy')}")
                    else:
                        self.log_test("AI Portfolio Create", False, f"Invalid response structure: {data}")
                else:
                    self.log_test("AI Portfolio Create", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("AI Portfolio Create", False, f"Exception: {str(e)}")
    
    async def test_ai_portfolio_rebalancing_signal(self):
        """Test POST /api/ai-portfolio/portfolios/{portfolio_id}/rebalancing-signal endpoint"""
        if not self.test_portfolio_id:
            self.log_test("AI Portfolio Rebalancing Signal", False, "No test portfolio ID available")
            return
            
        try:
            async with self.session.post(f"{API_BASE}/ai-portfolio/portfolios/{self.test_portfolio_id}/rebalancing-signal") as response:
                if response.status == 200:
                    data = await response.json()
                    if 'signal_generated' in data:
                        signal_generated = data.get('signal_generated', False)
                        if signal_generated and 'rebalancing_signal' in data:
                            signal = data['rebalancing_signal']
                            self.test_signal_id = signal.get('signal_id')
                            confidence = signal.get('confidence_score', 0)
                            self.log_test("AI Portfolio Rebalancing Signal", True, 
                                        f"Signal generated: {signal.get('signal_id')}, Confidence: {confidence:.2f}")
                        else:
                            reasons = data.get('reasons', [])
                            self.log_test("AI Portfolio Rebalancing Signal", True, 
                                        f"No signal generated - Reasons: {', '.join(reasons[:2])}")
                    else:
                        self.log_test("AI Portfolio Rebalancing Signal", False, f"Invalid response structure: {data}")
                else:
                    self.log_test("AI Portfolio Rebalancing Signal", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("AI Portfolio Rebalancing Signal", False, f"Exception: {str(e)}")
    
    async def test_ai_portfolio_rebalancing_execution(self):
        """Test POST /api/ai-portfolio/rebalancing-signals/{signal_id}/execute endpoint"""
        if not self.test_signal_id:
            # Create a test signal first
            await self.test_ai_portfolio_rebalancing_signal()
            
        if not self.test_signal_id:
            self.log_test("AI Portfolio Rebalancing Execution", False, "No test signal ID available")
            return
            
        try:
            async with self.session.post(f"{API_BASE}/ai-portfolio/rebalancing-signals/{self.test_signal_id}/execute") as response:
                if response.status == 200:
                    data = await response.json()
                    if 'execution_result' in data and 'trading_execution' in data:
                        execution = data['execution_result']
                        trading = data['trading_execution']
                        confidence = execution.get('confidence_score', 0)
                        expected_return = execution.get('expected_return', 0)
                        self.log_test("AI Portfolio Rebalancing Execution", True, 
                                    f"Executed signal: {execution.get('signal_id')}, Expected return: {expected_return:.2%}")
                    else:
                        self.log_test("AI Portfolio Rebalancing Execution", False, f"Invalid response structure: {data}")
                elif response.status == 404:
                    self.log_test("AI Portfolio Rebalancing Execution", False, "Signal not found or expired")
                else:
                    self.log_test("AI Portfolio Rebalancing Execution", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("AI Portfolio Rebalancing Execution", False, f"Exception: {str(e)}")
    
    async def test_ai_portfolio_market_sentiment(self):
        """Test GET /api/ai-portfolio/market-sentiment endpoint"""
        try:
            # Test with specific symbols
            symbols = "USDT,USDC,DAI"
            async with self.session.get(f"{API_BASE}/ai-portfolio/market-sentiment?symbols={symbols}") as response:
                if response.status == 200:
                    data = await response.json()
                    if 'market_sentiment' in data:
                        sentiment_data = data['market_sentiment']
                        individual_sentiments = sentiment_data.get('individual_sentiments', [])
                        market_overview = sentiment_data.get('market_overview', {})
                        avg_sentiment = market_overview.get('average_sentiment', 0)
                        self.log_test("AI Portfolio Market Sentiment", True, 
                                    f"Analyzed {len(individual_sentiments)} symbols, Avg sentiment: {avg_sentiment:.3f}")
                    else:
                        self.log_test("AI Portfolio Market Sentiment", False, f"Invalid response structure: {data}")
                else:
                    self.log_test("AI Portfolio Market Sentiment", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("AI Portfolio Market Sentiment", False, f"Exception: {str(e)}")
    
    async def test_ai_portfolio_market_regime(self):
        """Test GET /api/ai-portfolio/market-regime endpoint"""
        try:
            async with self.session.get(f"{API_BASE}/ai-portfolio/market-regime") as response:
                if response.status == 200:
                    data = await response.json()
                    if 'market_regime' in data:
                        regime_data = data['market_regime']
                        current_regime = regime_data.get('current_regime', 'unknown')
                        confidence = regime_data.get('confidence', 'unknown')
                        indicators = data.get('market_indicators', {})
                        volatility = indicators.get('yield_volatility', 0)
                        self.log_test("AI Portfolio Market Regime", True, 
                                    f"Regime: {current_regime}, Confidence: {confidence}, Volatility: {volatility:.3f}")
                    else:
                        self.log_test("AI Portfolio Market Regime", False, f"Invalid response structure: {data}")
                else:
                    self.log_test("AI Portfolio Market Regime", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("AI Portfolio Market Regime", False, f"Exception: {str(e)}")
    
    async def test_ai_portfolio_insights(self):
        """Test GET /api/ai-portfolio/ai-insights/{portfolio_id} endpoint"""
        if not self.test_portfolio_id:
            self.log_test("AI Portfolio Insights", False, "No test portfolio ID available")
            return
            
        try:
            async with self.session.get(f"{API_BASE}/ai-portfolio/ai-insights/{self.test_portfolio_id}") as response:
                if response.status == 200:
                    data = await response.json()
                    if 'ai_insights' in data:
                        insights_data = data['ai_insights']
                        insights = insights_data.get('insights', [])
                        portfolio_status = data.get('portfolio_ai_status', {})
                        market_context = data.get('market_context', {})
                        self.log_test("AI Portfolio Insights", True, 
                                    f"Generated {len(insights)} insights, Strategy: {portfolio_status.get('optimization_strategy', 'unknown')}")
                    else:
                        self.log_test("AI Portfolio Insights", False, f"Invalid response structure: {data}")
                else:
                    self.log_test("AI Portfolio Insights", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("AI Portfolio Insights", False, f"Exception: {str(e)}")
    
    async def test_ai_portfolio_integration_verification(self):
        """Test integration with other services"""
        try:
            async with self.session.get(f"{API_BASE}/ai-portfolio/summary") as response:
                if response.status == 200:
                    data = await response.json()
                    if 'integration_status' in data:
                        integration = data['integration_status']
                        connected_services = [service for service, status in integration.items() if status == "Connected"]
                        total_services = len(integration)
                        self.log_test("AI Portfolio Integration Verification", True, 
                                    f"Connected to {len(connected_services)}/{total_services} services: {', '.join(connected_services)}")
                    else:
                        self.log_test("AI Portfolio Integration Verification", False, f"No integration status in response")
                else:
                    self.log_test("AI Portfolio Integration Verification", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("AI Portfolio Integration Verification", False, f"Exception: {str(e)}")
    
    async def test_ai_portfolio_summary(self):
        """Test GET /api/ai-portfolio/summary endpoint"""
        try:
            async with self.session.get(f"{API_BASE}/ai-portfolio/summary") as response:
                if response.status == 200:
                    data = await response.json()
                    if 'service_status' in data and 'ai_portfolio_management' in data:
                        service_status = data.get('service_status', 'unknown')
                        portfolio_mgmt = data.get('ai_portfolio_management', {})
                        optimization_perf = data.get('optimization_performance', {})
                        api_endpoints = data.get('api_endpoints', {})
                        
                        total_endpoints = sum(len(endpoints) for endpoints in api_endpoints.values())
                        self.log_test("AI Portfolio Summary", True, 
                                    f"Service: {service_status}, Portfolios: {portfolio_mgmt.get('ai_portfolios', 0)}, Endpoints: {total_endpoints}")
                    else:
                        self.log_test("AI Portfolio Summary", False, f"Invalid response structure: {data}")
                else:
                    self.log_test("AI Portfolio Summary", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("AI Portfolio Summary", False, f"Exception: {str(e)}")
    
    # ========================================
    # STEP 14: ENHANCED RISK MANAGEMENT TESTS
    # ========================================
    
    async def test_risk_management_status(self):
        """Test GET /api/risk-management/status endpoint"""
        try:
            async with self.session.get(f"{API_BASE}/risk-management/status") as response:
                if response.status == 200:
                    data = await response.json()
                    required_fields = ['service_running', 'capabilities', 'monitored_portfolios']
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if not missing_fields:
                        service_running = data.get('service_running', False)
                        capabilities = data.get('capabilities', [])
                        monitored = data.get('monitored_portfolios', 0)
                        features = data.get('risk_management_features', [])
                        self.log_test("Risk Management Status", True, 
                                    f"Service: {service_running}, Capabilities: {len(capabilities)}, Monitored: {monitored}, Features: {len(features)}")
                    else:
                        self.log_test("Risk Management Status", False, f"Missing fields: {missing_fields}")
                else:
                    self.log_test("Risk Management Status", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Risk Management Status", False, f"Exception: {str(e)}")
    
    async def test_risk_management_start(self):
        """Test POST /api/risk-management/start endpoint"""
        try:
            async with self.session.post(f"{API_BASE}/risk-management/start") as response:
                if response.status == 200:
                    data = await response.json()
                    if 'message' in data and 'advanced_features' in data:
                        features = data.get('advanced_features', [])
                        integration = data.get('integration_status', {})
                        connected_services = [service for service, status in integration.items() if "Connected" in status]
                        self.log_test("Risk Management Start", True, 
                                    f"Started with {len(features)} features, Connected to {len(connected_services)} services")
                    else:
                        self.log_test("Risk Management Start", False, f"Invalid response structure: {data}")
                else:
                    self.log_test("Risk Management Start", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Risk Management Start", False, f"Exception: {str(e)}")
    
    async def test_risk_management_metrics(self):
        """Test GET /api/risk-management/metrics/{portfolio_id} endpoint"""
        # Use test portfolio ID if available, otherwise create a test ID
        portfolio_id = self.test_portfolio_id or f"test_portfolio_{uuid.uuid4().hex[:8]}"
        
        try:
            async with self.session.get(f"{API_BASE}/risk-management/metrics/{portfolio_id}") as response:
                if response.status == 200:
                    data = await response.json()
                    if 'risk_metrics' in data and 'risk_assessment' in data:
                        risk_metrics = data['risk_metrics']
                        risk_assessment = data['risk_assessment']
                        
                        # Check VaR calculations
                        var_data = risk_metrics.get('value_at_risk', {})
                        var_95 = var_data.get('var_1d_95', 0)
                        var_99 = var_data.get('var_1d_99', 0)
                        
                        # Check concentration analysis
                        concentration = risk_metrics.get('concentration_analysis', {})
                        max_concentration = concentration.get('max_concentration', 0)
                        
                        # Check liquidity metrics
                        liquidity = risk_metrics.get('liquidity_metrics', {})
                        liquidity_score = liquidity.get('liquidity_risk_score', 0)
                        
                        overall_risk = risk_assessment.get('overall_risk_level', 'unknown')
                        
                        self.log_test("Risk Management Metrics", True, 
                                    f"VaR 95%: {var_95:.4f}, VaR 99%: {var_99:.4f}, Concentration: {max_concentration:.2%}, Risk Level: {overall_risk}")
                    else:
                        self.log_test("Risk Management Metrics", False, f"Invalid response structure: {data}")
                elif response.status == 404:
                    self.log_test("Risk Management Metrics", False, f"Portfolio {portfolio_id} not found")
                else:
                    self.log_test("Risk Management Metrics", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Risk Management Metrics", False, f"Exception: {str(e)}")
    
    async def test_risk_management_stress_scenarios(self):
        """Test GET /api/risk-management/stress-scenarios endpoint"""
        try:
            async with self.session.get(f"{API_BASE}/risk-management/stress-scenarios") as response:
                if response.status == 200:
                    data = await response.json()
                    if 'stress_scenarios' in data:
                        scenarios = data.get('stress_scenarios', [])
                        total_scenarios = data.get('total_scenarios', 0)
                        methodology = data.get('methodology', {})
                        
                        # Check for expected scenarios
                        scenario_names = [s.get('name', '') for s in scenarios]
                        expected_scenarios = ['peg_break', 'defi_crisis', 'liquidity_crisis', 'regulatory_shock', 'black_swan']
                        found_scenarios = [name for name in expected_scenarios if any(name in s_name.lower() for s_name in scenario_names)]
                        
                        self.log_test("Risk Management Stress Scenarios", True, 
                                    f"Found {total_scenarios} scenarios including: {', '.join(found_scenarios[:3])}")
                    else:
                        self.log_test("Risk Management Stress Scenarios", False, f"Invalid response structure: {data}")
                else:
                    self.log_test("Risk Management Stress Scenarios", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Risk Management Stress Scenarios", False, f"Exception: {str(e)}")
    
    async def test_risk_management_stress_test(self):
        """Test POST /api/risk-management/stress-test/{portfolio_id} endpoint"""
        # Use test portfolio ID if available, otherwise create a test ID
        portfolio_id = self.test_portfolio_id or f"test_portfolio_{uuid.uuid4().hex[:8]}"
        
        try:
            # Test with peg_break scenario
            scenario_data = {
                "scenario_id": "peg_break"
            }
            
            async with self.session.post(f"{API_BASE}/risk-management/stress-test/{portfolio_id}", json=scenario_data) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'stress_test_results' in data and 'impact_analysis' in data:
                        stress_results = data['stress_test_results']
                        impact_analysis = data['impact_analysis']
                        
                        portfolio_impact = stress_results.get('portfolio_impact', {})
                        impact_pct = portfolio_impact.get('impact_percentage', 0)
                        severity = impact_analysis.get('severity', 'unknown')
                        
                        comparative = data.get('comparative_analysis', {})
                        resilience_score = comparative.get('resilience_score', 0)
                        
                        self.log_test("Risk Management Stress Test", True, 
                                    f"Peg break impact: {impact_pct:.1f}%, Severity: {severity}, Resilience: {resilience_score:.1f}")
                    else:
                        self.log_test("Risk Management Stress Test", False, f"Invalid response structure: {data}")
                elif response.status == 404:
                    self.log_test("Risk Management Stress Test", False, f"Portfolio or scenario not found")
                else:
                    self.log_test("Risk Management Stress Test", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Risk Management Stress Test", False, f"Exception: {str(e)}")
    
    async def test_risk_management_compliance(self):
        """Test GET /api/risk-management/compliance/{portfolio_id} endpoint"""
        # Use test portfolio ID if available, otherwise create a test ID
        portfolio_id = self.test_portfolio_id or f"test_portfolio_{uuid.uuid4().hex[:8]}"
        
        try:
            async with self.session.get(f"{API_BASE}/risk-management/compliance/{portfolio_id}") as response:
                if response.status == 200:
                    data = await response.json()
                    if 'compliance_overview' in data and 'compliance_details' in data:
                        overview = data['compliance_overview']
                        details = data['compliance_details']
                        regulatory = data.get('regulatory_framework', {})
                        
                        overall_compliant = overview.get('overall_compliant', False)
                        compliance_score = overview.get('compliance_score', 0)
                        total_checks = overview.get('total_checks', 0)
                        passed_checks = overview.get('passed_checks', 0)
                        
                        regulations = regulatory.get('applicable_regulations', [])
                        
                        self.log_test("Risk Management Compliance", True, 
                                    f"Compliant: {overall_compliant}, Score: {compliance_score}%, Checks: {passed_checks}/{total_checks}, Regulations: {len(regulations)}")
                    else:
                        self.log_test("Risk Management Compliance", False, f"Invalid response structure: {data}")
                elif response.status == 404:
                    self.log_test("Risk Management Compliance", False, f"Portfolio data not available")
                else:
                    self.log_test("Risk Management Compliance", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Risk Management Compliance", False, f"Exception: {str(e)}")
    
    async def test_risk_management_integration_verification(self):
        """Test integration with AI Portfolio and other services"""
        try:
            async with self.session.get(f"{API_BASE}/risk-management/summary") as response:
                if response.status == 200:
                    data = await response.json()
                    if 'integration_status' in data:
                        integration = data['integration_status']
                        connected_services = [service for service, status in integration.items() if status == "Connected"]
                        total_services = len(integration)
                        
                        # Check for specific integrations
                        ai_portfolio_connected = integration.get('ai_portfolio_service') == 'Connected'
                        trading_engine_connected = integration.get('trading_engine') == 'Connected'
                        ml_insights_connected = integration.get('ml_insights') == 'Connected'
                        
                        self.log_test("Risk Management Integration Verification", True, 
                                    f"Connected: {len(connected_services)}/{total_services}, AI Portfolio: {ai_portfolio_connected}, Trading: {trading_engine_connected}")
                    else:
                        self.log_test("Risk Management Integration Verification", False, f"No integration status in response")
                else:
                    self.log_test("Risk Management Integration Verification", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Risk Management Integration Verification", False, f"Exception: {str(e)}")
    
    async def test_risk_management_summary(self):
        """Test GET /api/risk-management/summary endpoint"""
        try:
            async with self.session.get(f"{API_BASE}/risk-management/summary") as response:
                if response.status == 200:
                    data = await response.json()
                    if 'service_status' in data and 'risk_management_capabilities' in data:
                        service_status = data.get('service_status', {})
                        capabilities = data.get('risk_management_capabilities', {})
                        api_endpoints = data.get('api_endpoints', {})
                        
                        service_running = service_status.get('service_running', False)
                        
                        # Count capabilities
                        real_time = capabilities.get('real_time_monitoring', {})
                        advanced_analytics = capabilities.get('advanced_analytics', {})
                        compliance_mgmt = capabilities.get('compliance_management', {})
                        
                        monitored_portfolios = real_time.get('monitored_portfolios', 0)
                        available_scenarios = advanced_analytics.get('available_scenarios', 0)
                        regulatory_frameworks = compliance_mgmt.get('regulatory_frameworks', 0)
                        
                        total_endpoints = sum(len(endpoints) for endpoints in api_endpoints.values())
                        
                        self.log_test("Risk Management Summary", True, 
                                    f"Service: {service_running}, Monitored: {monitored_portfolios}, Scenarios: {available_scenarios}, Endpoints: {total_endpoints}")
                    else:
                        self.log_test("Risk Management Summary", False, f"Invalid response structure: {data}")
                else:
                    self.log_test("Risk Management Summary", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Risk Management Summary", False, f"Exception: {str(e)}")
    
    # ========================================
    # INTEGRATION TESTS (STEP 13 + STEP 14)
    # ========================================
    
    async def test_step13_step14_integration(self):
        """Test integration between AI Portfolio Management and Risk Management"""
        if not self.test_portfolio_id:
            self.log_test("Step 13-14 Integration", False, "No test portfolio ID available for integration test")
            return
            
        try:
            # Test 1: Get AI portfolio insights
            async with self.session.get(f"{API_BASE}/ai-portfolio/ai-insights/{self.test_portfolio_id}") as ai_response:
                ai_success = ai_response.status == 200
                
            # Test 2: Get risk metrics for same portfolio
            async with self.session.get(f"{API_BASE}/risk-management/metrics/{self.test_portfolio_id}") as risk_response:
                risk_success = risk_response.status == 200
                
            # Test 3: Check if both services are aware of each other
            async with self.session.get(f"{API_BASE}/ai-portfolio/summary") as ai_summary:
                ai_summary_success = ai_summary.status == 200
                
            async with self.session.get(f"{API_BASE}/risk-management/summary") as risk_summary:
                risk_summary_success = risk_summary.status == 200
                
            integration_success = ai_success and risk_success and ai_summary_success and risk_summary_success
            
            if integration_success:
                self.log_test("Step 13-14 Integration", True, 
                            f"Both services operational and integrated for portfolio {self.test_portfolio_id}")
            else:
                failed_services = []
                if not ai_success: failed_services.append("AI Portfolio")
                if not risk_success: failed_services.append("Risk Management")
                self.log_test("Step 13-14 Integration", False, 
                            f"Integration issues with: {', '.join(failed_services)}")
                
        except Exception as e:
            self.log_test("Step 13-14 Integration", False, f"Exception: {str(e)}")
    
    async def test_production_ready_rebalancing(self):
        """Test production-ready rebalancing with real-world constraints"""
        if not self.test_portfolio_id:
            self.log_test("Production Ready Rebalancing", False, "No test portfolio ID available")
            return
            
        try:
            # Generate rebalancing signal
            async with self.session.post(f"{API_BASE}/ai-portfolio/portfolios/{self.test_portfolio_id}/rebalancing-signal") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('signal_generated', False) and 'rebalancing_signal' in data:
                        signal = data['rebalancing_signal']
                        signal_id = signal.get('signal_id')
                        
                        # Test execution with production constraints
                        async with self.session.post(f"{API_BASE}/ai-portfolio/rebalancing-signals/{signal_id}/execute") as exec_response:
                            if exec_response.status == 200:
                                exec_data = await exec_response.json()
                                if 'execution_result' in exec_data and 'trading_execution' in exec_data:
                                    execution = exec_data['execution_result']
                                    trading = exec_data['trading_execution']
                                    
                                    # Check for production constraints
                                    has_fees = 'fee_bps' in str(trading) or 'fees' in str(trading)
                                    has_slippage = 'slippage' in str(trading)
                                    has_constraints = 'constraints' in str(trading) or 'lot_size' in str(trading)
                                    
                                    production_ready = has_fees or has_slippage or has_constraints
                                    
                                    self.log_test("Production Ready Rebalancing", production_ready, 
                                                f"Execution includes production constraints: Fees: {has_fees}, Slippage: {has_slippage}")
                                else:
                                    self.log_test("Production Ready Rebalancing", False, "Invalid execution response structure")
                            else:
                                self.log_test("Production Ready Rebalancing", False, f"Execution failed: HTTP {exec_response.status}")
                    else:
                        self.log_test("Production Ready Rebalancing", True, "No rebalancing signal generated (conditions not met)")
                else:
                    self.log_test("Production Ready Rebalancing", False, f"Signal generation failed: HTTP {response.status}")
        except Exception as e:
            self.log_test("Production Ready Rebalancing", False, f"Exception: {str(e)}")
    
    # ========================================
    # TEST EXECUTION
    # ========================================
    
    async def run_all_tests(self):
        """Run all Step 13 and Step 14 tests"""
        print("🚀 Starting Comprehensive Step 13 & 14 Integration Testing...")
        print("=" * 80)
        
        # Step 13: AI-Powered Portfolio Management Tests
        print("\n📊 STEP 13: AI-POWERED PORTFOLIO MANAGEMENT TESTS")
        print("-" * 60)
        await self.test_ai_portfolio_status()
        await self.test_ai_portfolio_start()
        await self.test_ai_portfolio_create()
        await self.test_ai_portfolio_rebalancing_signal()
        await self.test_ai_portfolio_rebalancing_execution()
        await self.test_ai_portfolio_market_sentiment()
        await self.test_ai_portfolio_market_regime()
        await self.test_ai_portfolio_insights()
        await self.test_ai_portfolio_integration_verification()
        await self.test_ai_portfolio_summary()
        
        # Step 14: Enhanced Risk Management Tests
        print("\n🛡️ STEP 14: ENHANCED RISK MANAGEMENT TESTS")
        print("-" * 60)
        await self.test_risk_management_status()
        await self.test_risk_management_start()
        await self.test_risk_management_metrics()
        await self.test_risk_management_stress_scenarios()
        await self.test_risk_management_stress_test()
        await self.test_risk_management_compliance()
        await self.test_risk_management_integration_verification()
        await self.test_risk_management_summary()
        
        # Integration Tests
        print("\n🔗 STEP 13 + 14 INTEGRATION TESTS")
        print("-" * 60)
        await self.test_step13_step14_integration()
        await self.test_production_ready_rebalancing()
        
        # Summary
        print("\n" + "=" * 80)
        print("📋 TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t['success']])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for test in self.test_results:
                if not test['success']:
                    print(f"  - {test['test']}: {test['details']}")
        
        print(f"\n✅ COMPREHENSIVE STEP 13 & 14 TESTING COMPLETE")
        return success_rate >= 80  # Consider 80%+ success rate as passing

async def main():
    """Main test execution function"""
    async with StableYieldStep13_14Tester() as tester:
        success = await tester.run_all_tests()
        return success

if __name__ == "__main__":
    result = asyncio.run(main())
    exit(0 if result else 1)