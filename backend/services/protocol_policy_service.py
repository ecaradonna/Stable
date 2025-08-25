"""
Protocol Policy Service
Enforces allowlist/denylist and reputation scoring for institutional-grade protocols
"""

import yaml
import os
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class PolicyDecision(Enum):
    ALLOW = "allow"
    DENY = "deny" 
    GREYLIST = "greylist"
    UNKNOWN = "unknown"

@dataclass
class ProtocolInfo:
    protocol_id: str
    name: str
    reputation_score: float
    tier: str
    policy_decision: PolicyDecision
    risk_factors: List[str]
    rationale: str

class ProtocolPolicyService:
    def __init__(self):
        self.policy = self._load_policy()
        self.reputation_cache = {}
        self.last_policy_refresh = datetime.utcnow()
        
    def _load_policy(self) -> Dict[str, Any]:
        """Load protocol policy configuration"""
        try:
            policy_path = os.path.join(os.path.dirname(__file__), "../../config/protocol_policy.yml")
            with open(policy_path, 'r') as f:
                policy = yaml.safe_load(f)
                logger.info(f"Loaded protocol policy v{policy.get('version', 'unknown')}")
                return policy
        except Exception as e:
            logger.error(f"Failed to load protocol policy: {e}")
            return self._get_fallback_policy()
    
    def _get_fallback_policy(self) -> Dict[str, Any]:
        """Fallback policy when config file is unavailable"""
        return {
            "enforcement": {"strict_mode": False, "reputation_threshold": 0.5},
            "allowlist": {"tier_1_lending": [], "tier_2_amm": [], "tier_3_specialized": []},
            "denylist": {"high_risk": [], "exploited": [], "regulatory": []},
            "greylist": []
        }
    
    def refresh_policy(self) -> bool:
        """Refresh policy from configuration file"""
        try:
            new_policy = self._load_policy()
            old_version = self.policy.get('version', 'unknown')
            new_version = new_policy.get('version', 'unknown')
            
            if old_version != new_version:
                logger.info(f"Policy updated: {old_version} -> {new_version}")
                
            self.policy = new_policy
            self.reputation_cache.clear()  # Clear cache on policy update
            self.last_policy_refresh = datetime.utcnow()
            return True
        except Exception as e:
            logger.error(f"Failed to refresh policy: {e}")
            return False
    
    def is_protocol_allowed(self, protocol_id: str) -> Tuple[PolicyDecision, str]:
        """Check if protocol is allowed by policy"""
        # Check denylist first (highest priority)
        if self._is_denylisted(protocol_id):
            return PolicyDecision.DENY, "Protocol is explicitly denylisted"
            
        # Check greylist
        if self._is_greylisted(protocol_id):
            return PolicyDecision.GREYLIST, "Protocol is under review"
            
        # Check allowlist
        allowlist_info = self._find_in_allowlist(protocol_id)
        if allowlist_info:
            return PolicyDecision.ALLOW, f"Protocol approved in {allowlist_info['tier']}"
            
        # If strict mode, deny unknown protocols
        if self.policy.get('enforcement', {}).get('strict_mode', False):
            return PolicyDecision.DENY, "Unknown protocol in strict mode"
            
        return PolicyDecision.UNKNOWN, "Protocol not explicitly configured"
    
    def _is_denylisted(self, protocol_id: str) -> bool:
        """Check if protocol is in denylist"""
        denylist = self.policy.get('denylist', {})
        
        for category in ['high_risk', 'exploited', 'regulatory']:
            protocols = denylist.get(category, [])
            for protocol in protocols:
                if protocol.get('protocol_id') == protocol_id:
                    return True
        return False
    
    def _is_greylisted(self, protocol_id: str) -> bool:
        """Check if protocol is in greylist"""
        greylist = self.policy.get('greylist', [])
        for protocol in greylist:
            if protocol.get('protocol_id') == protocol_id:
                return True
        return False
    
    def _find_in_allowlist(self, protocol_id: str) -> Optional[Dict[str, Any]]:
        """Find protocol in allowlist and return its info"""
        allowlist = self.policy.get('allowlist', {})
        
        for tier_name, protocols in allowlist.items():
            for protocol in protocols:
                if protocol.get('protocol_id') == protocol_id:
                    return {**protocol, 'tier': tier_name}
        return None
    
    def calculate_reputation_score(self, protocol_id: str, 
                                 tvl_usd: float = 0,
                                 exploit_history: List[Dict] = None,
                                 audit_info: Dict = None) -> float:
        """Calculate dynamic reputation score"""
        
        # Check cache first
        cache_key = f"{protocol_id}_{int(tvl_usd/1000000)}"  # Cache by protocol and TVL tier
        if cache_key in self.reputation_cache:
            cached_data = self.reputation_cache[cache_key]
            if datetime.utcnow() - cached_data['timestamp'] < timedelta(hours=1):
                return cached_data['score']
        
        # Get base reputation from policy
        allowlist_info = self._find_in_allowlist(protocol_id)
        base_reputation = 0.5  # Default
        
        if allowlist_info:
            base_reputation = allowlist_info.get('reputation_base', 0.5)
        
        # Apply dynamic adjustments
        scoring_config = self.policy.get('reputation_scoring', {})
        factors = scoring_config.get('factors', {})
        final_score = base_reputation
        
        # Exploit penalty
        if exploit_history:
            exploit_config = factors.get('exploit_penalty', {})
            recent_exploits = [e for e in exploit_history 
                             if self._days_since(e.get('date', '2020-01-01')) < 730]  # 2 years
            
            if recent_exploits:
                penalty = exploit_config.get('recent_exploit_penalty', 0.30)
                final_score *= (1 - penalty)
                logger.info(f"Applied exploit penalty to {protocol_id}: -{penalty*100}%")
        
        # TVL longevity bonus/penalty
        if tvl_usd > 0:
            tvl_config = factors.get('tvl_longevity', {})
            if tvl_usd > 100_000_000:  # $100M+ gets bonus
                bonus = 0.05
                final_score = min(1.0, final_score + bonus)
            elif tvl_usd < 10_000_000:  # <$10M gets penalty
                penalty = 0.10
                final_score *= (1 - penalty)
        
        # Ensure bounds [0, 1]
        final_score = max(0.0, min(1.0, final_score))
        
        # Cache the result
        self.reputation_cache[cache_key] = {
            'score': final_score,
            'timestamp': datetime.utcnow()
        }
        
        return final_score
    
    def _days_since(self, date_str: str) -> int:
        """Calculate days since given date"""
        try:
            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return (datetime.utcnow() - date_obj.replace(tzinfo=None)).days
        except:
            return 9999  # Very old date for invalid dates
    
    def get_protocol_info(self, protocol_id: str, tvl_usd: float = 0) -> ProtocolInfo:
        """Get comprehensive protocol information"""
        policy_decision, rationale = self.is_protocol_allowed(protocol_id)
        
        # Calculate reputation score
        reputation_score = self.calculate_reputation_score(protocol_id, tvl_usd)
        
        # Determine tier
        tier = self._get_reputation_tier(reputation_score)
        
        # Get risk factors
        risk_factors = []
        allowlist_info = self._find_in_allowlist(protocol_id)
        if allowlist_info:
            risk_factors = allowlist_info.get('risk_factors', [])
        
        # Get display name
        name = protocol_id.replace('_', ' ').title()
        if allowlist_info:
            name = allowlist_info.get('name', name)
        
        return ProtocolInfo(
            protocol_id=protocol_id,
            name=name,
            reputation_score=reputation_score,
            tier=tier,
            policy_decision=policy_decision,
            risk_factors=risk_factors,
            rationale=rationale
        )
    
    def _get_reputation_tier(self, score: float) -> str:
        """Get reputation tier label from score"""
        tiers = self.policy.get('reputation_scoring', {}).get('tiers', {})
        
        for tier_name, tier_config in tiers.items():
            tier_range = tier_config.get('range', [0, 1])
            if tier_range[0] <= score <= tier_range[1]:
                return tier_config.get('label', tier_name)
        
        return "Unknown"
    
    def filter_pools_by_policy(self, pools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter pools according to protocol policy"""
        filtered_pools = []
        enforcement = self.policy.get('enforcement', {})
        reputation_threshold = enforcement.get('reputation_threshold', 0.70)
        
        stats = {
            'total_pools': len(pools),
            'allowed_pools': 0,
            'denied_pools': 0,
            'below_reputation_threshold': 0,
            'policy_decisions': {}
        }
        
        for pool in pools:
            protocol_id = pool.get('canonical_protocol_id', pool.get('project', '').lower())
            tvl_usd = pool.get('tvl', 0)
            
            # Get protocol policy decision
            protocol_info = self.get_protocol_info(protocol_id, tvl_usd)
            
            # Track policy decisions
            decision = protocol_info.policy_decision.value
            stats['policy_decisions'][decision] = stats['policy_decisions'].get(decision, 0) + 1
            
            # Apply filtering logic
            should_include = False
            
            if protocol_info.policy_decision == PolicyDecision.ALLOW:
                if protocol_info.reputation_score >= reputation_threshold:
                    should_include = True
                    stats['allowed_pools'] += 1
                else:
                    stats['below_reputation_threshold'] += 1
                    logger.debug(f"Pool {pool.get('pool_id')} excluded: reputation {protocol_info.reputation_score:.2f} < {reputation_threshold}")
            
            elif protocol_info.policy_decision == PolicyDecision.GREYLIST:
                # Include greylist protocols but with warning metadata
                if protocol_info.reputation_score >= reputation_threshold:
                    should_include = True
                    stats['allowed_pools'] += 1
                    pool['policy_warning'] = "Protocol under review"
                else:
                    stats['below_reputation_threshold'] += 1
            
            else:  # DENY or UNKNOWN
                stats['denied_pools'] += 1
                logger.debug(f"Pool {pool.get('pool_id')} excluded: {protocol_info.rationale}")
            
            if should_include:
                # Enrich pool with policy information
                pool['protocol_info'] = {
                    'reputation_score': protocol_info.reputation_score,
                    'tier': protocol_info.tier,
                    'risk_factors': protocol_info.risk_factors,
                    'policy_decision': protocol_info.policy_decision.value
                }
                filtered_pools.append(pool)
        
        logger.info(f"Policy filtering results: {stats}")
        return filtered_pools
    
    def get_policy_summary(self) -> Dict[str, Any]:
        """Get summary of current policy configuration"""
        allowlist = self.policy.get('allowlist', {})
        denylist = self.policy.get('denylist', {})
        greylist = self.policy.get('greylist', [])
        
        # Count protocols in each category
        allowlist_count = sum(len(protocols) for protocols in allowlist.values())
        denylist_count = sum(len(protocols) for protocols in denylist.values())
        greylist_count = len(greylist)
        
        return {
            'policy_version': self.policy.get('version', 'unknown'),
            'last_refresh': self.last_policy_refresh.isoformat(),
            'enforcement': self.policy.get('enforcement', {}),
            'protocol_counts': {
                'allowlisted': allowlist_count,
                'denylisted': denylist_count,
                'greylisted': greylist_count
            },
            'reputation_threshold': self.policy.get('enforcement', {}).get('reputation_threshold', 0.70),
            'strict_mode': self.policy.get('enforcement', {}).get('strict_mode', False)
        }