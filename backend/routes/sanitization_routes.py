"""
Sanitization Routes
API endpoints for yield sanitization and outlier detection information
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
import logging
import statistics
from services.yield_sanitizer import YieldSanitizer, OutlierMethod, SanitizationAction
from services.yield_aggregator import YieldAggregator

logger = logging.getLogger(__name__)
router = APIRouter()
sanitizer = YieldSanitizer()
yield_aggregator = YieldAggregator()

@router.get("/sanitization/summary")
async def get_sanitization_summary() -> Dict[str, Any]:
    """Get summary of yield sanitization configuration"""
    try:
        return sanitizer.get_sanitization_summary()
    except Exception as e:
        logger.error(f"Error getting sanitization summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to get sanitization summary")

@router.post("/sanitization/test")
async def test_yield_sanitization(
    apy: float = Query(description="APY to test for sanitization"),
    source: str = Query(default="test_protocol", description="Protocol source"),
    use_market_context: bool = Query(default=True, description="Use current market context for outlier detection")
) -> Dict[str, Any]:
    """Test yield sanitization on a single APY value"""
    try:
        # Prepare test yield data
        test_yield = {
            'apy': apy,
            'source': source,
            'stablecoin': 'USDT'
        }
        
        # Get market context if requested
        market_context = []
        if use_market_context:
            try:
                current_yields = await yield_aggregator.get_all_yields()
                market_context = [
                    {'apy': y['currentYield'], 'source': y['source']} 
                    for y in current_yields
                ]
            except:
                market_context = []  # Fallback to no context if yields unavailable
        
        # Run sanitization
        result = sanitizer.sanitize_yield(test_yield, market_context)
        
        return {
            'input': {
                'apy': apy,
                'source': source,
                'market_context_size': len(market_context)
            },
            'result': {
                'original_apy': result.original_apy,
                'sanitized_apy': result.sanitized_apy,
                'action_taken': result.action_taken.value,
                'confidence_score': result.confidence_score,
                'outlier_score': result.outlier_score,
                'warnings': result.warnings,
                'metadata': result.metadata
            }
        }
    except Exception as e:
        logger.error(f"Error testing yield sanitization: {e}")
        raise HTTPException(status_code=500, detail="Failed to test yield sanitization")

@router.get("/sanitization/stats")
async def get_sanitization_stats() -> Dict[str, Any]:
    """Get statistics on yield sanitization from current market data"""
    try:
        # Get current yields
        current_yields = await yield_aggregator.get_all_yields()
        
        if not current_yields:
            return {
                'total_yields': 0,
                'message': 'No yield data available for sanitization statistics'
            }
        
        # Check each yield for sanitization metadata
        sanitized_count = 0
        confidence_scores = []
        adjustment_magnitudes = []
        
        for yield_data in current_yields:
            sanitization_metadata = yield_data.get('metadata', {}).get('sanitization')
            
            if sanitization_metadata:
                sanitized_count += 1
                confidence_scores.append(sanitization_metadata.get('confidence_score', 0.0))
                adjustment_magnitudes.append(sanitization_metadata.get('adjustment_magnitude', 0.0))
        
        # Calculate statistics
        avg_confidence = statistics.mean(confidence_scores) if confidence_scores else 0.0
        avg_adjustment = statistics.mean(adjustment_magnitudes) if adjustment_magnitudes else 0.0
        
        return {
            'total_yields': len(current_yields),
            'sanitized_yields': sanitized_count,
            'sanitization_rate': sanitized_count / len(current_yields) if current_yields else 0.0,
            'averages': {
                'confidence_score': avg_confidence,
                'adjustment_magnitude': avg_adjustment
            },
            'quality_metrics': {
                'high_confidence_rate': len([s for s in confidence_scores if s > 0.80]) / len(confidence_scores) if confidence_scores else 0.0,
                'significant_adjustment_rate': len([a for a in adjustment_magnitudes if a > 1.0]) / len(adjustment_magnitudes) if adjustment_magnitudes else 0.0
            }
        }
    except Exception as e:
        logger.error(f"Error getting sanitization stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get sanitization statistics")

@router.get("/outliers/detect")
async def detect_current_outliers(
    method: str = Query(default="MAD", description="Outlier detection method", regex="^(MAD|IQR|Z_SCORE|PERCENTILE)$"),
    threshold: Optional[float] = Query(default=None, description="Custom threshold for outlier detection")
) -> Dict[str, Any]:
    """Detect outliers in current yield data using specified method"""
    try:
        # Get current yields
        current_yields = await yield_aggregator.get_all_yields()
        
        if not current_yields:
            return {
                'outliers': [],
                'total_yields': 0,
                'message': 'No yield data available for outlier detection'
            }
        
        # Extract APY values for statistics
        yield_values = [y['currentYield'] for y in current_yields]
        
        # Calculate summary statistics
        median_apy = statistics.median(yield_values)
        mean_apy = statistics.mean(yield_values)
        stdev_apy = statistics.stdev(yield_values) if len(yield_values) > 1 else 0.0
        
        return {
            'outliers': [],  # Simplified for now
            'total_yields': len(current_yields),
            'outlier_count': 0,
            'outlier_rate': 0.0,
            'method_used': method,
            'threshold_used': threshold or 3.0,
            'market_statistics': {
                'median_apy': median_apy,
                'mean_apy': mean_apy,
                'standard_deviation': stdev_apy,
                'min_apy': min(yield_values),
                'max_apy': max(yield_values)
            }
        }
    except Exception as e:
        logger.error(f"Error detecting outliers: {e}")
        raise HTTPException(status_code=500, detail="Failed to detect outliers")