"""
StableYield Index (SYI) Compositor Service
Composes institutional-grade StableYield Index using Risk-Adjusted Yields with TVL-capped weights
"""

import statistics
import math
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
from .ray_calculator import RAYCalculator, RAYResult

logger = logging.getLogger(__name__)

@dataclass
class SYIConstituent:
    stablecoin: str
    protocol: str
    weight: float
    ray: float
    base_apy: float
    risk_penalty: float
    tvl_usd: float
    confidence_score: float
    metadata: Dict[str, Any]

@dataclass
class SYIComposition:
    index_value: float
    constituent_count: int
    total_weight: float
    constituents: List[SYIConstituent]
    methodology_version: str
    calculation_timestamp: str
    quality_metrics: Dict[str, Any]
    breakdown: Dict[str, Any]

class SYICompositor:
    def __init__(self):
        self.ray_calculator = RAYCalculator()
        self.config = self._load_default_config()
        
    def _load_default_config(self) -> Dict[str, Any]:
        """Load SYI composition configuration"""
        return {
            "weighting_methodology": {
                "primary_method": "tvl_weighted",      # tvl_weighted, equal_weighted, confidence_weighted
                "tvl_cap_single_asset": 0.30,          # 30% max weight for single asset
                "tvl_cap_top_3_assets": 0.70,          # 70% max combined weight for top 3
                "min_weight_threshold": 0.01,          # 1% minimum weight for inclusion
                "weight_smoothing": True,               # Apply temporal weight smoothing
                "rebalancing_threshold": 0.05           # 5% weight change triggers rebalancing
            },
            "inclusion_criteria": {
                "min_confidence_score": 0.60,          # 60% minimum confidence for inclusion
                "min_tvl_usd": 10_000_000,             # $10M minimum TVL
                "max_constituents": 10,                # Maximum 10 constituents
                "min_constituents": 3,                 # Minimum 3 constituents
                "diversification_requirement": True,   # Require protocol diversification
                "max_single_protocol_weight": 0.40     # 40% max weight from single protocol
            },
            "risk_adjustments": {
                "apply_confidence_weighting": True,    # Weight by confidence scores
                "outlier_exclusion": True,             # Exclude statistical outliers
                "stress_testing": True,                # Apply stress test scenarios
                "correlation_adjustment": False,       # Adjust for yield correlations
                "volatility_weighting": False          # Weight by inverse volatility
            },
            "index_calculation": {
                "base_index_value": 1.0000,           # Starting index value
                "calculation_frequency": "1min",       # 1min, 5min, 15min, 1hour
                "precision_decimals": 4,               # 4 decimal places for index
                "minimum_data_freshness": 600,         # 10 minutes max data age
                "fallback_on_insufficient_data": True  # Use previous composition if data insufficient
            }
        }
    
    def compose_syi(self, yield_data: List[Dict[str, Any]]) -> SYIComposition:
        """
        Compose StableYield Index from yield data using RAY methodology
        """
        logger.info(f"Composing SYI from {len(yield_data)} yield sources")
        
        # Step 1: Calculate RAY for all yields
        ray_results = self.ray_calculator.calculate_ray_batch(yield_data)
        
        # Step 2: Apply inclusion criteria and filters
        eligible_constituents = self._apply_inclusion_criteria(yield_data, ray_results)
        
        # Step 3: Calculate weights using TVL-capped methodology
        weighted_constituents = self._calculate_weights(eligible_constituents)
        
        # Step 4: Apply weight caps and diversification requirements
        final_constituents = self._apply_weight_caps(weighted_constituents)
        
        # Step 5: Calculate final index value
        index_value = self._calculate_index_value(final_constituents)
        
        # Step 6: Generate quality metrics and breakdown
        quality_metrics = self._calculate_quality_metrics(final_constituents, ray_results)
        breakdown = self._create_breakdown(final_constituents)
        
        # Step 7: Create final composition
        composition = SYIComposition(
            index_value=index_value,
            constituent_count=len(final_constituents),
            total_weight=sum(c.weight for c in final_constituents),
            constituents=final_constituents,
            methodology_version="2.0.0",  # Enhanced with RAY
            calculation_timestamp=datetime.utcnow().isoformat(),
            quality_metrics=quality_metrics,
            breakdown=breakdown
        )
        
        logger.info(f"SYI composition complete: Index={index_value:.4f}, {len(final_constituents)} constituents, Quality={quality_metrics.get('overall_quality', 0):.2f}")
        
        return composition
    
    def _apply_inclusion_criteria(self, 
                                yield_data: List[Dict[str, Any]], 
                                ray_results: List[RAYResult]) -> List[Tuple[Dict[str, Any], RAYResult]]:
        """Apply inclusion criteria to filter eligible constituents"""
        config = self.config["inclusion_criteria"]
        eligible = []
        
        for yield_item, ray_result in zip(yield_data, ray_results):
            # Check minimum confidence score
            if ray_result.confidence_score < config["min_confidence_score"]:
                logger.debug(f"Excluding {yield_item.get('stablecoin', 'Unknown')} - low confidence: {ray_result.confidence_score:.2f}")
                continue
            
            # Check minimum TVL
            tvl_usd = self._extract_tvl(yield_item)
            if tvl_usd < config["min_tvl_usd"]:
                logger.debug(f"Excluding {yield_item.get('stablecoin', 'Unknown')} - low TVL: ${tvl_usd:,.0f}")
                continue
            
            # Check if RAY is positive and reasonable
            if ray_result.risk_adjusted_yield <= 0 or ray_result.risk_adjusted_yield > 100:
                logger.debug(f"Excluding {yield_item.get('stablecoin', 'Unknown')} - invalid RAY: {ray_result.risk_adjusted_yield:.2f}%")
                continue
            
            eligible.append((yield_item, ray_result))
        
        # Apply maximum constituents limit
        if len(eligible) > config["max_constituents"]:
            # Sort by RAY * confidence and take top N
            eligible.sort(key=lambda x: x[1].risk_adjusted_yield * x[1].confidence_score, reverse=True)
            eligible = eligible[:config["max_constituents"]]
        
        # Check minimum constituents requirement
        if len(eligible) < config["min_constituents"]:
            logger.warning(f"Insufficient eligible constituents: {len(eligible)} < {config['min_constituents']}")
            # Could implement fallback logic here
        
        return eligible
    
    def _calculate_weights(self, eligible_constituents: List[Tuple[Dict[str, Any], RAYResult]]) -> List[SYIConstituent]:
        """Calculate initial weights based on TVL and confidence"""
        config = self.config["weighting_methodology"]
        constituents = []
        
        # Extract data for weight calculation
        tvl_values = []
        confidence_scores = []
        
        for yield_item, ray_result in eligible_constituents:
            tvl_usd = self._extract_tvl(yield_item)
            tvl_values.append(tvl_usd)
            confidence_scores.append(ray_result.confidence_score)
        
        total_tvl = sum(tvl_values)
        
        for (yield_item, ray_result), tvl_usd, confidence in zip(eligible_constituents, tvl_values, confidence_scores):
            # Base weight from TVL
            if config["primary_method"] == "tvl_weighted":
                base_weight = tvl_usd / total_tvl if total_tvl > 0 else 1.0 / len(eligible_constituents)
            elif config["primary_method"] == "equal_weighted":
                base_weight = 1.0 / len(eligible_constituents)
            else:  # confidence_weighted
                total_confidence = sum(confidence_scores)
                base_weight = confidence / total_confidence if total_confidence > 0 else 1.0 / len(eligible_constituents)
            
            # Apply confidence weighting if enabled
            if config.get("apply_confidence_weighting", True) and config["primary_method"] != "confidence_weighted":
                # Blend TVL weight with confidence weight
                confidence_weight = confidence / sum(confidence_scores) if sum(confidence_scores) > 0 else base_weight
                base_weight = (base_weight * 0.7) + (confidence_weight * 0.3)
            
            # Create constituent
            constituent = SYIConstituent(
                stablecoin=yield_item.get('stablecoin', yield_item.get('canonical_stablecoin_id', 'Unknown')),
                protocol=yield_item.get('source', yield_item.get('canonical_protocol_id', 'Unknown')),
                weight=base_weight,
                ray=ray_result.risk_adjusted_yield,
                base_apy=ray_result.base_apy,
                risk_penalty=ray_result.risk_penalty,
                tvl_usd=tvl_usd,
                confidence_score=ray_result.confidence_score,
                metadata={
                    'ray_breakdown': ray_result.breakdown,
                    'risk_factors': {
                        'peg_stability': ray_result.risk_factors.peg_stability_score,
                        'liquidity': ray_result.risk_factors.liquidity_score,
                        'counterparty': ray_result.risk_factors.counterparty_score,
                        'protocol_reputation': ray_result.risk_factors.protocol_reputation,
                        'temporal_stability': ray_result.risk_factors.temporal_stability
                    },
                    'original_yield_data': yield_item
                }
            )
            constituents.append(constituent)
        
        return constituents
    
    def _apply_weight_caps(self, constituents: List[SYIConstituent]) -> List[SYIConstituent]:
        """Apply weight caps and diversification requirements"""
        config = self.config["weighting_methodology"]
        
        # Sort by weight (descending) for capping
        constituents.sort(key=lambda c: c.weight, reverse=True)
        
        # Apply single asset cap
        single_asset_cap = config["tvl_cap_single_asset"]
        for constituent in constituents:
            if constituent.weight > single_asset_cap:
                logger.info(f"Capping {constituent.stablecoin} weight from {constituent.weight:.3f} to {single_asset_cap:.3f}")
                constituent.weight = single_asset_cap
        
        # Apply top-3 assets cap
        top_3_cap = config["tvl_cap_top_3_assets"]
        if len(constituents) >= 3:
            top_3_weight = sum(c.weight for c in constituents[:3])
            if top_3_weight > top_3_cap:
                # Proportionally reduce top 3 weights
                reduction_factor = top_3_cap / top_3_weight
                for i in range(3):
                    constituents[i].weight *= reduction_factor
                    
        # Check protocol diversification
        protocol_weights = {}
        for constituent in constituents:
            protocol = constituent.protocol
            protocol_weights[protocol] = protocol_weights.get(protocol, 0) + constituent.weight
        
        # Apply protocol weight cap
        max_protocol_weight = self.config["inclusion_criteria"]["max_single_protocol_weight"]
        for protocol, total_weight in protocol_weights.items():
            if total_weight > max_protocol_weight:
                # Proportionally reduce weights for this protocol
                reduction_factor = max_protocol_weight / total_weight
                for constituent in constituents:
                    if constituent.protocol == protocol:
                        constituent.weight *= reduction_factor
        
        # Normalize weights to sum to 1.0
        total_weight = sum(c.weight for c in constituents)
        if total_weight > 0:
            for constituent in constituents:
                constituent.weight /= total_weight
        
        # Remove constituents below minimum weight threshold
        min_weight = config["min_weight_threshold"]
        constituents = [c for c in constituents if c.weight >= min_weight]
        
        # Re-normalize after filtering
        total_weight = sum(c.weight for c in constituents)
        if total_weight > 0:
            for constituent in constituents:
                constituent.weight /= total_weight
        
        return constituents
    
    def _calculate_index_value(self, constituents: List[SYIConstituent]) -> float:
        """Calculate the final index value"""
        if not constituents:
            return 0.0
        
        # Weighted average of RAY values
        weighted_ray = sum(c.ray * c.weight for c in constituents)
        
        # Convert to index format (1.0000 + percentage/100)
        # For example, 4.5% weighted RAY becomes 1.0450
        index_value = 1.0 + (weighted_ray / 100.0)
        
        # Apply precision rounding
        precision = self.config["index_calculation"]["precision_decimals"]
        index_value = round(index_value, precision)
        
        return index_value
    
    def _extract_tvl(self, yield_data: Dict[str, Any]) -> float:
        """Extract TVL from yield data"""
        # Try liquidity metrics first
        liquidity_metrics = yield_data.get('metadata', {}).get('liquidity_metrics', {})
        if liquidity_metrics and 'tvl_usd' in liquidity_metrics:
            return float(liquidity_metrics['tvl_usd'])
        
        # Try direct TVL field
        if 'tvl' in yield_data:
            tvl_value = yield_data['tvl']
            if isinstance(tvl_value, (int, float)):
                return float(tvl_value)
        
        # Try to parse liquidity string
        liquidity_str = yield_data.get('liquidity', '0')
        try:
            clean_str = liquidity_str.replace('$', '').replace(',', '')
            if 'B' in clean_str:
                return float(clean_str.replace('B', '')) * 1_000_000_000
            elif 'M' in clean_str:
                return float(clean_str.replace('M', '')) * 1_000_000
            elif 'K' in clean_str:
                return float(clean_str.replace('K', '')) * 1_000
            else:
                return float(clean_str)
        except:
            return 0.0
    
    def _calculate_quality_metrics(self, 
                                 constituents: List[SYIConstituent], 
                                 all_ray_results: List[RAYResult]) -> Dict[str, Any]:
        """Calculate quality metrics for the index composition"""
        if not constituents:
            return {"overall_quality": 0.0}
        
        # Constituent quality metrics
        avg_confidence = statistics.mean([c.confidence_score for c in constituents])
        avg_ray = statistics.mean([c.ray for c in constituents])
        avg_risk_penalty = statistics.mean([c.risk_penalty for c in constituents])
        
        # Diversification metrics
        unique_protocols = len(set(c.protocol for c in constituents))
        unique_stablecoins = len(set(c.stablecoin for c in constituents))
        max_weight = max(c.weight for c in constituents) if constituents else 0
        
        # Weight distribution metrics
        weight_gini = self._calculate_gini_coefficient([c.weight for c in constituents])
        
        # Overall quality score (0-1)
        quality_components = [
            avg_confidence,                    # Confidence quality
            min(1.0, unique_protocols / 5),    # Protocol diversity (max 5)
            min(1.0, unique_stablecoins / 6),  # Stablecoin diversity (max 6)
            1 - min(1.0, max_weight * 2),     # Weight concentration penalty
            1 - weight_gini,                  # Weight distribution quality
            min(1.0, len(constituents) / 8)   # Constituent count quality (max 8)
        ]
        
        overall_quality = statistics.mean(quality_components)
        
        return {
            "overall_quality": overall_quality,
            "avg_confidence": avg_confidence,
            "avg_ray": avg_ray,
            "avg_risk_penalty": avg_risk_penalty,
            "protocol_diversity": unique_protocols,
            "stablecoin_diversity": unique_stablecoins,
            "max_constituent_weight": max_weight,
            "weight_gini_coefficient": weight_gini,
            "total_tvl_usd": sum(c.tvl_usd for c in constituents),
            "methodology_version": "2.0.0"
        }
    
    def _calculate_gini_coefficient(self, weights: List[float]) -> float:
        """Calculate Gini coefficient for weight distribution"""
        if not weights or len(weights) <= 1:
            return 0.0
        
        # Sort weights
        sorted_weights = sorted(weights)
        n = len(weights)
        
        # Calculate Gini coefficient
        cumsum = 0
        for i, weight in enumerate(sorted_weights):
            cumsum += weight * (2 * i - n + 1)
        
        return cumsum / (n * sum(weights))
    
    def _create_breakdown(self, constituents: List[SYIConstituent]) -> Dict[str, Any]:
        """Create detailed breakdown of index composition"""
        if not constituents:
            return {}
        
        # Constituent breakdown
        constituent_breakdown = []
        for constituent in constituents:
            constituent_breakdown.append({
                "stablecoin": constituent.stablecoin,
                "protocol": constituent.protocol,
                "weight": constituent.weight,
                "ray": constituent.ray,
                "base_apy": constituent.base_apy,
                "risk_penalty": constituent.risk_penalty,
                "tvl_usd": constituent.tvl_usd,
                "confidence_score": constituent.confidence_score,
                "contribution_to_index": constituent.ray * constituent.weight
            })
        
        # Risk factor analysis
        risk_factor_summary = {
            "avg_peg_stability": statistics.mean([
                c.metadata['risk_factors']['peg_stability'] for c in constituents
            ]),
            "avg_liquidity_score": statistics.mean([
                c.metadata['risk_factors']['liquidity'] for c in constituents
            ]),
            "avg_counterparty_score": statistics.mean([
                c.metadata['risk_factors']['counterparty'] for c in constituents
            ]),
            "avg_protocol_reputation": statistics.mean([
                c.metadata['risk_factors']['protocol_reputation'] for c in constituents
            ]),
            "avg_temporal_stability": statistics.mean([
                c.metadata['risk_factors']['temporal_stability'] for c in constituents
            ])
        }
        
        # Protocol and stablecoin distribution
        protocol_distribution = {}
        stablecoin_distribution = {}
        
        for constituent in constituents:
            protocol = constituent.protocol
            stablecoin = constituent.stablecoin
            
            if protocol not in protocol_distribution:
                protocol_distribution[protocol] = {"weight": 0, "count": 0}
            protocol_distribution[protocol]["weight"] += constituent.weight
            protocol_distribution[protocol]["count"] += 1
            
            if stablecoin not in stablecoin_distribution:
                stablecoin_distribution[stablecoin] = {"weight": 0, "count": 0}
            stablecoin_distribution[stablecoin]["weight"] += constituent.weight
            stablecoin_distribution[stablecoin]["count"] += 1
        
        return {
            "constituents": constituent_breakdown,
            "risk_factor_summary": risk_factor_summary,
            "protocol_distribution": protocol_distribution,
            "stablecoin_distribution": stablecoin_distribution,
            "weighted_average_ray": sum(c.ray * c.weight for c in constituents),
            "total_risk_penalty": statistics.mean([c.risk_penalty for c in constituents])
        }
    
    def get_syi_methodology(self) -> Dict[str, Any]:
        """Get detailed methodology information"""
        return {
            "methodology_version": "2.0.0",
            "calculation_method": "risk_adjusted_yield_weighted",
            "weighting_scheme": "tvl_capped_with_confidence",
            "risk_adjustment": "multi_factor_ray",
            "rebalancing": "continuous_with_thresholds",
            "config": self.config,
            "last_updated": datetime.utcnow().isoformat()
        }