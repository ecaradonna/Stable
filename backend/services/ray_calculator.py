"""
Risk-Adjusted Yield (RAY) Calculator Service
Calculates institutional-grade risk-adjusted yields for StableYield Index composition
"""

import math
import statistics
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class RiskFactorType(Enum):
    PEG_STABILITY = "peg_stability"
    LIQUIDITY_RISK = "liquidity_risk"
    COUNTERPARTY_RISK = "counterparty_risk"
    PROTOCOL_RISK = "protocol_risk"
    TEMPORAL_RISK = "temporal_risk"

@dataclass
class RiskFactors:
    peg_stability_score: float      # [0,1] where 1 = perfect peg
    liquidity_score: float          # [0,1] where 1 = perfect liquidity  
    counterparty_score: float       # [0,1] where 1 = minimal counterparty risk
    protocol_reputation: float      # [0,1] from protocol policy system
    temporal_stability: float       # [0,1] where 1 = perfectly stable over time
    
@dataclass
class RAYResult:
    base_apy: float                 # Original base APY (excluding rewards)
    risk_adjusted_yield: float      # Final RAY after all adjustments
    risk_penalty: float             # Total risk penalty applied
    risk_factors: RiskFactors       # Individual risk factor scores
    confidence_score: float         # Confidence in the RAY calculation
    breakdown: Dict[str, float]     # Detailed breakdown of adjustments
    metadata: Dict[str, Any]        # Calculation metadata

class RAYCalculator:
    def __init__(self):
        self.config = self._load_default_config()
        self.peg_data_cache = {}
        self.liquidity_cache = {}
        
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default RAY calculation configuration"""
        return {
            "base_apy_preference": {
                "prefer_base_over_total": True,
                "max_reward_inclusion_ratio": 0.20,  # Max 20% of yield from rewards
                "sustainable_reward_threshold": 2.0,  # 2x base APY max for rewards
                "exclude_governance_tokens": True     # Exclude governance token rewards
            },
            "risk_penalties": {
                "peg_stability": {
                    "max_penalty": 0.50,        # Max 50% penalty for peg risk
                    "deviation_threshold": 0.005, # 0.5% deviation triggers penalty
                    "severe_deviation": 0.02,    # 2% deviation = severe penalty
                    "penalty_curve": "exponential" # exponential, linear, quadratic
                },
                "liquidity_risk": {
                    "max_penalty": 0.40,        # Max 40% penalty for liquidity risk
                    "min_tvl_threshold": 10_000_000,  # $10M minimum
                    "institutional_threshold": 100_000_000, # $100M institutional
                    "depth_requirement": 0.05,  # 5% depth requirement
                    "penalty_curve": "logarithmic"
                },
                "counterparty_risk": {
                    "max_penalty": 0.60,        # Max 60% penalty for counterparty risk
                    "min_reputation": 0.70,     # 0.70 minimum reputation
                    "institutional_reputation": 0.85, # 0.85 for institutional
                    "exploit_penalty": 0.30,    # 30% penalty for exploits
                    "penalty_curve": "linear"
                },
                "protocol_risk": {
                    "max_penalty": 0.35,        # Max 35% penalty for protocol risk
                    "new_protocol_penalty": 0.20, # 20% penalty for new protocols
                    "unaudited_penalty": 0.15,  # 15% penalty for unaudited
                    "beta_penalty": 0.10,       # 10% penalty for beta versions
                    "penalty_curve": "step"     # step, linear, exponential
                },
                "temporal_risk": {
                    "max_penalty": 0.25,        # Max 25% penalty for temporal instability
                    "volatility_threshold": 0.20, # 20% volatility threshold
                    "recent_spike_penalty": 0.15, # 15% penalty for recent spikes
                    "trend_analysis_days": 30,   # 30-day trend analysis
                    "penalty_curve": "quadratic"
                }
            },
            "aggregation_weights": {
                "equal_risk_weighting": False,  # Use TVL-based weighting
                "tvl_cap_percentage": 0.30,     # Cap single asset at 30% of index
                "top_3_asset_cap": 0.70,        # Top 3 assets max 70% of index
                "min_weight_threshold": 0.01,   # 1% minimum weight for inclusion
                "rebalancing_frequency": "daily" # daily, weekly, monthly
            },
            "calculation_methodology": {
                "compound_penalties": True,      # Compound vs additive penalties
                "confidence_weighting": True,    # Weight by confidence scores
                "outlier_exclusion": True,       # Exclude statistical outliers
                "temporal_smoothing": True,      # Apply temporal smoothing
                "stress_testing": True           # Apply stress test scenarios
            }
        }
    
    def calculate_ray(self, 
                     yield_data: Dict[str, Any], 
                     market_context: Optional[List[Dict[str, Any]]] = None) -> RAYResult:
        """
        Calculate Risk-Adjusted Yield for a single yield data point
        """
        
        # Step 1: Extract base APY (prefer base over total)
        base_apy = self._extract_base_apy(yield_data)
        
        # Step 2: Calculate individual risk factors
        risk_factors = self._calculate_risk_factors(yield_data, market_context)
        
        # Step 3: Calculate risk penalties
        risk_penalty, penalty_breakdown = self._calculate_risk_penalties(risk_factors)
        
        # Step 4: Apply risk adjustment
        risk_adjusted_yield = base_apy * (1 - risk_penalty)
        
        # Step 5: Calculate confidence score
        confidence_score = self._calculate_ray_confidence(risk_factors, yield_data)
        
        # Step 6: Create detailed breakdown
        breakdown = {
            "base_apy": base_apy,
            "peg_penalty": penalty_breakdown.get("peg_stability", 0.0),
            "liquidity_penalty": penalty_breakdown.get("liquidity_risk", 0.0),
            "counterparty_penalty": penalty_breakdown.get("counterparty_risk", 0.0),
            "protocol_penalty": penalty_breakdown.get("protocol_risk", 0.0),
            "temporal_penalty": penalty_breakdown.get("temporal_risk", 0.0),
            "total_penalty": risk_penalty,
            "final_ray": risk_adjusted_yield
        }
        
        # Step 7: Create metadata
        metadata = {
            "calculation_timestamp": datetime.utcnow().isoformat(),
            "methodology_version": "1.0.0",
            "market_context_size": len(market_context) if market_context else 0,
            "excluded_rewards": self._get_excluded_rewards(yield_data),
            "calculation_method": "compound_penalties" if self.config["calculation_methodology"]["compound_penalties"] else "additive_penalties"
        }
        
        return RAYResult(
            base_apy=base_apy,
            risk_adjusted_yield=risk_adjusted_yield,
            risk_penalty=risk_penalty,
            risk_factors=risk_factors,
            confidence_score=confidence_score,
            breakdown=breakdown,
            metadata=metadata
        )
    
    def _extract_base_apy(self, yield_data: Dict[str, Any]) -> float:
        """Extract base APY, preferring base over total APY"""
        config = self.config["base_apy_preference"]
        
        # Get available APY data
        total_apy = float(yield_data.get('currentYield', yield_data.get('apy', 0)))
        
        # Check for sanitization metadata that might have base APY
        sanitization = yield_data.get('metadata', {}).get('sanitization', {})
        if sanitization:
            base_apy_from_sanitization = sanitization.get('original_apy')
            if base_apy_from_sanitization:
                total_apy = float(base_apy_from_sanitization)
        
        # Try to extract base vs reward APY if available
        base_apy = yield_data.get('apy_base', yield_data.get('baseAPY'))
        reward_apy = yield_data.get('apy_reward', yield_data.get('rewardAPY'))
        
        if base_apy is not None and config["prefer_base_over_total"]:
            base_apy = float(base_apy)
            
            # Include limited rewards if they're sustainable
            if reward_apy is not None:
                reward_apy = float(reward_apy)
                
                # Check if rewards are sustainable
                if base_apy > 0 and reward_apy / base_apy <= config["sustainable_reward_threshold"]:
                    # Include limited portion of rewards
                    max_reward_inclusion = base_apy * config["max_reward_inclusion_ratio"]
                    included_rewards = min(reward_apy, max_reward_inclusion)
                    return base_apy + included_rewards
            
            return base_apy
        
        # Use total APY as fallback
        return total_apy
    
    def _calculate_risk_factors(self, 
                               yield_data: Dict[str, Any], 
                               market_context: Optional[List[Dict[str, Any]]]) -> RiskFactors:
        """Calculate individual risk factor scores"""
        
        # Peg Stability Score
        peg_stability_score = self._calculate_peg_stability(yield_data)
        
        # Liquidity Score  
        liquidity_score = self._calculate_liquidity_score(yield_data)
        
        # Counterparty Score (from protocol reputation)
        counterparty_score = self._calculate_counterparty_score(yield_data)
        
        # Protocol Reputation (from policy system)
        protocol_reputation = self._get_protocol_reputation(yield_data)
        
        # Temporal Stability
        temporal_stability = self._calculate_temporal_stability(yield_data, market_context)
        
        return RiskFactors(
            peg_stability_score=peg_stability_score,
            liquidity_score=liquidity_score,
            counterparty_score=counterparty_score,
            protocol_reputation=protocol_reputation,
            temporal_stability=temporal_stability
        )
    
    def _calculate_peg_stability(self, yield_data: Dict[str, Any]) -> float:
        """Calculate peg stability score for stablecoin"""
        stablecoin = yield_data.get('stablecoin', yield_data.get('canonical_stablecoin_id', 'UNKNOWN'))
        
        # This would integrate with real peg data in production
        # For now, use stablecoin-specific estimates based on historical performance
        peg_scores = {
            'USDT': 0.92,   # Generally stable but occasional depegs
            'USDC': 0.96,   # Very stable, regulated
            'DAI': 0.88,    # Generally stable but more volatile than centralized
            'TUSD': 0.90,   # Stable but smaller scale
            'PYUSD': 0.85,  # Newer, less track record
            'FRAX': 0.82,   # Algorithmic component adds risk
            'USDP': 0.91    # Paxos-backed, stable
        }
        
        base_score = peg_scores.get(stablecoin.upper(), 0.75)  # Default 0.75 for unknown
        
        # Adjust based on protocol (some protocols have better peg maintenance)
        protocol = yield_data.get('canonical_protocol_id', yield_data.get('source', '')).lower()
        
        # Curve pools generally have better peg stability
        if 'curve' in protocol:
            base_score = min(1.0, base_score + 0.03)
        # Uniswap V3 can have wider spreads
        elif 'uniswap' in protocol:
            base_score = max(0.0, base_score - 0.02)
        
        return base_score
    
    def _calculate_liquidity_score(self, yield_data: Dict[str, Any]) -> float:
        """Calculate liquidity risk score"""
        # Get TVL from various possible sources
        tvl_usd = 0.0
        
        # Check liquidity metrics first
        liquidity_metrics = yield_data.get('metadata', {}).get('liquidity_metrics', {})
        if liquidity_metrics:
            tvl_usd = liquidity_metrics.get('tvl_usd', 0.0)
        else:
            # Fallback to other TVL sources
            tvl_sources = ['tvl', 'tvlUsd', 'totalValueLocked']
            for source in tvl_sources:
                if source in yield_data:
                    try:
                        tvl_value = yield_data[source]
                        if isinstance(tvl_value, str):
                            # Parse liquidity strings like "$89.2B"
                            tvl_value = tvl_value.replace('$', '').replace(',', '')
                            if 'B' in tvl_value:
                                tvl_usd = float(tvl_value.replace('B', '')) * 1_000_000_000
                            elif 'M' in tvl_value:
                                tvl_usd = float(tvl_value.replace('M', '')) * 1_000_000
                            elif 'K' in tvl_value:
                                tvl_usd = float(tvl_value.replace('K', '')) * 1_000
                            else:
                                tvl_usd = float(tvl_value)
                        else:
                            tvl_usd = float(tvl_value)
                        break
                    except:
                        continue
        
        config = self.config["risk_penalties"]["liquidity_risk"]
        
        # Calculate liquidity score based on TVL
        if tvl_usd >= config["institutional_threshold"]:
            return 1.0  # Perfect liquidity score
        elif tvl_usd >= config["min_tvl_threshold"]:
            # Linear interpolation between min and institutional threshold
            ratio = (tvl_usd - config["min_tvl_threshold"]) / (config["institutional_threshold"] - config["min_tvl_threshold"])
            return 0.60 + (0.40 * ratio)  # Scale from 0.60 to 1.0
        else:
            # Below minimum threshold - low liquidity score
            if tvl_usd > 0:
                ratio = tvl_usd / config["min_tvl_threshold"]
                return 0.30 + (0.30 * ratio)  # Scale from 0.30 to 0.60
            else:
                return 0.10  # Very low liquidity
    
    def _calculate_counterparty_score(self, yield_data: Dict[str, Any]) -> float:
        """Calculate counterparty risk score"""
        # Get source type (DeFi vs CeFi)
        source_type = yield_data.get('sourceType', 'Unknown')
        
        # DeFi protocols generally have lower counterparty risk
        if source_type == 'DeFi':
            base_score = 0.85
        elif source_type == 'CeFi':
            base_score = 0.70  # Higher counterparty risk
        else:
            base_score = 0.75  # Unknown source type
        
        # Adjust based on protocol reputation if available
        protocol_info = yield_data.get('metadata', {}).get('protocol_info', {})
        if protocol_info:
            reputation = protocol_info.get('reputation_score', 0.75)
            # Blend protocol reputation with base counterparty score
            base_score = (base_score * 0.7) + (reputation * 0.3)
        
        return min(1.0, max(0.0, base_score))
    
    def _get_protocol_reputation(self, yield_data: Dict[str, Any]) -> float:
        """Get protocol reputation score from policy system"""
        # Check if protocol info is already in metadata
        protocol_info = yield_data.get('metadata', {}).get('protocol_info', {})
        if protocol_info:
            return protocol_info.get('reputation_score', 0.75)
            
        # Fallback reputation scores for known protocols
        protocol = yield_data.get('canonical_protocol_id', yield_data.get('source', '')).lower()
        
        reputation_scores = {
            'aave_v3': 0.95,
            'compound_v3': 0.90,
            'curve': 0.85,
            'uniswap_v3': 0.80,
            'convex': 0.78,
            'morpho': 0.83,
            'frax_finance': 0.75,
            'yearn': 0.70,
            'binance_earn': 0.75,
            'kraken_staking': 0.73
        }
        
        return reputation_scores.get(protocol, 0.60)  # Default for unknown protocols
    
    def _calculate_temporal_stability(self, 
                                    yield_data: Dict[str, Any], 
                                    market_context: Optional[List[Dict[str, Any]]]) -> float:
        """Calculate temporal stability score"""
        # This would use actual historical data in production
        # For now, estimate based on yield characteristics
        
        current_yield = float(yield_data.get('currentYield', 0))
        
        # Use market context to estimate volatility
        if market_context and len(market_context) > 1:
            context_yields = [float(y.get('currentYield', 0)) for y in market_context]
            if context_yields:
                median_yield = statistics.median(context_yields)
                
                # Calculate deviation from median as stability proxy
                if median_yield > 0:
                    deviation_ratio = abs(current_yield - median_yield) / median_yield
                    
                    # Convert deviation to stability score
                    if deviation_ratio <= 0.10:  # Within 10% of median
                        return 0.95
                    elif deviation_ratio <= 0.25:  # Within 25% of median
                        return 0.85 - (deviation_ratio * 1.0)
                    else:
                        return max(0.30, 0.85 - (deviation_ratio * 2.0))
        
        # Fallback based on yield level (very high yields are often unstable)
        if current_yield > 50:
            return 0.30  # Very high yields are typically unstable
        elif current_yield > 25:
            return 0.50
        elif current_yield > 15:
            return 0.70
        else:
            return 0.85  # Reasonable yields are more stable
    
    def _calculate_risk_penalties(self, risk_factors: RiskFactors) -> Tuple[float, Dict[str, float]]:
        """Calculate risk penalties based on risk factors"""
        config = self.config["risk_penalties"]
        penalties = {}
        
        # Peg stability penalty
        peg_penalty = self._apply_penalty_curve(
            1 - risk_factors.peg_stability_score,
            config["peg_stability"]["max_penalty"],
            config["peg_stability"]["penalty_curve"]
        )
        penalties["peg_stability"] = peg_penalty
        
        # Liquidity penalty  
        liquidity_penalty = self._apply_penalty_curve(
            1 - risk_factors.liquidity_score,
            config["liquidity_risk"]["max_penalty"],
            config["liquidity_risk"]["penalty_curve"]
        )
        penalties["liquidity_risk"] = liquidity_penalty
        
        # Counterparty penalty
        counterparty_penalty = self._apply_penalty_curve(
            1 - risk_factors.counterparty_score,
            config["counterparty_risk"]["max_penalty"],
            config["counterparty_risk"]["penalty_curve"]
        )
        penalties["counterparty_risk"] = counterparty_penalty
        
        # Protocol penalty
        protocol_penalty = self._apply_penalty_curve(
            1 - risk_factors.protocol_reputation,
            config["protocol_risk"]["max_penalty"],
            config["protocol_risk"]["penalty_curve"]
        )
        penalties["protocol_risk"] = protocol_penalty
        
        # Temporal penalty
        temporal_penalty = self._apply_penalty_curve(
            1 - risk_factors.temporal_stability,
            config["temporal_risk"]["max_penalty"],
            config["temporal_risk"]["penalty_curve"]
        )
        penalties["temporal_risk"] = temporal_penalty
        
        # Combine penalties (compound or additive)
        if self.config["calculation_methodology"]["compound_penalties"]:
            # Compound penalties: (1 - p1) * (1 - p2) * ... = 1 - total_penalty
            total_penalty = 1.0
            for penalty in penalties.values():
                total_penalty *= (1 - penalty)
            total_penalty = 1 - total_penalty
        else:
            # Additive penalties (capped at 1.0)
            total_penalty = min(1.0, sum(penalties.values()))
        
        return total_penalty, penalties
    
    def _apply_penalty_curve(self, risk_factor: float, max_penalty: float, curve_type: str) -> float:
        """Apply penalty curve transformation"""
        if risk_factor <= 0:
            return 0.0
        if risk_factor >= 1:
            return max_penalty
        
        if curve_type == "linear":
            return risk_factor * max_penalty
        elif curve_type == "exponential":
            return max_penalty * (1 - math.exp(-3 * risk_factor))
        elif curve_type == "quadratic":
            return max_penalty * (risk_factor ** 2)
        elif curve_type == "logarithmic":
            return max_penalty * (math.log(1 + risk_factor) / math.log(2))
        elif curve_type == "step":
            if risk_factor < 0.3:
                return 0.0
            elif risk_factor < 0.7:
                return max_penalty * 0.5
            else:
                return max_penalty
        else:
            return risk_factor * max_penalty  # Default to linear
    
    def _calculate_ray_confidence(self, risk_factors: RiskFactors, yield_data: Dict[str, Any]) -> float:
        """Calculate confidence score for RAY calculation"""
        
        # Base confidence
        confidence = 0.80
        
        # Factor in individual risk factor confidence
        risk_scores = [
            risk_factors.peg_stability_score,
            risk_factors.liquidity_score, 
            risk_factors.counterparty_score,
            risk_factors.protocol_reputation,
            risk_factors.temporal_stability
        ]
        
        # Lower confidence if any risk factors are very low
        min_risk_score = min(risk_scores)
        if min_risk_score < 0.30:
            confidence -= 0.30
        elif min_risk_score < 0.50:
            confidence -= 0.15
        
        # Factor in sanitization confidence if available
        sanitization = yield_data.get('metadata', {}).get('sanitization', {})
        if sanitization:
            sanitization_confidence = sanitization.get('confidence_score', 0.80)
            confidence = (confidence * 0.7) + (sanitization_confidence * 0.3)
        
        # Bonus for high-quality data sources
        if risk_factors.protocol_reputation > 0.90:
            confidence += 0.05
        
        return max(0.0, min(1.0, confidence))
    
    def _get_excluded_rewards(self, yield_data: Dict[str, Any]) -> List[str]:
        """Get list of excluded reward types"""
        excluded = []
        
        # Check if governance tokens are excluded
        if self.config["base_apy_preference"]["exclude_governance_tokens"]:
            # This would check actual reward token types in production
            reward_apy = yield_data.get('apy_reward', yield_data.get('rewardAPY'))
            if reward_apy and float(reward_apy) > 0:
                excluded.append("governance_tokens")
        
        return excluded
    
    def calculate_ray_batch(self, yields: List[Dict[str, Any]]) -> List[RAYResult]:
        """Calculate RAY for a batch of yields with market context"""
        logger.info(f"Calculating RAY for batch of {len(yields)} yields")
        
        results = []
        for i, yield_data in enumerate(yields):
            # Use other yields as market context
            market_context = yields[:i] + yields[i+1:]
            
            result = self.calculate_ray(yield_data, market_context)
            results.append(result)
        
        # Log summary
        avg_ray = statistics.mean([r.risk_adjusted_yield for r in results])
        avg_penalty = statistics.mean([r.risk_penalty for r in results])
        avg_confidence = statistics.mean([r.confidence_score for r in results])
        
        logger.info(f"RAY calculation complete: Avg RAY={avg_ray:.2f}%, Avg penalty={avg_penalty:.1%}, Avg confidence={avg_confidence:.2f}")
        
        return results
    
    def get_ray_summary(self) -> Dict[str, Any]:
        """Get summary of RAY calculation configuration"""
        return {
            "methodology_version": "1.0.0",
            "config": self.config,
            "supported_risk_factors": [factor.value for factor in RiskFactorType],
            "penalty_curves": ["linear", "exponential", "quadratic", "logarithmic", "step"],
            "last_updated": datetime.utcnow().isoformat()
        }