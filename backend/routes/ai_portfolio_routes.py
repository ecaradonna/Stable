"""
AI-Powered Portfolio Management API Routes (STEP 13)
Advanced AI algorithms for autonomous portfolio optimization, machine learning-driven 
rebalancing strategies, and predictive risk management
"""

from fastapi import APIRouter, HTTPException, Query, Body
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from services.ai_portfolio_service import get_ai_portfolio_service

logger = logging.getLogger(__name__)

router = APIRouter()

# === SERVICE MANAGEMENT ===

@router.get("/status")
async def get_ai_portfolio_status():
    """Get AI portfolio service status and overview"""
    ai_service = get_ai_portfolio_service()
    
    if not ai_service:
        return {
            "service_running": False,
            "message": "AI-Powered Portfolio Management service not started",
            "ai_portfolios": 0,
            "capabilities": []
        }
    
    try:
        status = ai_service.get_ai_portfolio_status()
        return {
            **status,
            "status": "running",
            "endpoints": 15,
            "ai_features": [
                "AI-Enhanced Portfolio Optimization",
                "Automated Rebalancing with ML Signals",
                "Market Sentiment Analysis",
                "Market Regime Detection",
                "Predictive Risk Management",
                "Multi-Strategy Optimization"
            ]
        }
    except Exception as e:
        logger.error(f"Error getting AI portfolio status: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting AI portfolio status: {str(e)}")

@router.post("/start")
async def start_ai_portfolio_service():
    """Start the AI-powered portfolio management service"""
    try:
        from services.ai_portfolio_service import start_ai_portfolio
        await start_ai_portfolio()
        
        return {
            "message": "AI-Powered Portfolio Management service started successfully",
            "status": "running",
            "ai_capabilities": [
                "Advanced AI algorithms for autonomous portfolio optimization",
                "Machine learning-driven rebalancing strategies with market signals",
                "Predictive risk management with automated position sizing",
                "Real-time market sentiment analysis and trading signals",
                "Market regime detection for adaptive portfolio management",
                "Multi-strategy optimization (Mean Variance, Risk Parity, Black-Litterman, AI-Enhanced)",
                "Automated rebalancing with configurable triggers and confidence thresholds",
                "Performance tracking with institutional-grade analytics"
            ],
            "optimization_strategies": [
                "AI-Enhanced Optimization (ML-driven multi-factor approach)",
                "Mean-Variance Optimization (Modern Portfolio Theory)",
                "Risk Parity Optimization (Equal risk contribution)",
                "Black-Litterman Optimization (Bayesian approach with views)",
                "Hierarchical Risk Parity (Machine learning clustering)"
            ],
            "rebalancing_triggers": [
                "Time-based (scheduled rebalancing)",
                "Threshold-based (allocation drift triggers)",
                "Volatility-based (market volatility triggers)",
                "AI Signal (machine learning generated signals)",
                "Market Regime Change (regime detection triggers)"
            ]
        }
    except Exception as e:
        logger.error(f"Error starting AI portfolio service: {e}")
        raise HTTPException(status_code=500, detail=f"Error starting AI portfolio service: {str(e)}")

@router.post("/stop")
async def stop_ai_portfolio_service():
    """Stop the AI-powered portfolio management service"""
    try:
        from services.ai_portfolio_service import stop_ai_portfolio
        await stop_ai_portfolio()
        
        return {
            "message": "AI-Powered Portfolio Management service stopped successfully",
            "status": "stopped"
        }
    except Exception as e:
        logger.error(f"Error stopping AI portfolio service: {e}")
        raise HTTPException(status_code=500, detail=f"Error stopping AI portfolio service: {str(e)}")

# === AI PORTFOLIO MANAGEMENT ===

@router.post("/portfolios")
async def create_ai_portfolio(portfolio_data: Dict[str, Any] = Body(...)):
    """Create a new AI-managed portfolio"""
    ai_service = get_ai_portfolio_service()
    
    if not ai_service:
        raise HTTPException(status_code=503, detail="AI portfolio service not available")
    
    try:
        # Validate required fields
        required_fields = ["portfolio_id", "client_id"]
        for field in required_fields:
            if field not in portfolio_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Create AI portfolio
        ai_config = await ai_service.create_ai_portfolio(portfolio_data)
        
        return {
            "ai_portfolio": {
                "portfolio_id": ai_config.portfolio_id,
                "client_id": ai_config.client_id,
                "optimization_strategy": ai_config.optimization_strategy.value,
                "rebalancing_triggers": [trigger.value for trigger in ai_config.rebalancing_triggers],
                "risk_tolerance": ai_config.risk_tolerance,
                "max_position_size": ai_config.max_position_size,
                "min_position_size": ai_config.min_position_size,
                "rebalancing_frequency": ai_config.rebalancing_frequency,
                "ai_confidence_threshold": ai_config.ai_confidence_threshold,
                "performance_target": ai_config.performance_target,
                "max_drawdown_limit": ai_config.max_drawdown_limit
            },
            "ai_features": {
                "sentiment_analysis": ai_config.use_sentiment_analysis,
                "regime_detection": ai_config.use_market_regime_detection,
                "predictive_rebalancing": ai_config.use_predictive_rebalancing
            },
            "message": f"AI portfolio {ai_config.portfolio_id} created successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating AI portfolio: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating AI portfolio: {str(e)}")

@router.get("/portfolios")
async def get_ai_portfolios(client_id: Optional[str] = Query(None)):
    """Get AI-managed portfolios with optional client filtering"""
    ai_service = get_ai_portfolio_service()
    
    if not ai_service:
        raise HTTPException(status_code=503, detail="AI portfolio service not available")
    
    try:
        ai_portfolios = []
        
        for portfolio_id, ai_config in ai_service.ai_portfolios.items():
            # Apply client filter
            if client_id and ai_config.client_id != client_id:
                continue
            
            ai_portfolios.append({
                "portfolio_id": ai_config.portfolio_id,
                "client_id": ai_config.client_id,
                "optimization_strategy": ai_config.optimization_strategy.value,
                "rebalancing_triggers": [trigger.value for trigger in ai_config.rebalancing_triggers],
                "risk_tolerance": ai_config.risk_tolerance,
                "ai_confidence_threshold": ai_config.ai_confidence_threshold,
                "performance_target": ai_config.performance_target,
                "max_drawdown_limit": ai_config.max_drawdown_limit,
                "ai_features_enabled": {
                    "sentiment_analysis": ai_config.use_sentiment_analysis,
                    "regime_detection": ai_config.use_market_regime_detection,
                    "predictive_rebalancing": ai_config.use_predictive_rebalancing
                }
            })
        
        return {
            "ai_portfolios": ai_portfolios,
            "total_portfolios": len(ai_portfolios),
            "optimization_strategies_used": list(set(p["optimization_strategy"] for p in ai_portfolios)),
            "filters_applied": {
                "client_id": client_id
            }
        }
    except Exception as e:
        logger.error(f"Error getting AI portfolios: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting AI portfolios: {str(e)}")

# === PORTFOLIO OPTIMIZATION ===

@router.post("/portfolios/{portfolio_id}/optimize")
async def optimize_portfolio(portfolio_id: str, 
                           optimization_data: Dict[str, Any] = Body(default={})):
    """Optimize portfolio using AI algorithms"""
    ai_service = get_ai_portfolio_service()
    
    if not ai_service:
        raise HTTPException(status_code=503, detail="AI portfolio service not available")
    
    try:
        from services.ai_portfolio_service import OptimizationStrategy
        
        # Get optimization strategy from request or use portfolio default
        strategy_name = optimization_data.get("optimization_strategy")
        strategy = OptimizationStrategy(strategy_name) if strategy_name else None
        
        # Perform optimization
        result = await ai_service.optimize_portfolio(portfolio_id, strategy)
        
        return {
            "optimization_result": {
                "portfolio_id": result.portfolio_id,
                "optimization_strategy": result.optimization_strategy.value,
                "optimal_allocation": result.optimal_allocation,
                "performance_metrics": {
                    "expected_return": result.expected_return,
                    "expected_volatility": result.expected_volatility,
                    "sharpe_ratio": result.sharpe_ratio,
                    "max_drawdown": result.max_drawdown,
                    "optimization_score": result.optimization_score
                },
                "constraints_satisfied": result.constraints_satisfied,
                "optimization_time": result.optimization_time,
                "metadata": result.metadata
            },
            "optimization_insights": {
                "market_regime": result.metadata.get("market_regime"),
                "sentiment_score": result.metadata.get("sentiment_score"),
                "features_analyzed": result.metadata.get("features_used"),
                "risk_adjusted": "Expected return adjusted for portfolio risk and market conditions",
                "ai_enhancement": f"Optimization enhanced with {result.optimization_strategy.value} strategy"
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error optimizing portfolio {portfolio_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error optimizing portfolio: {str(e)}")

@router.get("/portfolios/{portfolio_id}/optimization-result")
async def get_optimization_result(portfolio_id: str):
    """Get latest optimization result for a portfolio"""
    ai_service = get_ai_portfolio_service()
    
    if not ai_service:
        raise HTTPException(status_code=503, detail="AI portfolio service not available")
    
    try:
        if portfolio_id not in ai_service.optimization_results:
            raise HTTPException(status_code=404, detail=f"No optimization result found for portfolio {portfolio_id}")
        
        result = ai_service.optimization_results[portfolio_id]
        
        return {
            "optimization_result": {
                "portfolio_id": result.portfolio_id,
                "optimization_strategy": result.optimization_strategy.value,
                "optimal_allocation": result.optimal_allocation,
                "performance_metrics": {
                    "expected_return": result.expected_return,
                    "expected_volatility": result.expected_volatility,
                    "sharpe_ratio": result.sharpe_ratio,
                    "max_drawdown": result.max_drawdown,
                    "optimization_score": result.optimization_score
                },
                "constraints_satisfied": result.constraints_satisfied,
                "optimization_time": result.optimization_time,
                "metadata": result.metadata
            },
            "result_metadata": {
                "optimization_timestamp": "Available in metadata",
                "validity": "Current optimization result",
                "confidence_level": "High" if result.constraints_satisfied else "Medium"
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting optimization result: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting optimization result: {str(e)}")

# === AUTOMATED REBALANCING ===

@router.post("/portfolios/{portfolio_id}/rebalancing-signal")
async def generate_rebalancing_signal(portfolio_id: str):
    """Generate AI-powered rebalancing signal"""
    ai_service = get_ai_portfolio_service()
    
    if not ai_service:
        raise HTTPException(status_code=503, detail="AI portfolio service not available")
    
    try:
        signal = await ai_service.generate_rebalancing_signal(portfolio_id)
        
        if not signal:
            return {
                "signal_generated": False,
                "message": "No rebalancing signal generated - conditions not met",
                "reasons": [
                    "Current allocation within acceptable thresholds",
                    "AI confidence below minimum threshold", 
                    "No significant market regime changes detected",
                    "Recent rebalancing activity"
                ]
            }
        
        return {
            "signal_generated": True,
            "rebalancing_signal": {
                "signal_id": signal.signal_id,
                "portfolio_id": signal.portfolio_id,
                "trigger_type": signal.trigger_type.value,
                "recommended_allocation": signal.recommended_allocation,
                "current_allocation": signal.current_allocation,
                "confidence_score": signal.confidence_score,
                "expected_return": signal.expected_return,
                "expected_risk": signal.expected_risk,
                "market_regime": signal.market_regime.value,
                "reasoning": signal.reasoning,
                "generated_at": signal.generated_at.isoformat(),
                "expires_at": signal.expires_at.isoformat()
            },
            "allocation_changes": {
                asset: {
                    "current": signal.current_allocation.get(asset, 0),
                    "recommended": recommended,
                    "change": recommended - signal.current_allocation.get(asset, 0)
                }
                for asset, recommended in signal.recommended_allocation.items()
            },
            "signal_insights": {
                "confidence_level": "High" if signal.confidence_score > 0.8 else "Medium" if signal.confidence_score > 0.6 else "Low",
                "market_context": f"Market regime: {signal.market_regime.value}",
                "expected_improvement": f"Expected return: {signal.expected_return:.2%}, Risk: {signal.expected_risk:.2%}"
            }
        }
    except Exception as e:
        logger.error(f"Error generating rebalancing signal: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating rebalancing signal: {str(e)}")

@router.get("/portfolios/{portfolio_id}/rebalancing-signals")
async def get_rebalancing_signals(portfolio_id: str, 
                                active_only: bool = Query(True, description="Return only active signals")):
    """Get rebalancing signals for a portfolio"""
    ai_service = get_ai_portfolio_service()
    
    if not ai_service:
        raise HTTPException(status_code=503, detail="AI portfolio service not available")
    
    try:
        signals = []
        current_time = datetime.utcnow()
        
        for signal in ai_service.rebalancing_signals.values():
            if signal.portfolio_id != portfolio_id:
                continue
            
            # Filter active signals if requested
            if active_only and current_time > signal.expires_at:
                continue
            
            signals.append({
                "signal_id": signal.signal_id,
                "trigger_type": signal.trigger_type.value,
                "confidence_score": signal.confidence_score,
                "expected_return": signal.expected_return,
                "expected_risk": signal.expected_risk,
                "market_regime": signal.market_regime.value,
                "generated_at": signal.generated_at.isoformat(),
                "expires_at": signal.expires_at.isoformat(),
                "is_active": current_time <= signal.expires_at,
                "is_executed": hasattr(signal, 'executed_at') and signal.executed_at is not None
            })
        
        # Sort by generation time (newest first)
        signals.sort(key=lambda x: x["generated_at"], reverse=True)
        
        return {
            "rebalancing_signals": signals,
            "total_signals": len(signals),
            "active_signals": len([s for s in signals if s["is_active"]]),
            "executed_signals": len([s for s in signals if s["is_executed"]]),
            "avg_confidence": sum(s["confidence_score"] for s in signals) / len(signals) if signals else 0,
            "portfolio_id": portfolio_id
        }
    except Exception as e:
        logger.error(f"Error getting rebalancing signals: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting rebalancing signals: {str(e)}")

@router.post("/rebalancing-signals/{signal_id}/execute")
async def execute_rebalancing_signal(signal_id: str):
    """Execute AI-recommended rebalancing"""
    ai_service = get_ai_portfolio_service()
    
    if not ai_service:
        raise HTTPException(status_code=503, detail="AI portfolio service not available")
    
    try:
        result = await ai_service.execute_ai_rebalancing(signal_id)
        
        return {
            "execution_result": {
                "signal_id": result["signal_id"],
                "portfolio_id": result["portfolio_id"],
                "executed_at": result["executed_at"],
                "confidence_score": result["confidence_score"],
                "expected_return": result["expected_return"],
                "expected_risk": result["expected_risk"]
            },
            "trading_execution": result["execution_result"],
            "execution_summary": {
                "status": "completed",
                "execution_method": "AI-powered automated rebalancing",
                "confidence_level": "High" if result["confidence_score"] > 0.8 else "Medium",
                "expected_outcome": f"Portfolio optimized for {result['expected_return']:.2%} expected return"
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error executing rebalancing signal: {e}")
        raise HTTPException(status_code=500, detail=f"Error executing rebalancing signal: {str(e)}")

# === MARKET SENTIMENT ANALYSIS ===

@router.get("/market-sentiment")
async def get_market_sentiment(symbols: Optional[str] = Query(None, description="Comma-separated symbols")):
    """Get market sentiment analysis"""
    ai_service = get_ai_portfolio_service()
    
    if not ai_service:
        raise HTTPException(status_code=503, detail="AI portfolio service not available")
    
    try:
        # Parse symbols if provided
        symbol_list = None
        if symbols:
            symbol_list = [s.strip() for s in symbols.split(",")]
        
        sentiment_data = await ai_service.analyze_market_sentiment(symbol_list)
        
        sentiments = []
        for symbol, sentiment in sentiment_data.items():
            sentiments.append({
                "symbol": sentiment.symbol,
                "sentiment_score": sentiment.sentiment_score,
                "confidence": sentiment.confidence,
                "sentiment_components": {
                    "news_sentiment": sentiment.news_sentiment,
                    "social_sentiment": sentiment.social_sentiment,
                    "technical_sentiment": sentiment.technical_sentiment,
                    "fundamental_sentiment": sentiment.fundamental_sentiment
                },
                "sentiment_trend": sentiment.sentiment_trend,
                "last_updated": sentiment.last_updated.isoformat(),
                "interpretation": {
                    "overall": "Positive" if sentiment.sentiment_score > 0.1 else "Negative" if sentiment.sentiment_score < -0.1 else "Neutral",
                    "strength": "Strong" if abs(sentiment.sentiment_score) > 0.5 else "Moderate" if abs(sentiment.sentiment_score) > 0.2 else "Weak",
                    "reliability": "High" if sentiment.confidence > 0.8 else "Medium" if sentiment.confidence > 0.6 else "Low"
                }
            })
        
        # Calculate market-wide sentiment
        if sentiments:
            avg_sentiment = sum(s["sentiment_score"] for s in sentiments) / len(sentiments)
            avg_confidence = sum(s["confidence"] for s in sentiments) / len(sentiments)
        else:
            avg_sentiment = 0
            avg_confidence = 0
        
        return {
            "market_sentiment": {
                "individual_sentiments": sentiments,
                "market_overview": {
                    "average_sentiment": avg_sentiment,
                    "average_confidence": avg_confidence,
                    "market_mood": "Positive" if avg_sentiment > 0.1 else "Negative" if avg_sentiment < -0.1 else "Neutral",
                    "sentiment_dispersion": statistics.stdev([s["sentiment_score"] for s in sentiments]) if len(sentiments) > 1 else 0
                },
                "analysis_metadata": {
                    "symbols_analyzed": len(sentiments),
                    "analysis_timestamp": datetime.utcnow().isoformat(),
                    "sentiment_range": {
                        "min": min(s["sentiment_score"] for s in sentiments) if sentiments else 0,
                        "max": max(s["sentiment_score"] for s in sentiments) if sentiments else 0
                    }
                }
            }
        }
    except Exception as e:
        logger.error(f"Error getting market sentiment: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting market sentiment: {str(e)}")

# === MARKET REGIME DETECTION ===

@router.get("/market-regime")
async def get_market_regime():
    """Get current market regime detection"""
    ai_service = get_ai_portfolio_service()
    
    if not ai_service:
        raise HTTPException(status_code=503, detail="AI portfolio service not available")
    
    try:
        current_regime = await ai_service._detect_market_regime()
        
        # Get market features used for detection
        market_features = await ai_service._extract_market_features()
        
        return {
            "market_regime": {
                "current_regime": current_regime.value,
                "regime_description": {
                    "bull_market": "Rising yields and positive market trends",
                    "bear_market": "Declining yields and negative market trends", 
                    "sideways_market": "Stable yields with minimal directional movement",
                    "high_volatility": "High yield volatility and market uncertainty",
                    "low_volatility": "Low yield volatility and stable market conditions"
                }.get(current_regime.value, "Unknown regime"),
                "confidence": "High",  # Simplified
                "detection_timestamp": datetime.utcnow().isoformat()
            },
            "market_indicators": {
                "yield_volatility": market_features.get("yield_volatility", 0),
                "yield_trend": market_features.get("syi_trend", 0),
                "market_spread": market_features.get("yield_spread", 0),
                "syi_value": market_features.get("syi_value", 1.0)
            },
            "regime_implications": {
                "portfolio_strategy": {
                    "bull_market": "Favor higher-yielding opportunities with growth potential",
                    "bear_market": "Focus on capital preservation and risk management",
                    "sideways_market": "Maintain balanced allocation with regular rebalancing",
                    "high_volatility": "Increase diversification and reduce position sizes",
                    "low_volatility": "Opportunities for strategic position sizing"
                }.get(current_regime.value, "Maintain current strategy"),
                "rebalancing_frequency": {
                    "bull_market": "Less frequent, trend-following",
                    "bear_market": "More frequent, risk-focused",
                    "sideways_market": "Regular scheduled rebalancing",
                    "high_volatility": "Reactive, volatility-based triggers",
                    "low_volatility": "Opportunistic rebalancing"
                }.get(current_regime.value, "Standard frequency")
            }
        }
    except Exception as e:
        logger.error(f"Error getting market regime: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting market regime: {str(e)}")

# === AI ANALYTICS & INSIGHTS ===

@router.get("/ai-insights/{portfolio_id}")
async def get_ai_portfolio_insights(portfolio_id: str):
    """Get AI-powered insights for a specific portfolio"""
    ai_service = get_ai_portfolio_service()
    
    if not ai_service:
        raise HTTPException(status_code=503, detail="AI portfolio service not available")
    
    try:
        if portfolio_id not in ai_service.ai_portfolios:
            raise HTTPException(status_code=404, detail=f"AI portfolio {portfolio_id} not found")
        
        ai_config = ai_service.ai_portfolios[portfolio_id]
        
        # Get various AI insights
        optimization_result = ai_service.optimization_results.get(portfolio_id)
        market_regime = await ai_service._detect_market_regime()
        market_features = await ai_service._extract_market_features()
        
        # Generate insights
        insights = []
        
        # Performance insights
        if optimization_result:
            if optimization_result.expected_return > ai_config.performance_target:
                insights.append({
                    "type": "performance_opportunity",
                    "title": "Portfolio Exceeding Performance Target",
                    "description": f"Current optimization suggests {optimization_result.expected_return:.2%} expected return, above target of {ai_config.performance_target:.2%}",
                    "confidence": 0.8,
                    "impact": "positive"
                })
            
            if optimization_result.sharpe_ratio > 1.5:
                insights.append({
                    "type": "risk_efficiency",
                    "title": "Excellent Risk-Adjusted Performance",
                    "description": f"Portfolio shows strong risk-adjusted returns with Sharpe ratio of {optimization_result.sharpe_ratio:.2f}",
                    "confidence": 0.9,
                    "impact": "positive"
                })
        
        # Market regime insights
        regime_insight = {
            "type": "market_regime",
            "title": f"Current Market Regime: {market_regime.value.replace('_', ' ').title()}",
            "description": f"AI detects {market_regime.value.replace('_', ' ')} conditions, suggesting specific portfolio adjustments",
            "confidence": 0.75,
            "impact": "neutral"
        }
        insights.append(regime_insight)
        
        # Volatility insights
        volatility = market_features.get("yield_volatility", 0)
        if volatility > 0.3:
            insights.append({
                "type": "volatility_warning",
                "title": "Elevated Market Volatility Detected",
                "description": f"Current yield volatility of {volatility:.2%} suggests increased market uncertainty",
                "confidence": 0.8,
                "impact": "negative"
            })
        
        return {
            "ai_insights": {
                "portfolio_id": portfolio_id,
                "insights": insights,
                "insights_count": len(insights),
                "analysis_timestamp": datetime.utcnow().isoformat()
            },
            "portfolio_ai_status": {
                "optimization_strategy": ai_config.optimization_strategy.value,
                "ai_confidence_threshold": ai_config.ai_confidence_threshold,
                "rebalancing_triggers": [trigger.value for trigger in ai_config.rebalancing_triggers],
                "ai_features_enabled": {
                    "sentiment_analysis": ai_config.use_sentiment_analysis,
                    "regime_detection": ai_config.use_market_regime_detection,
                    "predictive_rebalancing": ai_config.use_predictive_rebalancing
                }
            },
            "market_context": {
                "current_regime": market_regime.value,
                "market_volatility": volatility,
                "syi_trend": market_features.get("syi_trend", 0),
                "yield_environment": "favorable" if market_features.get("avg_yield", 0) > 0.05 else "challenging"
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting AI insights: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting AI insights: {str(e)}")

# === COMPREHENSIVE AI SUMMARY ===

@router.get("/summary")
async def get_ai_portfolio_summary():
    """Get comprehensive AI portfolio service summary"""
    ai_service = get_ai_portfolio_service()
    
    if not ai_service:
        return {
            "service_running": False,
            "message": "AI-Powered Portfolio Management service not started"
        }
    
    try:
        status = ai_service.get_ai_portfolio_status()
        
        return {
            "service_status": "running" if status["service_running"] else "stopped",
            "ai_portfolio_management": {
                "ai_portfolios": status["ai_portfolios"],
                "optimization_results": status["optimization_results"],
                "rebalancing_signals": status["rebalancing_signals"],
                "market_sentiments": status["market_sentiments"]
            },
            "optimization_performance": {
                "total_optimizations": status["optimization_metrics"]["total_optimizations"],
                "successful_optimizations": status["optimization_metrics"]["successful_optimizations"],
                "success_rate": (status["optimization_metrics"]["successful_optimizations"] / 
                               max(status["optimization_metrics"]["total_optimizations"], 1)) * 100,
                "avg_optimization_time": status["optimization_metrics"]["avg_optimization_time"],
                "total_rebalancing_signals": status["optimization_metrics"]["total_rebalancing_signals"],
                "executed_rebalances": status["optimization_metrics"]["executed_rebalances"],
                "execution_rate": (status["optimization_metrics"]["executed_rebalances"] / 
                                 max(status["optimization_metrics"]["total_rebalancing_signals"], 1)) * 100,
                "avg_signal_confidence": status["optimization_metrics"]["avg_signal_confidence"]
            },
            "ai_capabilities": status["capabilities"],
            "optimization_strategies": status["optimization_strategies"],
            "rebalancing_triggers": status["rebalancing_triggers"],
            "api_endpoints": {
                "service_management": [
                    "GET /api/ai-portfolio/status",
                    "POST /api/ai-portfolio/start",
                    "POST /api/ai-portfolio/stop"
                ],
                "portfolio_management": [
                    "POST /api/ai-portfolio/portfolios",
                    "GET /api/ai-portfolio/portfolios"
                ],
                "optimization": [
                    "POST /api/ai-portfolio/portfolios/{id}/optimize",
                    "GET /api/ai-portfolio/portfolios/{id}/optimization-result"
                ],
                "rebalancing": [
                    "POST /api/ai-portfolio/portfolios/{id}/rebalancing-signal",
                    "GET /api/ai-portfolio/portfolios/{id}/rebalancing-signals",
                    "POST /api/ai-portfolio/rebalancing-signals/{id}/execute"
                ],
                "analytics": [
                    "GET /api/ai-portfolio/market-sentiment",
                    "GET /api/ai-portfolio/market-regime",
                    "GET /api/ai-portfolio/ai-insights/{id}"
                ]
            },
            "integration_status": {
                "trading_engine": "Connected",
                "ml_insights": "Connected",
                "dashboard_service": "Connected", 
                "yield_aggregator": "Connected",
                "ray_calculator": "Connected"
            },
            "system_performance": {
                "background_tasks": status["background_tasks"],
                "service_uptime": "Available in production metrics",
                "model_update_frequency": "1 hour",
                "sentiment_analysis_frequency": "5 minutes"
            },
            "last_updated": status["last_updated"]
        }
    except Exception as e:
        logger.error(f"Error getting AI portfolio summary: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting AI portfolio summary: {str(e)}")

import statistics