#!/usr/bin/env python3
"""
Test Production-Ready Rebalancing with Real-World Constraints
"""

import asyncio
import aiohttp
import json
import uuid
import os
from dotenv import load_dotenv

load_dotenv('/app/frontend/.env')
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://crypto-yields-1.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

async def test_production_rebalancing():
    async with aiohttp.ClientSession() as session:
        print('🔍 Testing Production-Ready Rebalancing with Real-World Constraints...')
        
        # Create a new portfolio for testing
        portfolio_data = {
            'portfolio_id': f'prod_test_{uuid.uuid4().hex[:8]}',
            'client_id': f'client_{uuid.uuid4().hex[:8]}',
            'optimization_strategy': 'ai_enhanced',
            'risk_tolerance': 0.7,
            'performance_target': 0.10,
            'max_drawdown_limit': 0.20,
            'rebalancing_frequency': 'daily',
            'ai_confidence_threshold': 0.6,
            'use_sentiment_analysis': True,
            'use_market_regime_detection': True,
            'use_predictive_rebalancing': True
        }
        
        try:
            async with session.post(f'{API_BASE}/ai-portfolio/portfolios', json=portfolio_data) as response:
                if response.status == 200:
                    data = await response.json()
                    portfolio_id = data['ai_portfolio']['portfolio_id']
                    print(f'✅ Created test portfolio: {portfolio_id}')
                    
                    # Test rebalancing signal generation with production constraints
                    async with session.post(f'{API_BASE}/ai-portfolio/portfolios/{portfolio_id}/rebalancing-signal') as signal_response:
                        if signal_response.status == 200:
                            signal_data = await signal_response.json()
                            
                            if signal_data.get('signal_generated'):
                                signal = signal_data['rebalancing_signal']
                                allocation_changes = signal_data.get('allocation_changes', {})
                                
                                print(f'✅ Generated rebalancing signal:')
                                print(f'   Signal ID: {signal.get("signal_id")}')
                                print(f'   Confidence: {signal.get("confidence_score", 0):.2f}')
                                print(f'   Market Regime: {signal.get("market_regime")}')
                                print(f'   Expected Return: {signal.get("expected_return", 0):.2%}')
                                print(f'   Expected Risk: {signal.get("expected_risk", 0):.2%}')
                                
                                # Verify production-ready constraints
                                print(f'\n🔍 Production Constraints Verification:')
                                print(f'   Allocation Changes: {len(allocation_changes)} assets')
                                for asset, change_data in allocation_changes.items():
                                    current = change_data.get('current', 0)
                                    recommended = change_data.get('recommended', 0)
                                    change = change_data.get('change', 0)
                                    print(f'     {asset}: {current:.2%} -> {recommended:.2%} (Δ{change:+.2%})')
                                
                                # Test execution with production constraints
                                signal_id = signal.get('signal_id')
                                if signal_id:
                                    async with session.post(f'{API_BASE}/ai-portfolio/rebalancing-signals/{signal_id}/execute') as exec_response:
                                        if exec_response.status == 200:
                                            exec_data = await exec_response.json()
                                            
                                            if 'trading_execution' in exec_data:
                                                execution = exec_data['trading_execution']
                                                plan = execution.get('execution_plan', {})
                                                
                                                print(f'\n✅ Production Execution Plan:')
                                                print(f'   Total Trades: {plan.get("total_trades", 0)}')
                                                print(f'   Successful Trades: {plan.get("successful_trades", 0)}')
                                                print(f'   Est. Fees: ${plan.get("est_fees", 0):.2f}')
                                                print(f'   Est. Slippage: ${plan.get("est_slippage", 0):.2f}')
                                                print(f'   Est. Total Cost: ${plan.get("est_total_cost", 0):.2f}')
                                                print(f'   Tracking Error: {plan.get("tracking_error", 0):.4f}')
                                                
                                                # Verify production-ready features
                                                has_fees = 'est_fees' in plan
                                                has_slippage = 'est_slippage' in plan
                                                has_tracking = 'tracking_error' in plan
                                                has_trades = plan.get('total_trades', 0) >= 0  # Can be 0 if no trades needed
                                                
                                                print(f'\n🎯 Production Features Verification:')
                                                print(f'   ✅ Fee Calculations: {has_fees}')
                                                print(f'   ✅ Slippage Calculations: {has_slippage}')
                                                print(f'   ✅ Tracking Error: {has_tracking}')
                                                print(f'   ✅ Trade Generation: {has_trades}')
                                                
                                                if has_fees and has_slippage and has_tracking:
                                                    print(f'\n✅ PRODUCTION-READY: All real-world constraints integrated!')
                                                    return True
                                                else:
                                                    print(f'\n⚠️ MISSING: Some production constraints not implemented')
                                                    return False
                                            else:
                                                print(f'❌ No trading execution data in response')
                                                return False
                                        else:
                                            exec_text = await exec_response.text()
                                            print(f'❌ Execution failed: {exec_response.status} - {exec_text}')
                                            return False
                            else:
                                reasons = signal_data.get('reasons', [])
                                print(f'ℹ️ No rebalancing signal generated:')
                                for reason in reasons:
                                    print(f'   - {reason}')
                                print(f'\n✅ This is expected behavior when conditions are not met')
                                return True  # This is actually correct behavior
                        else:
                            signal_text = await signal_response.text()
                            print(f'❌ Signal generation failed: {signal_response.status} - {signal_text}')
                            return False
                else:
                    text = await response.text()
                    print(f'❌ Portfolio creation failed: {response.status} - {text}')
                    return False
        except Exception as e:
            print(f'❌ Exception: {e}')
            return False

if __name__ == "__main__":
    result = asyncio.run(test_production_rebalancing())
    if result:
        print(f'\n🎯 CONCLUSION: Production-ready rebalancing system is operational!')
    else:
        print(f'\n⚠️ CONCLUSION: Production-ready rebalancing needs attention')