#!/usr/bin/env python3
"""
Direct AI Portfolio Service Test
Tests AI portfolio functionality without going through the full server startup
"""

import asyncio
import sys
import os
sys.path.append('/app/backend')

from services.ai_portfolio_service import AIPortfolioService, OptimizationStrategy, RebalancingTrigger

async def test_ai_portfolio_service():
    """Test AI portfolio service directly"""
    print("🤖 Testing AI Portfolio Service Directly...")
    
    try:
        # Initialize service
        service = AIPortfolioService()
        await service.start()
        print("✅ AI Portfolio Service started successfully")
        
        # Test service status
        status = service.get_ai_portfolio_status()
        print(f"✅ Service Status: {status['service_running']}, Portfolios: {status['ai_portfolios']}")
        
        # Test portfolio creation
        portfolio_data = {
            "portfolio_id": "test_portfolio_001",
            "client_id": "test_client_001",
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
        
        ai_config = await service.create_ai_portfolio(portfolio_data)
        print(f"✅ AI Portfolio Created: {ai_config.portfolio_id}, Strategy: {ai_config.optimization_strategy.value}")
        
        # Test portfolio optimization
        optimization_result = await service.optimize_portfolio("test_portfolio_001")
        print(f"✅ Portfolio Optimized: Expected Return: {optimization_result.expected_return:.2%}, Sharpe: {optimization_result.sharpe_ratio:.2f}")
        
        # Test market sentiment analysis
        sentiment_data = await service.analyze_market_sentiment(["USDT", "USDC", "DAI"])
        print(f"✅ Market Sentiment Analyzed: {len(sentiment_data)} symbols")
        
        # Test market regime detection
        regime = await service._detect_market_regime()
        print(f"✅ Market Regime Detected: {regime.value}")
        
        # Test rebalancing signal generation
        signal = await service.generate_rebalancing_signal("test_portfolio_001")
        if signal:
            print(f"✅ Rebalancing Signal Generated: {signal.signal_id}, Confidence: {signal.confidence_score:.2f}")
        else:
            print("✅ No rebalancing signal generated (conditions not met)")
        
        # Test service summary
        summary_status = service.get_ai_portfolio_status()
        print(f"✅ Final Status: Portfolios: {summary_status['ai_portfolios']}, Results: {summary_status['optimization_results']}")
        
        await service.stop()
        print("✅ AI Portfolio Service stopped successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing AI Portfolio Service: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    print("🚀 Starting Direct AI Portfolio Service Tests...")
    print("=" * 60)
    
    success = await test_ai_portfolio_service()
    
    print("=" * 60)
    if success:
        print("✅ All AI Portfolio Service tests completed successfully!")
    else:
        print("❌ AI Portfolio Service tests failed!")
    
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)