"""
Trend analysis for pegcheck historical data
"""

import asyncio
import statistics
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

@dataclass
class TrendAnalysis:
    """Results of trend analysis for a symbol"""
    symbol: str
    analysis_period_hours: int
    data_points: int
    
    # Price trends
    avg_price: float
    min_price: float
    max_price: float
    price_volatility: float
    
    # Peg deviation trends
    avg_deviation_bps: float
    max_deviation_bps: float
    deviation_episodes: int  # Number of times it went above warning threshold
    depeg_episodes: int     # Number of times it went above depeg threshold
    
    # Stability metrics
    time_in_normal: float    # Percentage of time in normal status
    time_in_warning: float   # Percentage of time in warning status
    time_in_depeg: float     # Percentage of time in depeg status
    
    # Trend direction
    price_trend: str         # "stable", "upward", "downward", "volatile"
    deviation_trend: str     # "improving", "stable", "deteriorating"
    
    # Risk assessment
    risk_score: float        # 0-100, higher = more risky
    stability_grade: str     # "A", "B", "C", "D", "F"

class TrendAnalyzer:
    """Analyzes trends in pegcheck historical data"""
    
    def __init__(self, storage_backend):
        self.storage = storage_backend
    
    async def analyze_symbol_trends(self, symbol: str, hours: int = 168) -> Optional[TrendAnalysis]:
        """Analyze trends for a single symbol over specified time period"""
        try:
            # Get historical data
            history = await self.storage.get_peg_history(symbol, hours)
            
            if len(history) < 10:  # Need minimum data points
                return None
            
            # Extract data
            timestamps, prices, statuses = zip(*history)
            
            # Calculate price statistics
            valid_prices = [p for p in prices if p > 0]
            if not valid_prices:
                return None
            
            avg_price = statistics.mean(valid_prices)
            min_price = min(valid_prices)
            max_price = max(valid_prices)
            price_volatility = statistics.stdev(valid_prices) if len(valid_prices) > 1 else 0
            
            # Calculate deviation statistics
            deviations_bps = [abs(p - 1.0) * 10000 for p in valid_prices]
            avg_deviation_bps = statistics.mean(deviations_bps)
            max_deviation_bps = max(deviations_bps)
            
            # Count episodes
            deviation_episodes = sum(1 for d in deviations_bps if d >= 25)  # Warning threshold
            depeg_episodes = sum(1 for d in deviations_bps if d >= 50)     # Depeg threshold
            
            # Calculate time in each status
            status_counts = {"normal": 0, "warning": 0, "depeg": 0}
            for status in statuses:
                if status in status_counts:
                    status_counts[status] += 1
            
            total_points = len(statuses)
            time_in_normal = (status_counts["normal"] / total_points) * 100
            time_in_warning = (status_counts["warning"] / total_points) * 100
            time_in_depeg = (status_counts["depeg"] / total_points) * 100
            
            # Determine price trend
            if len(valid_prices) >= 5:
                first_half_avg = statistics.mean(valid_prices[:len(valid_prices)//2])
                second_half_avg = statistics.mean(valid_prices[len(valid_prices)//2:])
                price_change_pct = ((second_half_avg - first_half_avg) / first_half_avg) * 100
                
                if abs(price_change_pct) < 0.1:
                    price_trend = "stable"
                elif price_change_pct > 0.5:
                    price_trend = "upward"
                elif price_change_pct < -0.5:
                    price_trend = "downward"
                else:
                    price_trend = "volatile" if price_volatility > 0.01 else "stable"
            else:
                price_trend = "stable"
            
            # Determine deviation trend
            if len(deviations_bps) >= 5:
                first_half_dev = statistics.mean(deviations_bps[:len(deviations_bps)//2])
                second_half_dev = statistics.mean(deviations_bps[len(deviations_bps)//2:])
                
                if second_half_dev < first_half_dev * 0.8:
                    deviation_trend = "improving"
                elif second_half_dev > first_half_dev * 1.2:
                    deviation_trend = "deteriorating" 
                else:
                    deviation_trend = "stable"
            else:
                deviation_trend = "stable"
            
            # Calculate risk score (0-100)
            risk_score = 0
            risk_score += min(avg_deviation_bps * 2, 30)       # Deviation component (0-30)
            risk_score += min(depeg_episodes * 10, 25)        # Depeg episodes (0-25)
            risk_score += min(price_volatility * 1000, 20)    # Volatility component (0-20)
            risk_score += min((100 - time_in_normal) / 4, 25) # Time out of peg (0-25)
            
            # Assign stability grade
            if risk_score < 10:
                stability_grade = "A"
            elif risk_score < 25:
                stability_grade = "B"
            elif risk_score < 50:
                stability_grade = "C"
            elif risk_score < 75:
                stability_grade = "D"
            else:
                stability_grade = "F"
            
            return TrendAnalysis(
                symbol=symbol,
                analysis_period_hours=hours,
                data_points=len(history),
                avg_price=avg_price,
                min_price=min_price,
                max_price=max_price,
                price_volatility=price_volatility,
                avg_deviation_bps=avg_deviation_bps,
                max_deviation_bps=max_deviation_bps,
                deviation_episodes=deviation_episodes,
                depeg_episodes=depeg_episodes,
                time_in_normal=time_in_normal,
                time_in_warning=time_in_warning,
                time_in_depeg=time_in_depeg,
                price_trend=price_trend,
                deviation_trend=deviation_trend,
                risk_score=risk_score,
                stability_grade=stability_grade
            )
            
        except Exception as e:
            print(f"Error analyzing trends for {symbol}: {e}")
            return None
    
    async def analyze_market_trends(self, symbols: List[str], hours: int = 168) -> Dict[str, TrendAnalysis]:
        """Analyze trends for multiple symbols"""
        results = {}
        
        for symbol in symbols:
            analysis = await self.analyze_symbol_trends(symbol, hours)
            if analysis:
                results[symbol] = analysis
        
        return results
    
    async def get_market_stability_report(self, symbols: List[str], hours: int = 168) -> Dict:
        """Generate comprehensive market stability report"""
        analyses = await self.analyze_market_trends(symbols, hours)
        
        if not analyses:
            return {"error": "No data available for analysis"}
        
        # Aggregate statistics
        all_grades = [a.stability_grade for a in analyses.values()]
        all_risk_scores = [a.risk_score for a in analyses.values()]
        all_deviations = [a.avg_deviation_bps for a in analyses.values()]
        
        grade_distribution = {grade: all_grades.count(grade) for grade in "ABCDF"}
        avg_risk_score = statistics.mean(all_risk_scores)
        avg_deviation = statistics.mean(all_deviations)
        
        # Identify problematic coins
        high_risk_coins = [symbol for symbol, analysis in analyses.items() 
                          if analysis.risk_score > 50]
        
        improving_coins = [symbol for symbol, analysis in analyses.items()
                          if analysis.deviation_trend == "improving"]
        
        deteriorating_coins = [symbol for symbol, analysis in analyses.items()
                              if analysis.deviation_trend == "deteriorating"]
        
        return {
            "analysis_period_hours": hours,
            "symbols_analyzed": len(analyses),
            "timestamp": datetime.utcnow().isoformat(),
            
            "market_summary": {
                "avg_risk_score": round(avg_risk_score, 1),
                "avg_deviation_bps": round(avg_deviation, 1),
                "grade_distribution": grade_distribution,
                "market_health": "healthy" if avg_risk_score < 25 else "concerning" if avg_risk_score < 50 else "critical"
            },
            
            "alerts": {
                "high_risk_symbols": high_risk_coins,
                "improving_symbols": improving_coins,
                "deteriorating_symbols": deteriorating_coins
            },
            
            "detailed_analysis": {
                symbol: {
                    "stability_grade": analysis.stability_grade,
                    "risk_score": round(analysis.risk_score, 1),
                    "avg_deviation_bps": round(analysis.avg_deviation_bps, 1),
                    "depeg_episodes": analysis.depeg_episodes,
                    "price_trend": analysis.price_trend,
                    "deviation_trend": analysis.deviation_trend,
                    "time_in_normal": round(analysis.time_in_normal, 1)
                }
                for symbol, analysis in analyses.items()
            }
        }