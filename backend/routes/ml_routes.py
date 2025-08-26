"""
Machine Learning Routes (STEP 8)
API endpoints for ML insights, yield predictions, anomaly detection, and AI-powered analytics
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

from services.ml_insights_service import get_ml_insights_service
from services.yield_aggregator import YieldAggregator

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/ml/status")
async def get_ml_status() -> Dict[str, Any]:
    """Get ML service status and model information"""
    try:
        ml_service = get_ml_insights_service()
        
        if not ml_service:
            return {
                "service_initialized": False,
                "message": "ML Insights service not started",
                "models_trained": {},
                "cache_statistics": {}
            }
        
        return ml_service.get_ml_status()
        
    except Exception as e:
        logger.error(f"Error getting ML status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get ML status")

@router.post("/ml/start")
async def start_ml_service() -> Dict[str, Any]:
    """Start the ML insights service and initialize models"""
    try:
        from services.ml_insights_service import start_ml_insights
        
        await start_ml_insights()
        
        return {
            "message": "ML Insights service started successfully",
            "capabilities": [
                "Yield prediction (1d, 7d, 30d horizons)",
                "Anomaly detection (yield spikes, drops, risk increases)",
                "Market sentiment analysis",
                "Risk prediction modeling",
                "AI-powered market insights",
                "Portfolio optimization recommendations"
            ],
            "models": [
                "Random Forest Yield Predictor",
                "Isolation Forest Anomaly Detector", 
                "Random Forest Risk Predictor",
                "K-Means Market Segmentation"
            ],
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error starting ML service: {e}")
        raise HTTPException(status_code=500, detail="Failed to start ML service")

@router.post("/ml/stop")
async def stop_ml_service() -> Dict[str, Any]:
    """Stop the ML insights service"""
    try:
        from services.ml_insights_service import stop_ml_insights
        
        await stop_ml_insights()
        
        return {
            "message": "ML Insights service stopped successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error stopping ML service: {e}")
        raise HTTPException(status_code=500, detail="Failed to stop ML service")

@router.get("/ml/predictions")
async def get_yield_predictions() -> Dict[str, Any]:
    """Get ML-powered yield predictions for all stablecoins"""
    try:
        ml_service = get_ml_insights_service()
        
        if not ml_service:
            raise HTTPException(status_code=503, detail="ML Insights service not running")
        
        # Get current yield data
        yield_aggregator = YieldAggregator()
        current_yields = await yield_aggregator.get_all_yields()
        
        if not current_yields:
            return {
                "message": "No yield data available for predictions",
                "predictions": []
            }
        
        # Generate predictions
        predictions = await ml_service.predict_yields(current_yields)
        
        # Format predictions for API response
        formatted_predictions = []
        for pred in predictions:
            formatted_predictions.append({
                "symbol": pred.symbol,
                "current_yield": pred.current_yield,
                "predictions": {
                    "1_day": {
                        "predicted_yield": pred.predicted_yield_1d,
                        "confidence": pred.confidence_1d
                    },
                    "7_day": {
                        "predicted_yield": pred.predicted_yield_7d,
                        "confidence": pred.confidence_7d
                    },
                    "30_day": {
                        "predicted_yield": pred.predicted_yield_30d,
                        "confidence": pred.confidence_30d
                    }
                },
                "trend_direction": pred.trend_direction,
                "prediction_timestamp": pred.prediction_timestamp.isoformat()
            })
        
        # Calculate summary statistics
        avg_confidence_1d = sum(p.confidence_1d for p in predictions) / len(predictions)
        avg_confidence_7d = sum(p.confidence_7d for p in predictions) / len(predictions)
        avg_confidence_30d = sum(p.confidence_30d for p in predictions) / len(predictions)
        
        trend_distribution = {}
        for pred in predictions:
            trend_distribution[pred.trend_direction] = trend_distribution.get(pred.trend_direction, 0) + 1
        
        return {
            "predictions": formatted_predictions,
            "total_symbols": len(predictions),
            "summary_statistics": {
                "average_confidence": {
                    "1_day": avg_confidence_1d,
                    "7_day": avg_confidence_7d,
                    "30_day": avg_confidence_30d
                },
                "trend_distribution": trend_distribution,
                "high_confidence_predictions": len([p for p in predictions if p.confidence_7d > 0.8])
            },
            "methodology": "Random Forest with time series features",
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting yield predictions: {e}")
        raise HTTPException(status_code=500, detail="Failed to get yield predictions")

@router.get("/ml/anomalies")
async def get_anomaly_detection() -> Dict[str, Any]:
    """Get ML-powered anomaly detection results"""
    try:
        ml_service = get_ml_insights_service()
        
        if not ml_service:
            raise HTTPException(status_code=503, detail="ML Insights service not running")
        
        # Get current yield data
        yield_aggregator = YieldAggregator()
        current_yields = await yield_aggregator.get_all_yields()
        
        if not current_yields:
            return {
                "message": "No yield data available for anomaly detection",
                "anomalies": []
            }
        
        # Detect anomalies
        anomalies = await ml_service.detect_anomalies(current_yields)
        
        # Format anomalies for API response
        formatted_anomalies = []
        for anomaly in anomalies:
            formatted_anomalies.append({
                "symbol": anomaly.symbol,
                "anomaly_type": anomaly.anomaly_type,
                "severity": anomaly.severity,
                "current_value": anomaly.current_value,
                "expected_value": anomaly.expected_value,
                "deviation_magnitude": anomaly.deviation_magnitude,
                "confidence_score": anomaly.confidence_score,
                "description": anomaly.description,
                "timestamp": anomaly.timestamp.isoformat()
            })
        
        # Calculate summary statistics
        severity_distribution = {}
        anomaly_type_distribution = {}
        
        for anomaly in anomalies:
            severity_distribution[anomaly.severity] = severity_distribution.get(anomaly.severity, 0) + 1
            anomaly_type_distribution[anomaly.anomaly_type] = anomaly_type_distribution.get(anomaly.anomaly_type, 0) + 1
        
        return {
            "anomalies": formatted_anomalies,
            "total_anomalies": len(anomalies),
            "symbols_affected": len(set(a.symbol for a in anomalies)),
            "summary_statistics": {
                "severity_distribution": severity_distribution,
                "anomaly_type_distribution": anomaly_type_distribution,
                "critical_anomalies": len([a for a in anomalies if a.severity == "critical"]),
                "high_confidence_anomalies": len([a for a in anomalies if a.confidence_score > 0.8])
            },
            "methodology": "Isolation Forest with multi-dimensional features",
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting anomaly detection: {e}")
        raise HTTPException(status_code=500, detail="Failed to get anomaly detection")

@router.get("/ml/insights")
async def get_market_insights() -> Dict[str, Any]:
    """Get AI-powered market insights and recommendations"""
    try:
        ml_service = get_ml_insights_service()
        
        if not ml_service:
            raise HTTPException(status_code=503, detail="ML Insights service not running")
        
        # Get current yield data
        yield_aggregator = YieldAggregator()
        current_yields = await yield_aggregator.get_all_yields()
        
        if not current_yields:
            return {
                "message": "No yield data available for insights generation",
                "insights": []
            }
        
        # Generate insights
        insights = await ml_service.generate_market_insights(current_yields)
        
        # Format insights for API response
        formatted_insights = []
        for insight in insights:
            formatted_insights.append({
                "insight_type": insight.insight_type,
                "title": insight.title,
                "description": insight.description,
                "impact_level": insight.impact_level,
                "confidence": insight.confidence,
                "supporting_data": insight.supporting_data,
                "timestamp": insight.timestamp.isoformat(),
                "expiry_date": insight.expiry_date.isoformat() if insight.expiry_date else None
            })
        
        # Calculate summary statistics
        insight_type_distribution = {}
        impact_level_distribution = {}
        
        for insight in insights:
            insight_type_distribution[insight.insight_type] = insight_type_distribution.get(insight.insight_type, 0) + 1
            impact_level_distribution[insight.impact_level] = impact_level_distribution.get(insight.impact_level, 0) + 1
        
        avg_confidence = sum(i.confidence for i in insights) / len(insights) if insights else 0
        
        return {
            "insights": formatted_insights,
            "total_insights": len(insights),
            "summary_statistics": {
                "insight_type_distribution": insight_type_distribution,
                "impact_level_distribution": impact_level_distribution,
                "average_confidence": avg_confidence,
                "high_impact_insights": len([i for i in insights if i.impact_level == "high"]),
                "high_confidence_insights": len([i for i in insights if i.confidence > 0.8])
            },
            "categories": {
                "opportunities": len([i for i in insights if i.insight_type == "opportunity"]),
                "risks": len([i for i in insights if i.insight_type == "risk"]),
                "trends": len([i for i in insights if i.insight_type == "trend"]),
                "correlations": len([i for i in insights if i.insight_type == "correlation"])
            },
            "methodology": "Multi-factor AI analysis with pattern recognition",
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting market insights: {e}")
        raise HTTPException(status_code=500, detail="Failed to get market insights")

@router.get("/ml/predictions/{symbol}")
async def get_symbol_prediction(symbol: str) -> Dict[str, Any]:
    """Get ML predictions for a specific stablecoin symbol"""
    try:
        ml_service = get_ml_insights_service()
        
        if not ml_service:
            raise HTTPException(status_code=503, detail="ML Insights service not running")
        
        # Check if prediction is cached
        if symbol.upper() in ml_service.predictions_cache:
            cached_pred = ml_service.predictions_cache[symbol.upper()]
            
            return {
                "symbol": cached_pred.symbol,
                "current_yield": cached_pred.current_yield,
                "predictions": {
                    "1_day": {
                        "predicted_yield": cached_pred.predicted_yield_1d,
                        "confidence": cached_pred.confidence_1d
                    },
                    "7_day": {
                        "predicted_yield": cached_pred.predicted_yield_7d,
                        "confidence": cached_pred.confidence_7d
                    },
                    "30_day": {
                        "predicted_yield": cached_pred.predicted_yield_30d,
                        "confidence": cached_pred.confidence_30d
                    }
                },
                "trend_direction": cached_pred.trend_direction,
                "prediction_timestamp": cached_pred.prediction_timestamp.isoformat(),
                "data_source": "cached_prediction"
            }
        else:
            return {
                "message": f"No prediction available for symbol {symbol}",
                "symbol": symbol,
                "suggestion": "Run GET /api/ml/predictions to generate predictions for all symbols"
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting symbol prediction: {e}")
        raise HTTPException(status_code=500, detail="Failed to get symbol prediction")

@router.post("/ml/retrain")
async def retrain_models() -> Dict[str, Any]:
    """Retrain ML models with latest data"""
    try:
        ml_service = get_ml_insights_service()
        
        if not ml_service:
            raise HTTPException(status_code=503, detail="ML Insights service not running")
        
        # Reinitialize models (this will retrain with latest data)
        await ml_service.initialize()
        
        return {
            "message": "ML models retrained successfully",
            "models_updated": [
                "yield_predictor",
                "anomaly_detector",
                "risk_predictor",
                "market_segmentation"
            ],
            "retrain_timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retraining models: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrain models")

@router.get("/ml/model-performance")
async def get_model_performance() -> Dict[str, Any]:
    """Get ML model performance metrics and statistics"""
    try:
        ml_service = get_ml_insights_service()
        
        if not ml_service:
            raise HTTPException(status_code=503, detail="ML Insights service not running")
        
        # Get model performance from saved metrics
        import joblib
        from pathlib import Path
        
        models_dir = Path("/app/data/ml_models")
        performance_metrics = {}
        
        # Try to load performance metrics for each model
        model_files = {
            "yield_predictor": "yield_predictor.pkl",
            "risk_predictor": "risk_predictor.pkl"
        }
        
        for model_name, filename in model_files.items():
            model_path = models_dir / filename
            if model_path.exists():
                try:
                    model_data = joblib.load(model_path)
                    if 'metrics' in model_data:
                        performance_metrics[model_name] = model_data['metrics']
                except Exception as e:
                    logger.warning(f"Could not load metrics for {model_name}: {e}")
        
        return {
            "model_performance": performance_metrics,
            "model_status": {
                "yield_predictor": ml_service.yield_predictor is not None,
                "anomaly_detector": ml_service.anomaly_detector is not None,
                "risk_predictor": ml_service.risk_predictor is not None,
                "market_segmentation": ml_service.market_segmentation is not None
            },
            "cache_statistics": {
                "predictions_cached": len(ml_service.predictions_cache),
                "insights_cached": len(ml_service.insights_cache),
                "anomalies_cached": len(ml_service.anomalies_cache)
            },
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting model performance: {e}")
        raise HTTPException(status_code=500, detail="Failed to get model performance")

@router.get("/ml/feature-importance")
async def get_feature_importance() -> Dict[str, Any]:
    """Get feature importance from trained ML models"""
    try:
        ml_service = get_ml_insights_service()
        
        if not ml_service:
            raise HTTPException(status_code=503, detail="ML Insights service not running")
        
        feature_importance = {}
        
        # Get feature importance from yield predictor
        if ml_service.yield_predictor is not None and hasattr(ml_service.yield_predictor, 'feature_importances_'):
            feature_names = ['hour', 'day_of_week', 'month', 'ma_7', 'ma_30', 
                           'volatility_7', 'volatility_30', 'trend_7', 'trend_30',
                           'ray', 'risk_penalty', 'confidence_score', 
                           'peg_stability_score', 'liquidity_score']
            
            importances = ml_service.yield_predictor.feature_importances_
            
            feature_importance['yield_predictor'] = [
                {"feature": name, "importance": float(imp)}
                for name, imp in zip(feature_names, importances)
            ]
            
            # Sort by importance
            feature_importance['yield_predictor'].sort(key=lambda x: x['importance'], reverse=True)
        
        # Get feature importance from risk predictor
        if ml_service.risk_predictor is not None and hasattr(ml_service.risk_predictor, 'feature_importances_'):
            risk_feature_names = ['apy', 'ma_7', 'ma_30', 'volatility_7', 'volatility_30',
                                'peg_stability_score', 'liquidity_score']
            
            risk_importances = ml_service.risk_predictor.feature_importances_
            
            feature_importance['risk_predictor'] = [
                {"feature": name, "importance": float(imp)}
                for name, imp in zip(risk_feature_names, risk_importances)
            ]
            
            # Sort by importance
            feature_importance['risk_predictor'].sort(key=lambda x: x['importance'], reverse=True)
        
        return {
            "feature_importance": feature_importance,
            "interpretation": {
                "yield_predictor": "Features ranked by importance for yield prediction",
                "risk_predictor": "Features ranked by importance for risk assessment"
            },
            "methodology": "Random Forest feature importance based on mean decrease in impurity",
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting feature importance: {e}")
        raise HTTPException(status_code=500, detail="Failed to get feature importance")

@router.get("/ml/summary")
async def get_ml_summary() -> Dict[str, Any]:
    """Get comprehensive ML service summary"""
    try:
        ml_service = get_ml_insights_service()
        
        if not ml_service:
            return {
                "message": "ML Insights service not running",
                "service_status": "stopped",
                "capabilities": []
            }
        
        # Get basic status
        status = ml_service.get_ml_status()
        
        # Add recent activity summary
        recent_predictions = len(ml_service.predictions_cache)
        recent_insights = len([i for i in ml_service.insights_cache if (datetime.utcnow() - i.timestamp).days < 1])
        recent_anomalies = len([a for a in ml_service.anomalies_cache if (datetime.utcnow() - a.timestamp).days < 1])
        
        return {
            "service_status": "running" if status["service_initialized"] else "stopped",
            "models_status": status["models_trained"],
            "cache_statistics": status["cache_statistics"],
            "recent_activity": {
                "predictions_available": recent_predictions,
                "insights_generated_24h": recent_insights,
                "anomalies_detected_24h": recent_anomalies
            },
            "capabilities": [
                "Multi-horizon yield prediction (1d, 7d, 30d)",
                "Advanced anomaly detection",
                "AI-powered market insights",
                "Risk prediction modeling",
                "Market sentiment analysis",
                "Portfolio optimization recommendations"
            ],
            "api_endpoints": [
                "GET /api/ml/predictions (Yield predictions)",
                "GET /api/ml/anomalies (Anomaly detection)",
                "GET /api/ml/insights (Market insights)",
                "GET /api/ml/predictions/{symbol} (Symbol-specific predictions)",
                "POST /api/ml/retrain (Retrain models)",
                "GET /api/ml/model-performance (Model metrics)",
                "GET /api/ml/feature-importance (Feature analysis)"
            ],
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting ML summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to get ML summary")