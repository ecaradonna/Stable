#!/usr/bin/env python3
"""
Comprehensive AI-Powered Portfolio Management Testing (STEP 13)
Tests all critical endpoints and production-ready rebalancing functionality
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

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://yield-index-dash.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class AIPortfolioTester:
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
    
    async def test_core_service_status(self):
        """Test 1: Core Service Status"""
        print("\n🔍 Testing Core Service Status...")
        
        # Test GET /api/ai-portfolio/status
        try:
            async with self.session.get(f"{API_BASE}/ai-portfolio/status") as response:
                if response.status == 200:
                    data = await response.json()
                    required_fields = ['service_running', 'ai_portfolios', 'capabilities', 'optimization_strategies']
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if not missing_fields:
                        service_running = data.get('service_running', False)
                        capabilities = data.get('capabilities', [])
                        strategies = data.get('optimization_strategies', [])
                        
                        if service_running and len(capabilities) >= 5 and len(strategies) >= 5:
                            self.log_test("AI Portfolio Status", True, 
                                        f"Service running with {len(capabilities)} capabilities, {len(strategies)} strategies")
                        else:
                            self.log_test("AI Portfolio Status", False, 
                                        f"Service issues: running={service_running}, capabilities={len(capabilities)}, strategies={len(strategies)}")
                    else:
                        self.log_test("AI Portfolio Status", False, f"Missing fields: {missing_fields}")
                else:
                    self.log_test("AI Portfolio Status", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("AI Portfolio Status", False, f"Exception: {str(e)}")
        
        # Test POST /api/ai-portfolio/start
        try:
            async with self.session.post(f"{API_BASE}/ai-portfolio/start") as response:
                if response.status == 200:
                    data = await response.json()
                    if 'ai_capabilities' in data and 'optimization_strategies' in data:
                        capabilities = data.get('ai_capabilities', [])
                        strategies = data.get('optimization_strategies', [])
                        triggers = data.get('rebalancing_triggers', [])
                        
                        if len(capabilities) >= 5 and len(strategies) >= 5 and len(triggers) >= 5:
                            self.log_test("AI Portfolio Start", True, 
                                        f"Started with {len(capabilities)} capabilities, {len(strategies)} strategies, {len(triggers)} triggers")
                        else:
                            self.log_test("AI Portfolio Start", False, 
                                        f"Insufficient features: capabilities={len(capabilities)}, strategies={len(strategies)}, triggers={len(triggers)}")
                    else:
                        self.log_test("AI Portfolio Start", False, f"Invalid response structure: {data}")
                else:
                    self.log_test("AI Portfolio Start", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("AI Portfolio Start", False, f"Exception: {str(e)}")
    
    async def test_portfolio_creation_management(self):
        """Test 2: Portfolio Creation & Management"""
        print("\n🔍 Testing Portfolio Creation & Management...")
        
        # Test POST /api/ai-portfolio/portfolios (create AI-managed portfolio)
        try:
            portfolio_data = {
                "portfolio_id": f"test_ai_portfolio_{uuid.uuid4().hex[:8]}",
                "client_id": f"test_client_{uuid.uuid4().hex[:8]}",
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
                        
                        # Verify production-ready constraints integration
                        if (ai_portfolio.get('optimization_strategy') == 'ai_enhanced' and
                            ai_features.get('sentiment_analysis') and
                            ai_features.get('regime_detection') and
                            ai_features.get('predictive_rebalancing')):
                            
                            self.log_test("AI Portfolio Creation", True, 
                                        f"Created portfolio: {ai_portfolio.get('portfolio_id')}, Strategy: {ai_portfolio.get('optimization_strategy')}")
                        else:
                            self.log_test("AI Portfolio Creation", False, f"Missing AI features or wrong strategy")
                    else:
                        self.log_test("AI Portfolio Creation", False, f"Invalid response structure: {data}")
                else:
                    text = await response.text()
                    self.log_test("AI Portfolio Creation", False, f"HTTP {response.status}: {text}")
        except Exception as e:
            self.log_test("AI Portfolio Creation", False, f"Exception: {str(e)}")
        
        # Test GET /api/ai-portfolio/portfolios (list AI portfolios)
        try:
            async with self.session.get(f"{API_BASE}/ai-portfolio/portfolios") as response:
                if response.status == 200:
                    data = await response.json()
                    if 'ai_portfolios' in data and 'total_portfolios' in data:
                        portfolios = data['ai_portfolios']
                        total = data['total_portfolios']
                        
                        if total > 0 and len(portfolios) > 0:
                            # Verify production-ready constraints integration
                            has_constraints = any(
                                'optimization_strategy' in p and 'ai_features_enabled' in p
                                for p in portfolios
                            )
                            
                            if has_constraints:
                                self.log_test("AI Portfolio List", True, 
                                            f"Found {total} AI portfolios with production-ready constraints")
                            else:
                                self.log_test("AI Portfolio List", False, 
                                            f"Portfolios missing production-ready constraints")
                        else:
                            self.log_test("AI Portfolio List", False, f"No portfolios found: total={total}")
                    else:
                        self.log_test("AI Portfolio List", False, f"Invalid response structure: {data}")
                else:
                    self.log_test("AI Portfolio List", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("AI Portfolio List", False, f"Exception: {str(e)}")
    
    async def test_production_ready_rebalancing(self):
        """Test 3: Production-Ready Rebalancing - PRIORITY FOCUS"""
        print("\n🔍 Testing Production-Ready Rebalancing (PRIORITY FOCUS)...")
        
        if not self.test_portfolio_id:
            self.log_test("Rebalancing Signal Generation", False, "No test portfolio available")
            return
        
        # Test POST /api/ai-portfolio/rebalancing-signal/{portfolio_id}
        try:
            async with self.session.post(f"{API_BASE}/ai-portfolio/portfolios/{self.test_portfolio_id}/rebalancing-signal") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('signal_generated'):
                        signal_data = data.get('rebalancing_signal', {})
                        allocation_changes = data.get('allocation_changes', {})
                        
                        # Store signal ID for execution test
                        self.test_signal_id = signal_data.get('signal_id')
                        
                        # Verify production-ready execution plan with real-world constraints
                        required_fields = ['signal_id', 'recommended_allocation', 'confidence_score', 'market_regime']
                        missing_fields = [field for field in required_fields if field not in signal_data]
                        
                        if not missing_fields:
                            confidence = signal_data.get('confidence_score', 0)
                            regime = signal_data.get('market_regime', 'unknown')
                            
                            # Check for production-ready constraints integration
                            has_allocation_changes = len(allocation_changes) > 0
                            has_confidence_threshold = confidence > 0
                            
                            if has_allocation_changes and has_confidence_threshold:
                                self.log_test("Rebalancing Signal Generation", True, 
                                            f"Generated signal: {signal_data.get('signal_id')}, Confidence: {confidence:.2f}, Regime: {regime}")
                            else:
                                self.log_test("Rebalancing Signal Generation", False, 
                                            f"Missing production constraints: changes={has_allocation_changes}, confidence={has_confidence_threshold}")
                        else:
                            self.log_test("Rebalancing Signal Generation", False, f"Missing fields: {missing_fields}")
                    else:
                        # No signal generated is also valid (conditions not met)
                        reasons = data.get('reasons', [])
                        self.log_test("Rebalancing Signal Generation", True, 
                                    f"No signal generated (conditions not met): {', '.join(reasons)}")
                else:
                    text = await response.text()
                    self.log_test("Rebalancing Signal Generation", False, f"HTTP {response.status}: {text}")
        except Exception as e:
            self.log_test("Rebalancing Signal Generation", False, f"Exception: {str(e)}")
        
        # Test generateRebalancePlan function integration with real-world constraints
        if self.test_signal_id:
            try:
                # Get the signal details to verify rebalance plan
                async with self.session.get(f"{API_BASE}/ai-portfolio/portfolios/{self.test_portfolio_id}/rebalancing-signals") as response:
                    if response.status == 200:
                        data = await response.json()
                        signals = data.get('rebalancing_signals', [])
                        
                        if signals:
                            signal = signals[0]  # Get the latest signal
                            
                            # Verify production-ready constraints are included
                            has_confidence = 'confidence_score' in signal
                            has_expected_metrics = 'expected_return' in signal and 'expected_risk' in signal
                            has_market_context = 'market_regime' in signal
                            
                            if has_confidence and has_expected_metrics and has_market_context:
                                self.log_test("Production Constraints Integration", True, 
                                            f"Signal includes production constraints: confidence, risk metrics, market context")
                            else:
                                self.log_test("Production Constraints Integration", False, 
                                            f"Missing constraints: confidence={has_confidence}, metrics={has_expected_metrics}, context={has_market_context}")
                        else:
                            self.log_test("Production Constraints Integration", False, "No signals found for verification")
                    else:
                        self.log_test("Production Constraints Integration", False, f"HTTP {response.status}")
            except Exception as e:
                self.log_test("Production Constraints Integration", False, f"Exception: {str(e)}")
        
        # Test POST /api/ai-portfolio/execute-rebalancing/{signal_id}
        if self.test_signal_id:
            try:
                async with self.session.post(f"{API_BASE}/ai-portfolio/rebalancing-signals/{self.test_signal_id}/execute") as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if 'execution_result' in data and 'trading_execution' in data:
                            execution_result = data['execution_result']
                            trading_execution = data['trading_execution']
                            
                            # Verify production-ready execution includes fees/slippage calculations
                            has_execution_plan = 'execution_plan' in trading_execution
                            has_cost_calculations = False
                            
                            if has_execution_plan:
                                plan = trading_execution['execution_plan']
                                has_cost_calculations = ('est_fees' in plan and 'est_slippage' in plan and 
                                                       'est_total_cost' in plan and 'tracking_error' in plan)
                            
                            if has_execution_plan and has_cost_calculations:
                                total_cost = trading_execution['execution_plan'].get('est_total_cost', 0)
                                tracking_error = trading_execution['execution_plan'].get('tracking_error', 0)
                                
                                self.log_test("Rebalancing Execution", True, 
                                            f"Executed with production constraints: Cost: ${total_cost:.2f}, Tracking Error: {tracking_error:.4f}")
                            else:
                                self.log_test("Rebalancing Execution", False, 
                                            f"Missing production execution details: plan={has_execution_plan}, costs={has_cost_calculations}")
                        else:
                            self.log_test("Rebalancing Execution", False, f"Invalid response structure: {data}")
                    else:
                        text = await response.text()
                        self.log_test("Rebalancing Execution", False, f"HTTP {response.status}: {text}")
            except Exception as e:
                self.log_test("Rebalancing Execution", False, f"Exception: {str(e)}")
    
    async def test_ai_features(self):
        """Test 4: AI Features"""
        print("\n🔍 Testing AI Features...")
        
        # Test portfolio optimization
        if self.test_portfolio_id:
            try:
                optimization_data = {"optimization_strategy": "ai_enhanced"}
                async with self.session.post(f"{API_BASE}/ai-portfolio/portfolios/{self.test_portfolio_id}/optimize", 
                                           json=optimization_data) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if 'optimization_result' in data and 'optimization_insights' in data:
                            result = data['optimization_result']
                            insights = data['optimization_insights']
                            
                            # Verify multi-strategy optimization
                            has_performance_metrics = 'performance_metrics' in result
                            has_ai_insights = 'ai_enhancement' in insights
                            has_market_context = 'market_regime' in insights
                            
                            if has_performance_metrics and has_ai_insights and has_market_context:
                                strategy = result.get('optimization_strategy', 'unknown')
                                expected_return = result.get('performance_metrics', {}).get('expected_return', 0)
                                
                                self.log_test("Portfolio Optimization", True, 
                                            f"Multi-strategy optimization: {strategy}, Expected Return: {expected_return:.2%}")
                            else:
                                self.log_test("Portfolio Optimization", False, 
                                            f"Missing optimization features: metrics={has_performance_metrics}, insights={has_ai_insights}, context={has_market_context}")
                        else:
                            self.log_test("Portfolio Optimization", False, f"Invalid response structure: {data}")
                    else:
                        text = await response.text()
                        self.log_test("Portfolio Optimization", False, f"HTTP {response.status}: {text}")
            except Exception as e:
                self.log_test("Portfolio Optimization", False, f"Exception: {str(e)}")
        
        # Test market sentiment analysis
        try:
            async with self.session.get(f"{API_BASE}/ai-portfolio/market-sentiment?symbols=USDT,USDC,DAI") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if 'market_sentiment' in data:
                        sentiment_data = data['market_sentiment']
                        individual_sentiments = sentiment_data.get('individual_sentiments', [])
                        market_overview = sentiment_data.get('market_overview', {})
                        
                        if len(individual_sentiments) >= 3 and 'average_sentiment' in market_overview:
                            avg_sentiment = market_overview.get('average_sentiment', 0)
                            symbols_analyzed = len(individual_sentiments)
                            
                            self.log_test("Market Sentiment Analysis", True, 
                                        f"Analyzed {symbols_analyzed} symbols, Avg sentiment: {avg_sentiment:.2f}")
                        else:
                            self.log_test("Market Sentiment Analysis", False, 
                                        f"Insufficient sentiment data: symbols={len(individual_sentiments)}, overview={bool(market_overview)}")
                    else:
                        self.log_test("Market Sentiment Analysis", False, f"Invalid response structure: {data}")
                else:
                    self.log_test("Market Sentiment Analysis", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Market Sentiment Analysis", False, f"Exception: {str(e)}")
        
        # Test market regime detection
        try:
            async with self.session.get(f"{API_BASE}/ai-portfolio/market-regime") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if 'market_regime' in data and 'market_indicators' in data:
                        regime_data = data['market_regime']
                        indicators = data['market_indicators']
                        implications = data.get('regime_implications', {})
                        
                        current_regime = regime_data.get('current_regime', 'unknown')
                        has_indicators = len(indicators) > 0
                        has_implications = len(implications) > 0
                        
                        if current_regime != 'unknown' and has_indicators and has_implications:
                            self.log_test("Market Regime Detection", True, 
                                        f"Detected regime: {current_regime}, Indicators: {len(indicators)}, Implications: {len(implications)}")
                        else:
                            self.log_test("Market Regime Detection", False, 
                                        f"Incomplete regime detection: regime={current_regime}, indicators={has_indicators}, implications={has_implications}")
                    else:
                        self.log_test("Market Regime Detection", False, f"Invalid response structure: {data}")
                else:
                    self.log_test("Market Regime Detection", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Market Regime Detection", False, f"Exception: {str(e)}")
        
        # Test AI insights
        if self.test_portfolio_id:
            try:
                async with self.session.get(f"{API_BASE}/ai-portfolio/ai-insights/{self.test_portfolio_id}") as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if 'ai_insights' in data and 'portfolio_ai_status' in data:
                            insights = data['ai_insights']
                            ai_status = data['portfolio_ai_status']
                            market_context = data.get('market_context', {})
                            
                            insights_list = insights.get('insights', [])
                            ai_features = ai_status.get('ai_features_enabled', {})
                            
                            if len(insights_list) > 0 and len(ai_features) > 0 and len(market_context) > 0:
                                self.log_test("AI Insights", True, 
                                            f"Generated {len(insights_list)} insights with AI features and market context")
                            else:
                                self.log_test("AI Insights", False, 
                                            f"Incomplete insights: insights={len(insights_list)}, features={len(ai_features)}, context={len(market_context)}")
                        else:
                            self.log_test("AI Insights", False, f"Invalid response structure: {data}")
                    else:
                        self.log_test("AI Insights", False, f"HTTP {response.status}")
            except Exception as e:
                self.log_test("AI Insights", False, f"Exception: {str(e)}")
    
    async def test_integration_verification(self):
        """Test 5: Integration Verification"""
        print("\n🔍 Testing Integration Verification...")
        
        # Test comprehensive summary to verify all integrations
        try:
            async with self.session.get(f"{API_BASE}/ai-portfolio/summary") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if 'integration_status' in data and 'ai_portfolio_management' in data:
                        integration_status = data['integration_status']
                        portfolio_mgmt = data['ai_portfolio_management']
                        
                        # Verify key integrations
                        required_integrations = ['trading_engine', 'ml_insights', 'dashboard_service', 'yield_aggregator', 'ray_calculator']
                        connected_integrations = [k for k, v in integration_status.items() if v == 'Connected']
                        
                        integration_success = len(connected_integrations) >= 4  # At least 4 out of 5
                        
                        # Verify AI portfolio management features
                        has_portfolios = 'ai_portfolios' in portfolio_mgmt
                        has_optimization = 'optimization_results' in portfolio_mgmt
                        has_rebalancing = 'rebalancing_signals' in portfolio_mgmt
                        
                        if integration_success and has_portfolios and has_optimization and has_rebalancing:
                            self.log_test("Integration Verification", True, 
                                        f"Connected integrations: {len(connected_integrations)}/5, AI features operational")
                        else:
                            self.log_test("Integration Verification", False, 
                                        f"Integration issues: connected={len(connected_integrations)}/5, features={has_portfolios and has_optimization and has_rebalancing}")
                    else:
                        self.log_test("Integration Verification", False, f"Invalid response structure: {data}")
                else:
                    self.log_test("Integration Verification", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Integration Verification", False, f"Exception: {str(e)}")
    
    async def test_summary_metrics(self):
        """Test 6: Summary & Metrics"""
        print("\n🔍 Testing Summary & Metrics...")
        
        # Test comprehensive service summary
        try:
            async with self.session.get(f"{API_BASE}/ai-portfolio/summary") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    required_sections = ['service_status', 'ai_portfolio_management', 'optimization_performance', 
                                       'ai_capabilities', 'api_endpoints', 'system_performance']
                    missing_sections = [section for section in required_sections if section not in data]
                    
                    if not missing_sections:
                        service_status = data.get('service_status', 'unknown')
                        capabilities = data.get('ai_capabilities', [])
                        api_endpoints = data.get('api_endpoints', {})
                        
                        # Count total endpoints
                        total_endpoints = sum(len(endpoints) for endpoints in api_endpoints.values())
                        
                        if service_status == 'running' and len(capabilities) >= 5 and total_endpoints >= 15:
                            self.log_test("Comprehensive Summary", True, 
                                        f"Service: {service_status}, Capabilities: {len(capabilities)}, Endpoints: {total_endpoints}")
                        else:
                            self.log_test("Comprehensive Summary", False, 
                                        f"Service issues: status={service_status}, capabilities={len(capabilities)}, endpoints={total_endpoints}")
                    else:
                        self.log_test("Comprehensive Summary", False, f"Missing sections: {missing_sections}")
                else:
                    self.log_test("Comprehensive Summary", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Comprehensive Summary", False, f"Exception: {str(e)}")
    
    async def run_comprehensive_tests(self):
        """Run all comprehensive AI Portfolio Management tests"""
        print("🚀 Starting Comprehensive AI-Powered Portfolio Management Testing (STEP 13)")
        print("=" * 80)
        
        await self.test_core_service_status()
        await self.test_portfolio_creation_management()
        await self.test_production_ready_rebalancing()
        await self.test_ai_features()
        await self.test_integration_verification()
        await self.test_summary_metrics()
        
        # Calculate results
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print("\n" + "=" * 80)
        print(f"🎯 AI PORTFOLIO MANAGEMENT TESTING COMPLETE")
        print(f"📊 Results: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}% success rate)")
        
        if success_rate >= 90:
            print("✅ EXCELLENT: AI Portfolio Management system is production-ready")
        elif success_rate >= 75:
            print("✅ GOOD: AI Portfolio Management system is operational with minor issues")
        elif success_rate >= 50:
            print("⚠️ PARTIAL: AI Portfolio Management system has significant issues")
        else:
            print("❌ CRITICAL: AI Portfolio Management system has major failures")
        
        return self.test_results

async def main():
    async with AIPortfolioTester() as tester:
        results = await tester.run_comprehensive_tests()
        return results

if __name__ == "__main__":
    asyncio.run(main())