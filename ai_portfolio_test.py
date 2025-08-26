#!/usr/bin/env python3
"""
AI-Powered Portfolio Management & Automated Rebalancing (STEP 13) Test Suite
Tests all 15 AI portfolio endpoints locally
"""

import asyncio
import aiohttp
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List

# Use local backend URL for testing
API_BASE = "http://localhost:8001/api"

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
                        endpoints = data.get('endpoints', 0)
                        self.log_test("AI Portfolio Status", True, 
                                    f"Service: {'Running' if service_running else 'Stopped'}, Portfolios: {ai_portfolios}, Capabilities: {len(capabilities)}, Endpoints: {endpoints}")
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
        """Test POST /api/ai-portfolio/portfolios endpoint"""
        try:
            # Create test portfolio
            portfolio_data = {
                "portfolio_id": f"ai_test_portfolio_{uuid.uuid4().hex[:8]}",
                "client_id": f"test_client_{uuid.uuid4().hex[:8]}",
                "optimization_strategy": "mean_variance",  # Use simpler strategy
                "rebalancing_triggers": ["threshold_based"],
                "risk_tolerance": 0.6,
                "max_position_size": 0.4,
                "min_position_size": 0.1,
                "rebalancing_frequency": "weekly",
                "ai_confidence_threshold": 0.75,
                "performance_target": 0.08,
                "max_drawdown_limit": 0.15
            }
            
            async with self.session.post(f"{API_BASE}/ai-portfolio/portfolios", json=portfolio_data) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'ai_portfolio' in data and 'ai_features' in data:
                        ai_portfolio = data['ai_portfolio']
                        portfolio_id = ai_portfolio.get('portfolio_id')
                        strategy = ai_portfolio.get('optimization_strategy')
                        self.test_portfolio_id = portfolio_id  # Store for other tests
                        self.log_test("AI Portfolio Create", True, 
                                    f"Created portfolio {portfolio_id} with {strategy} strategy")
                    else:
                        self.log_test("AI Portfolio Create", False, f"Invalid response structure: {data}")
                else:
                    response_text = await response.text()
                    self.log_test("AI Portfolio Create", False, f"HTTP {response.status}: {response_text}")
        except Exception as e:
            self.log_test("AI Portfolio Create", False, f"Exception: {str(e)}")
    
    async def test_ai_portfolio_list(self):
        """Test GET /api/ai-portfolio/portfolios endpoint"""
        try:
            async with self.session.get(f"{API_BASE}/ai-portfolio/portfolios") as response:
                if response.status == 200:
                    data = await response.json()
                    if 'ai_portfolios' in data and 'total_portfolios' in data:
                        portfolios = data['ai_portfolios']
                        total = data['total_portfolios']
                        strategies = data.get('optimization_strategies_used', [])
                        self.log_test("AI Portfolio List", True, 
                                    f"Found {total} AI portfolios using {len(strategies)} strategies")
                    else:
                        self.log_test("AI Portfolio List", False, f"Invalid response structure: {data}")
                else:
                    self.log_test("AI Portfolio List", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("AI Portfolio List", False, f"Exception: {str(e)}")
    
    async def test_ai_portfolio_optimize(self):
        """Test POST /api/ai-portfolio/portfolios/{id}/optimize endpoint"""
        try:
            # Use test portfolio ID if available, otherwise create a test ID
            portfolio_id = self.test_portfolio_id or 'test_portfolio_123'
            
            optimization_data = {
                "optimization_strategy": "mean_variance"
            }
            
            async with self.session.post(f"{API_BASE}/ai-portfolio/portfolios/{portfolio_id}/optimize", 
                                       json=optimization_data) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'optimization_result' in data and 'optimization_insights' in data:
                        result = data['optimization_result']
                        strategy = result.get('optimization_strategy')
                        expected_return = result.get('performance_metrics', {}).get('expected_return', 0)
                        sharpe_ratio = result.get('performance_metrics', {}).get('sharpe_ratio', 0)
                        self.log_test("AI Portfolio Optimize", True, 
                                    f"Optimized with {strategy}: Return {expected_return:.2%}, Sharpe {sharpe_ratio:.2f}")
                    else:
                        self.log_test("AI Portfolio Optimize", False, f"Invalid response structure: {data}")
                elif response.status == 404:
                    self.log_test("AI Portfolio Optimize", False, f"Portfolio not found: {portfolio_id}")
                else:
                    response_text = await response.text()
                    self.log_test("AI Portfolio Optimize", False, f"HTTP {response.status}: {response_text}")
        except Exception as e:
            self.log_test("AI Portfolio Optimize", False, f"Exception: {str(e)}")
    
    async def test_ai_portfolio_optimization_result(self):
        """Test GET /api/ai-portfolio/portfolios/{id}/optimization-result endpoint"""
        try:
            portfolio_id = self.test_portfolio_id or 'test_portfolio_123'
            
            async with self.session.get(f"{API_BASE}/ai-portfolio/portfolios/{portfolio_id}/optimization-result") as response:
                if response.status == 200:
                    data = await response.json()
                    if 'optimization_result' in data and 'result_metadata' in data:
                        result = data['optimization_result']
                        strategy = result.get('optimization_strategy')
                        constraints_satisfied = result.get('constraints_satisfied')
                        self.log_test("AI Portfolio Optimization Result", True, 
                                    f"Result for {strategy}: Constraints {'satisfied' if constraints_satisfied else 'not satisfied'}")
                    else:
                        self.log_test("AI Portfolio Optimization Result", False, f"Invalid response structure: {data}")
                elif response.status == 404:
                    self.log_test("AI Portfolio Optimization Result", False, f"No optimization result found for {portfolio_id}")
                else:
                    self.log_test("AI Portfolio Optimization Result", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("AI Portfolio Optimization Result", False, f"Exception: {str(e)}")
    
    async def test_ai_portfolio_rebalancing_signal(self):
        """Test POST /api/ai-portfolio/portfolios/{id}/rebalancing-signal endpoint"""
        try:
            portfolio_id = self.test_portfolio_id or 'test_portfolio_123'
            
            async with self.session.post(f"{API_BASE}/ai-portfolio/portfolios/{portfolio_id}/rebalancing-signal") as response:
                if response.status == 200:
                    data = await response.json()
                    signal_generated = data.get('signal_generated', False)
                    
                    if signal_generated:
                        signal = data.get('rebalancing_signal', {})
                        signal_id = signal.get('signal_id')
                        confidence = signal.get('confidence_score', 0)
                        trigger = signal.get('trigger_type')
                        self.test_signal_id = signal_id  # Store for execution test
                        self.log_test("AI Portfolio Rebalancing Signal", True, 
                                    f"Generated signal {signal_id}: Confidence {confidence:.2f}, Trigger: {trigger}")
                    else:
                        reasons = data.get('reasons', [])
                        self.log_test("AI Portfolio Rebalancing Signal", True, 
                                    f"No signal generated: {len(reasons)} reasons (expected behavior)")
                else:
                    response_text = await response.text()
                    self.log_test("AI Portfolio Rebalancing Signal", False, f"HTTP {response.status}: {response_text}")
        except Exception as e:
            self.log_test("AI Portfolio Rebalancing Signal", False, f"Exception: {str(e)}")
    
    async def test_ai_portfolio_rebalancing_signals_list(self):
        """Test GET /api/ai-portfolio/portfolios/{id}/rebalancing-signals endpoint"""
        try:
            portfolio_id = self.test_portfolio_id or 'test_portfolio_123'
            
            async with self.session.get(f"{API_BASE}/ai-portfolio/portfolios/{portfolio_id}/rebalancing-signals") as response:
                if response.status == 200:
                    data = await response.json()
                    if 'rebalancing_signals' in data and 'total_signals' in data:
                        signals = data['rebalancing_signals']
                        total = data['total_signals']
                        active = data.get('active_signals', 0)
                        executed = data.get('executed_signals', 0)
                        avg_confidence = data.get('avg_confidence', 0)
                        self.log_test("AI Portfolio Rebalancing Signals List", True, 
                                    f"Found {total} signals ({active} active, {executed} executed), avg confidence: {avg_confidence:.2f}")
                    else:
                        self.log_test("AI Portfolio Rebalancing Signals List", False, f"Invalid response structure: {data}")
                else:
                    self.log_test("AI Portfolio Rebalancing Signals List", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("AI Portfolio Rebalancing Signals List", False, f"Exception: {str(e)}")
    
    async def test_ai_portfolio_execute_rebalancing(self):
        """Test POST /api/ai-portfolio/rebalancing-signals/{id}/execute endpoint"""
        try:
            # Use test signal ID if available, otherwise create a test ID
            signal_id = self.test_signal_id or 'test_signal_123'
            
            async with self.session.post(f"{API_BASE}/ai-portfolio/rebalancing-signals/{signal_id}/execute") as response:
                if response.status == 200:
                    data = await response.json()
                    if 'execution_result' in data and 'execution_summary' in data:
                        result = data['execution_result']
                        summary = data['execution_summary']
                        confidence = result.get('confidence_score', 0)
                        status = summary.get('status')
                        self.log_test("AI Portfolio Execute Rebalancing", True, 
                                    f"Executed rebalancing: Status {status}, Confidence {confidence:.2f}")
                    else:
                        self.log_test("AI Portfolio Execute Rebalancing", False, f"Invalid response structure: {data}")
                elif response.status == 404:
                    self.log_test("AI Portfolio Execute Rebalancing", False, f"Signal not found: {signal_id}")
                else:
                    self.log_test("AI Portfolio Execute Rebalancing", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("AI Portfolio Execute Rebalancing", False, f"Exception: {str(e)}")
    
    async def test_ai_portfolio_market_sentiment(self):
        """Test GET /api/ai-portfolio/market-sentiment endpoint"""
        try:
            async with self.session.get(f"{API_BASE}/ai-portfolio/market-sentiment") as response:
                if response.status == 200:
                    data = await response.json()
                    if 'market_sentiment' in data:
                        sentiment_data = data['market_sentiment']
                        individual = sentiment_data.get('individual_sentiments', [])
                        overview = sentiment_data.get('market_overview', {})
                        avg_sentiment = overview.get('average_sentiment', 0)
                        market_mood = overview.get('market_mood', 'Unknown')
                        self.log_test("AI Portfolio Market Sentiment", True, 
                                    f"Analyzed {len(individual)} symbols: Avg sentiment {avg_sentiment:.2f}, Mood: {market_mood}")
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
                    if 'market_regime' in data and 'market_indicators' in data:
                        regime_data = data['market_regime']
                        indicators = data['market_indicators']
                        current_regime = regime_data.get('current_regime')
                        confidence = regime_data.get('confidence')
                        volatility = indicators.get('yield_volatility', 0)
                        self.log_test("AI Portfolio Market Regime", True, 
                                    f"Current regime: {current_regime}, Confidence: {confidence}, Volatility: {volatility:.3f}")
                    else:
                        self.log_test("AI Portfolio Market Regime", False, f"Invalid response structure: {data}")
                else:
                    self.log_test("AI Portfolio Market Regime", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("AI Portfolio Market Regime", False, f"Exception: {str(e)}")
    
    async def test_ai_portfolio_insights(self):
        """Test GET /api/ai-portfolio/ai-insights/{id} endpoint"""
        try:
            portfolio_id = self.test_portfolio_id or 'test_portfolio_123'
            
            async with self.session.get(f"{API_BASE}/ai-portfolio/ai-insights/{portfolio_id}") as response:
                if response.status == 200:
                    data = await response.json()
                    if 'ai_insights' in data and 'portfolio_ai_status' in data:
                        insights = data['ai_insights']
                        insights_list = insights.get('insights', [])
                        insights_count = insights.get('insights_count', 0)
                        ai_status = data['portfolio_ai_status']
                        strategy = ai_status.get('optimization_strategy')
                        self.log_test("AI Portfolio Insights", True, 
                                    f"Generated {insights_count} insights for {strategy} portfolio")
                    else:
                        self.log_test("AI Portfolio Insights", False, f"Invalid response structure: {data}")
                elif response.status == 404:
                    self.log_test("AI Portfolio Insights", False, f"Portfolio not found: {portfolio_id}")
                else:
                    self.log_test("AI Portfolio Insights", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("AI Portfolio Insights", False, f"Exception: {str(e)}")
    
    async def test_ai_portfolio_summary(self):
        """Test GET /api/ai-portfolio/summary endpoint"""
        try:
            async with self.session.get(f"{API_BASE}/ai-portfolio/summary") as response:
                if response.status == 200:
                    data = await response.json()
                    if 'service_status' in data and 'ai_portfolio_management' in data:
                        service_status = data.get('service_status')
                        management = data.get('ai_portfolio_management', {})
                        performance = data.get('optimization_performance', {})
                        capabilities = data.get('ai_capabilities', [])
                        
                        ai_portfolios = management.get('ai_portfolios', 0)
                        total_optimizations = performance.get('total_optimizations', 0)
                        success_rate = performance.get('success_rate', 0)
                        
                        self.log_test("AI Portfolio Summary", True, 
                                    f"Service: {service_status}, {ai_portfolios} portfolios, {total_optimizations} optimizations, {success_rate:.1f}% success rate, {len(capabilities)} capabilities")
                    else:
                        self.log_test("AI Portfolio Summary", False, f"Invalid response structure: {data}")
                else:
                    self.log_test("AI Portfolio Summary", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("AI Portfolio Summary", False, f"Exception: {str(e)}")
    
    async def test_ai_portfolio_stop(self):
        """Test POST /api/ai-portfolio/stop endpoint"""
        try:
            async with self.session.post(f"{API_BASE}/ai-portfolio/stop") as response:
                if response.status == 200:
                    data = await response.json()
                    if 'message' in data and 'status' in data:
                        status = data.get('status')
                        self.log_test("AI Portfolio Stop", True, f"Service stopped: {status}")
                    else:
                        self.log_test("AI Portfolio Stop", False, f"Invalid response: {data}")
                else:
                    self.log_test("AI Portfolio Stop", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("AI Portfolio Stop", False, f"Exception: {str(e)}")
    
    async def run_all_tests(self):
        """Run all AI Portfolio Management tests"""
        print("🤖 Starting AI-Powered Portfolio Management & Automated Rebalancing (STEP 13) Tests")
        print(f"📍 API Base: {API_BASE}")
        print("=" * 80)
        
        # Service Management Tests
        print("\n🔧 SERVICE MANAGEMENT TESTS")
        await self.test_ai_portfolio_status()
        await self.test_ai_portfolio_start()
        
        # AI Portfolio Management Tests
        print("\n📊 AI PORTFOLIO MANAGEMENT TESTS")
        await self.test_ai_portfolio_create()
        await self.test_ai_portfolio_list()
        
        # Portfolio Optimization Tests
        print("\n⚡ PORTFOLIO OPTIMIZATION TESTS")
        await self.test_ai_portfolio_optimize()
        await self.test_ai_portfolio_optimization_result()
        
        # Automated Rebalancing Tests
        print("\n🔄 AUTOMATED REBALANCING TESTS")
        await self.test_ai_portfolio_rebalancing_signal()
        await self.test_ai_portfolio_rebalancing_signals_list()
        await self.test_ai_portfolio_execute_rebalancing()
        
        # Market Analysis Tests
        print("\n📈 MARKET ANALYSIS TESTS")
        await self.test_ai_portfolio_market_sentiment()
        await self.test_ai_portfolio_market_regime()
        
        # AI Analytics & Insights Tests
        print("\n🧠 AI ANALYTICS & INSIGHTS TESTS")
        await self.test_ai_portfolio_insights()
        
        # Comprehensive Summary Tests
        print("\n📋 COMPREHENSIVE SUMMARY TESTS")
        await self.test_ai_portfolio_summary()
        
        # Service Management Tests (Stop)
        print("\n🛑 SERVICE SHUTDOWN TESTS")
        await self.test_ai_portfolio_stop()
        
        # Print final results
        print("\n" + "=" * 80)
        print("📊 AI PORTFOLIO MANAGEMENT TEST RESULTS SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS ({failed_tests}):")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['details']}")
        
        print(f"\n🎯 AI PORTFOLIO TESTING COMPLETE - {success_rate:.1f}% SUCCESS RATE")
        return success_rate

async def main():
    """Main test runner"""
    async with AIPortfolioTester() as tester:
        await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())