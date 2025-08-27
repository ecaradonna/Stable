"""
Yield Sanitizer Service
Statistical outlier detection and APY cleaning for institutional-grade yield data
"""

import statistics
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
from enum import Enum
import json

logger = logging.getLogger(__name__)

class OutlierMethod(Enum):
    MAD = "median_absolute_deviation"
    IQR = "interquartile_range" 
    Z_SCORE = "z_score"
    PERCENTILE = "percentile_capping"

class SanitizationAction(Enum):
    ACCEPT = "accept"
    CAP = "cap"
    WINSORIZE = "winsorize"
    REJECT = "reject"
    FLAG = "flag"

@dataclass
class YieldSanitizationResult:
    original_apy: float
    sanitized_apy: float
    action_taken: SanitizationAction
    confidence_score: float
    outlier_score: float
    warnings: List[str]
    metadata: Dict[str, Any]

class YieldSanitizer:
    def __init__(self):
        self.config = self._load_default_config()
        self.historical_yields = {}  # Store for temporal analysis
        self.last_cleanup = datetime.utcnow()
        
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default sanitization configuration"""
        return {
            "apy_bounds": {
                "absolute_minimum": 0.0,        # 0% minimum
                "absolute_maximum": 200.0,      # 200% absolute ceiling
                "reasonable_maximum": 50.0,     # 50% reasonable ceiling
                "suspicious_threshold": 25.0,   # 25% triggers review
                "flash_spike_threshold": 100.0  # 100% considered flash spike
            },
            "outlier_detection": {
                "method": "MAD",                # Primary method
                "mad_threshold": 3.0,           # 3 MAD units
                "iqr_multiplier": 1.5,         # 1.5 IQR method
                "z_score_threshold": 3.0,       # 3 standard deviations
                "percentile_lower": 1,          # 1st percentile
                "percentile_upper": 99          # 99th percentile
            },
            "winsorization": {
                "enabled": True,
                "lower_percentile": 5,          # Winsorize at 5th percentile
                "upper_percentile": 95,         # Winsorize at 95th percentile
                "max_adjustment": 0.50          # Max 50% adjustment
            },
            "temporal_analysis": {
                "max_24h_change": 5.0,          # 5x max 24h change
                "max_7d_change": 3.0,           # 3x max 7d change
                "flash_duration_minutes": 30,   # Consider <30min as flash
                "stability_window_hours": 24    # 24h stability window
            },
            "base_vs_reward_apy": {
                "prefer_base": True,            # Prefer base over total APY
                "max_reward_ratio": 5.0,        # Max 5:1 reward:base ratio
                "suspicious_reward_ratio": 10.0, # 10:1 triggers review
                "exclude_unsustainable": True   # Exclude unsustainable rewards
            },
            "supply_borrow_consistency": {
                "check_consistency": True,
                "max_spread_ratio": 0.20,       # 20% max spread
                "inverted_curve_penalty": 0.50  # 50% penalty for inverted curves
            },
            "confidence_scoring": {
                "base_confidence": 0.80,        # 80% base confidence
                "outlier_penalty": 0.30,        # 30% penalty for outliers
                "temporal_bonus": 0.10,         # 10% bonus for stable yields
                "source_reliability_bonus": 0.05 # 5% bonus for reliable sources
            }
        }
    
    def sanitize_yield(self, 
                      yield_data: Dict[str, Any], 
                      market_context: List[Dict[str, Any]] = None) -> YieldSanitizationResult:
        """
        Sanitize a single yield data point using statistical methods
        """
        original_apy = float(yield_data.get('apy', yield_data.get('currentYield', 0)))
        warnings = []
        metadata = {
            'sanitization_timestamp': datetime.utcnow().isoformat(),
            'original_yield_data': yield_data.get('source', 'unknown')
        }
        
        # Step 1: Basic bounds checking
        sanitized_apy, bounds_action, bounds_warnings = self._apply_bounds_checking(original_apy)
        warnings.extend(bounds_warnings)
        
        # Step 2: Outlier detection against market context
        outlier_score = 0.0
        outlier_action = SanitizationAction.ACCEPT
        
        if market_context:
            outlier_score, outlier_action, outlier_warnings = self._detect_outliers(
                sanitized_apy, market_context, yield_data
            )
            warnings.extend(outlier_warnings)
            
            # Apply outlier treatment
            if outlier_action in [SanitizationAction.CAP, SanitizationAction.WINSORIZE]:
                sanitized_apy = self._apply_outlier_treatment(
                    sanitized_apy, market_context, outlier_action
                )
        
        # Step 3: Base vs Reward APY preference
        if self.config['base_vs_reward_apy']['prefer_base']:
            base_apy = yield_data.get('apy_base', yield_data.get('baseAPY'))
            reward_apy = yield_data.get('apy_reward', yield_data.get('rewardAPY'))
            
            if base_apy is not None and reward_apy is not None:
                sanitized_apy, base_warnings = self._prefer_base_apy(
                    sanitized_apy, float(base_apy), float(reward_apy)
                )
                warnings.extend(base_warnings)
        
        # Step 4: Temporal consistency check
        temporal_warnings = self._check_temporal_consistency(
            sanitized_apy, yield_data
        )
        warnings.extend(temporal_warnings)
        
        # Step 5: Supply/Borrow consistency
        if 'borrow_apy' in yield_data or 'borrowAPY' in yield_data:
            consistency_warnings = self._check_supply_borrow_consistency(
                sanitized_apy, yield_data
            )
            warnings.extend(consistency_warnings)
        
        # Step 6: Calculate confidence score
        confidence_score = self._calculate_confidence_score(
            original_apy, sanitized_apy, outlier_score, len(warnings), yield_data
        )
        
        # Step 7: Determine final action
        final_action = self._determine_final_action(
            bounds_action, outlier_action, confidence_score, warnings
        )
        
        # Update metadata
        metadata.update({
            'bounds_checked': True,
            'outlier_score': outlier_score,
            'market_context_size': len(market_context) if market_context else 0,
            'adjustment_magnitude': abs(sanitized_apy - original_apy),
            'warnings_count': len(warnings)
        })
        
        return YieldSanitizationResult(
            original_apy=original_apy,
            sanitized_apy=sanitized_apy,
            action_taken=final_action,
            confidence_score=confidence_score,
            outlier_score=outlier_score,
            warnings=warnings,
            metadata=metadata
        )
    
    def _apply_bounds_checking(self, apy: float) -> Tuple[float, SanitizationAction, List[str]]:
        """Apply basic APY bounds checking"""
        bounds = self.config['apy_bounds']
        warnings = []
        action = SanitizationAction.ACCEPT
        
        # Check absolute bounds
        if apy < bounds['absolute_minimum']:
            warnings.append(f"APY {apy:.2f}% below absolute minimum {bounds['absolute_minimum']:.2f}%")
            apy = bounds['absolute_minimum']
            action = SanitizationAction.CAP
            
        elif apy > bounds['absolute_maximum']:
            warnings.append(f"APY {apy:.2f}% exceeds absolute maximum {bounds['absolute_maximum']:.2f}%")
            apy = bounds['absolute_maximum'] 
            action = SanitizationAction.CAP
            
        # Check reasonable bounds
        elif apy > bounds['reasonable_maximum']:
            warnings.append(f"APY {apy:.2f}% exceeds reasonable maximum {bounds['reasonable_maximum']:.2f}%")
            action = SanitizationAction.FLAG
            
        # Check suspicious threshold
        elif apy > bounds['suspicious_threshold']:
            warnings.append(f"APY {apy:.2f}% above suspicious threshold {bounds['suspicious_threshold']:.2f}%")
            action = SanitizationAction.FLAG
        
        return apy, action, warnings
    
    def _detect_outliers(self, 
                        apy: float, 
                        market_context: List[Dict[str, Any]], 
                        yield_data: Dict[str, Any]) -> Tuple[float, SanitizationAction, List[str]]:
        """Detect outliers using statistical methods"""
        warnings = []
        
        # Extract APY values from market context
        context_apys = [
            float(y.get('apy', y.get('currentYield', 0))) 
            for y in market_context 
            if y.get('apy') or y.get('currentYield')
        ]
        
        if len(context_apys) < 3:
            return 0.0, SanitizationAction.ACCEPT, ["Insufficient market context for outlier detection"]
        
        config = self.config['outlier_detection']
        method = config['method']
        
        if method == "MAD":
            return self._mad_outlier_detection(apy, context_apys, config['mad_threshold'])
        elif method == "IQR":
            return self._iqr_outlier_detection(apy, context_apys, config['iqr_multiplier'])
        elif method == "Z_SCORE":
            return self._z_score_outlier_detection(apy, context_apys, config['z_score_threshold'])
        elif method == "PERCENTILE":
            return self._percentile_outlier_detection(apy, context_apys, config)
        else:
            return 0.0, SanitizationAction.ACCEPT, [f"Unknown outlier detection method: {method}"]
    
    def _mad_outlier_detection(self, apy: float, context_apys: List[float], threshold: float) -> Tuple[float, SanitizationAction, List[str]]:
        """Median Absolute Deviation outlier detection"""
        warnings = []
        
        median = statistics.median(context_apys)
        mad = statistics.median([abs(x - median) for x in context_apys])
        
        if mad == 0:
            mad = 0.01  # Avoid division by zero
        
        outlier_score = abs(apy - median) / mad
        
        if outlier_score > threshold:
            warnings.append(f"MAD outlier detected: score {outlier_score:.2f} > {threshold}")
            
            if outlier_score > threshold * 2:  # Very extreme outlier
                return outlier_score, SanitizationAction.WINSORIZE, warnings
            else:
                return outlier_score, SanitizationAction.FLAG, warnings
        
        return outlier_score, SanitizationAction.ACCEPT, warnings
    
    def _iqr_outlier_detection(self, apy: float, context_apys: List[float], multiplier: float) -> Tuple[float, SanitizationAction, List[str]]:
        """Interquartile Range outlier detection"""
        warnings = []
        context_apys.sort()
        
        q1 = np.percentile(context_apys, 25)
        q3 = np.percentile(context_apys, 75)
        iqr = q3 - q1
        
        lower_bound = q1 - multiplier * iqr
        upper_bound = q3 + multiplier * iqr
        
        if apy < lower_bound or apy > upper_bound:
            outlier_score = max(
                (lower_bound - apy) / iqr if apy < lower_bound else 0,
                (apy - upper_bound) / iqr if apy > upper_bound else 0
            )
            warnings.append(f"IQR outlier detected: APY {apy:.2f}% outside [{lower_bound:.2f}%, {upper_bound:.2f}%]")
            
            if outlier_score > multiplier * 2:
                return outlier_score, SanitizationAction.WINSORIZE, warnings
            else:
                return outlier_score, SanitizationAction.FLAG, warnings
        
        return 0.0, SanitizationAction.ACCEPT, warnings
    
    def _z_score_outlier_detection(self, apy: float, context_apys: List[float], threshold: float) -> Tuple[float, SanitizationAction, List[str]]:
        """Z-Score outlier detection"""
        warnings = []
        
        mean_apy = statistics.mean(context_apys)
        stdev_apy = statistics.stdev(context_apys) if len(context_apys) > 1 else 0.01
        
        z_score = abs(apy - mean_apy) / stdev_apy
        
        if z_score > threshold:
            warnings.append(f"Z-score outlier detected: score {z_score:.2f} > {threshold}")
            
            if z_score > threshold * 1.5:
                return z_score, SanitizationAction.WINSORIZE, warnings
            else:
                return z_score, SanitizationAction.FLAG, warnings
        
        return z_score, SanitizationAction.ACCEPT, warnings
    
    def _percentile_outlier_detection(self, apy: float, context_apys: List[float], config: Dict) -> Tuple[float, SanitizationAction, List[str]]:
        """Percentile-based outlier detection"""
        warnings = []
        
        lower_percentile = np.percentile(context_apys, config['percentile_lower'])
        upper_percentile = np.percentile(context_apys, config['percentile_upper'])
        
        if apy < lower_percentile or apy > upper_percentile:
            range_size = upper_percentile - lower_percentile
            if apy < lower_percentile:
                outlier_score = (lower_percentile - apy) / range_size
            else:
                outlier_score = (apy - upper_percentile) / range_size
                
            warnings.append(f"Percentile outlier detected: APY {apy:.2f}% outside [{lower_percentile:.2f}%, {upper_percentile:.2f}%]")
            
            if outlier_score > 0.5:  # Very extreme
                return outlier_score, SanitizationAction.WINSORIZE, warnings
            else:
                return outlier_score, SanitizationAction.FLAG, warnings
        
        return 0.0, SanitizationAction.ACCEPT, warnings
    
    def _apply_outlier_treatment(self, apy: float, context_apys: List[Dict[str, Any]], action: SanitizationAction) -> float:
        """Apply outlier treatment (capping or winsorization)"""
        apys = [float(y.get('apy', y.get('currentYield', 0))) for y in context_apys]
        
        if action == SanitizationAction.CAP:
            # Cap to reasonable maximum
            reasonable_max = self.config['apy_bounds']['reasonable_maximum']
            return min(apy, reasonable_max)
            
        elif action == SanitizationAction.WINSORIZE:
            # Winsorize to percentiles
            config = self.config['winsorization']
            lower_p = np.percentile(apys, config['lower_percentile'])
            upper_p = np.percentile(apys, config['upper_percentile'])
            
            if apy < lower_p:
                return lower_p
            elif apy > upper_p:
                return upper_p
        
        return apy
    
    def _prefer_base_apy(self, total_apy: float, base_apy: float, reward_apy: float) -> Tuple[float, List[str]]:
        """Prefer base APY over reward-inflated APY"""
        warnings = []
        config = self.config['base_vs_reward_apy']
        
        if reward_apy <= 0:
            return base_apy, warnings
        
        reward_ratio = reward_apy / base_apy if base_apy > 0 else float('inf')
        
        if reward_ratio > config['suspicious_reward_ratio']:
            warnings.append(f"Suspicious reward ratio {reward_ratio:.1f}:1 (reward:base)")
            return base_apy, warnings  # Use only base APY
            
        elif reward_ratio > config['max_reward_ratio']:
            warnings.append(f"High reward ratio {reward_ratio:.1f}:1, capping rewards")
            # Cap the reward component
            capped_reward = base_apy * config['max_reward_ratio']
            return base_apy + capped_reward, warnings
        
        # Use total APY but flag if rewards are unsustainable
        if config['exclude_unsustainable'] and reward_apy > base_apy * 2:
            warnings.append(f"Potentially unsustainable rewards: {reward_apy:.2f}% reward vs {base_apy:.2f}% base")
        
        return total_apy, warnings
    
    def _check_temporal_consistency(self, apy: float, yield_data: Dict[str, Any]) -> List[str]:
        """Check temporal consistency of yields"""
        warnings = []
        config = self.config['temporal_analysis']
        
        # This would check against historical data in production
        # For now, implement basic flash spike detection
        
        source = yield_data.get('source', 'unknown')
        current_time = datetime.utcnow()
        
        # Simulate historical check (in production, query actual historical data)
        if apy > config['flash_duration_minutes']:  # Simple heuristic
            warnings.append(f"Potential flash spike detected for {source}: {apy:.2f}%")
        
        return warnings
    
    def _check_supply_borrow_consistency(self, supply_apy: float, yield_data: Dict[str, Any]) -> List[str]:
        """Check consistency between supply and borrow rates"""
        warnings = []
        config = self.config['supply_borrow_consistency']
        
        borrow_apy = yield_data.get('borrow_apy', yield_data.get('borrowAPY'))
        if borrow_apy is None:
            return warnings
        
        borrow_apy = float(borrow_apy)
        
        # Normal expectation: borrow rate > supply rate
        if borrow_apy < supply_apy:
            warnings.append(f"Inverted yield curve: supply {supply_apy:.2f}% > borrow {borrow_apy:.2f}%")
        
        # Check spread ratio
        if supply_apy > 0:
            spread_ratio = abs(borrow_apy - supply_apy) / supply_apy
            if spread_ratio > config['max_spread_ratio']:
                warnings.append(f"Unusual spread ratio: {spread_ratio:.1%} between supply and borrow")
        
        return warnings
    
    def _calculate_confidence_score(self, 
                                  original_apy: float, 
                                  sanitized_apy: float, 
                                  outlier_score: float, 
                                  warning_count: int,
                                  yield_data: Dict[str, Any]) -> float:
        """Calculate confidence score for sanitized yield"""
        config = self.config['confidence_scoring']
        
        # Start with base confidence
        confidence = config['base_confidence']
        
        # Penalty for outliers
        if outlier_score > 0:
            outlier_penalty = min(outlier_score * config['outlier_penalty'], 0.50)
            confidence -= outlier_penalty
        
        # Penalty for warnings
        warning_penalty = min(warning_count * 0.05, 0.30)
        confidence -= warning_penalty
        
        # Penalty for large adjustments
        adjustment_ratio = abs(sanitized_apy - original_apy) / original_apy if original_apy > 0 else 0
        adjustment_penalty = min(adjustment_ratio * 0.50, 0.40)
        confidence -= adjustment_penalty
        
        # Bonus for reliable sources
        reliable_sources = ['aave_v3', 'compound_v3', 'curve']
        source = yield_data.get('canonical_protocol_id') or yield_data.get('source', '') or ''
        source = source.lower() if source else ''
        if any(reliable in source for reliable in reliable_sources):
            confidence += config['source_reliability_bonus']
        
        # Ensure bounds
        return max(0.0, min(1.0, confidence))
    
    def _determine_final_action(self, 
                              bounds_action: SanitizationAction, 
                              outlier_action: SanitizationAction, 
                              confidence_score: float,
                              warnings: List[str]) -> SanitizationAction:
        """Determine final sanitization action"""
        
        # Reject if confidence is too low
        if confidence_score < 0.30:
            return SanitizationAction.REJECT
        
        # Use the most restrictive action
        actions_hierarchy = {
            SanitizationAction.ACCEPT: 0,
            SanitizationAction.FLAG: 1,
            SanitizationAction.CAP: 2,
            SanitizationAction.WINSORIZE: 3,
            SanitizationAction.REJECT: 4
        }
        
        final_action_level = max(
            actions_hierarchy[bounds_action],
            actions_hierarchy[outlier_action]
        )
        
        # Convert back to action
        for action, level in actions_hierarchy.items():
            if level == final_action_level:
                return action
        
        return SanitizationAction.ACCEPT
    
    def sanitize_yield_batch(self, yields: List[Dict[str, Any]]) -> List[YieldSanitizationResult]:
        """Sanitize a batch of yields with market context"""
        logger.info(f"Sanitizing batch of {len(yields)} yields")
        
        results = []
        for i, yield_data in enumerate(yields):
            # Use other yields as market context (excluding current one)
            market_context = yields[:i] + yields[i+1:]
            
            result = self.sanitize_yield(yield_data, market_context)
            results.append(result)
        
        # Log summary statistics
        accepted = sum(1 for r in results if r.action_taken == SanitizationAction.ACCEPT)
        flagged = sum(1 for r in results if r.action_taken == SanitizationAction.FLAG)  
        capped = sum(1 for r in results if r.action_taken == SanitizationAction.CAP)
        winsorized = sum(1 for r in results if r.action_taken == SanitizationAction.WINSORIZE)
        rejected = sum(1 for r in results if r.action_taken == SanitizationAction.REJECT)
        
        avg_confidence = statistics.mean([r.confidence_score for r in results])
        
        logger.info(f"Sanitization results: {accepted} accepted, {flagged} flagged, {capped} capped, {winsorized} winsorized, {rejected} rejected. Avg confidence: {avg_confidence:.2f}")
        
        return results
    
    def get_sanitization_summary(self) -> Dict[str, Any]:
        """Get summary of sanitization configuration and statistics"""
        return {
            'config': self.config,
            'supported_methods': [method.value for method in OutlierMethod],
            'sanitization_actions': [action.value for action in SanitizationAction],
            'last_cleanup': self.last_cleanup.isoformat(),
            'version': '1.0.0'
        }