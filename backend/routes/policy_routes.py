"""
Policy Routes
API endpoints for protocol policy information and management
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
import logging
from ..services.protocol_policy_service import ProtocolPolicyService

logger = logging.getLogger(__name__)
router = APIRouter()
policy_service = ProtocolPolicyService()

@router.get("/policy/summary")
async def get_policy_summary() -> Dict[str, Any]:
    """Get summary of current protocol policy configuration"""
    try:
        return policy_service.get_policy_summary()
    except Exception as e:
        logger.error(f"Error getting policy summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to get policy summary")

@router.get("/policy/protocols/{protocol_id}")
async def get_protocol_info(
    protocol_id: str,
    tvl_usd: Optional[float] = Query(default=0, description="Protocol TVL in USD for reputation calculation")
) -> Dict[str, Any]:
    """Get detailed information about a specific protocol"""
    try:
        protocol_info = policy_service.get_protocol_info(protocol_id, tvl_usd)
        
        return {
            "protocol_id": protocol_info.protocol_id,
            "name": protocol_info.name,
            "reputation_score": protocol_info.reputation_score,
            "tier": protocol_info.tier,
            "policy_decision": protocol_info.policy_decision.value,
            "risk_factors": protocol_info.risk_factors,
            "rationale": protocol_info.rationale
        }
    except Exception as e:
        logger.error(f"Error getting protocol info for {protocol_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get protocol info for {protocol_id}")

@router.get("/policy/allowlist")
async def get_allowlist() -> Dict[str, Any]:
    """Get current protocol allowlist"""
    try:
        policy = policy_service.policy
        allowlist = policy.get('allowlist', {})
        
        # Flatten allowlist for easier consumption
        flattened = []
        for tier, protocols in allowlist.items():
            for protocol in protocols:
                flattened.append({
                    **protocol,
                    'tier': tier
                })
        
        return {
            "allowlist": flattened,
            "total_protocols": len(flattened),
            "policy_version": policy.get('version', 'unknown')
        }
    except Exception as e:
        logger.error(f"Error getting allowlist: {e}")
        raise HTTPException(status_code=500, detail="Failed to get allowlist")

@router.get("/policy/denylist")
async def get_denylist() -> Dict[str, Any]:
    """Get current protocol denylist"""
    try:
        policy = policy_service.policy
        denylist = policy.get('denylist', {})
        
        # Flatten denylist for easier consumption
        flattened = []
        for category, protocols in denylist.items():
            for protocol in protocols:
                flattened.append({
                    **protocol,
                    'category': category
                })
        
        return {
            "denylist": flattened,
            "total_protocols": len(flattened),
            "policy_version": policy.get('version', 'unknown')
        }
    except Exception as e:
        logger.error(f"Error getting denylist: {e}")
        raise HTTPException(status_code=500, detail="Failed to get denylist")

@router.get("/policy/reputation/tiers")
async def get_reputation_tiers() -> Dict[str, Any]:
    """Get reputation tier definitions"""
    try:
        policy = policy_service.policy
        tiers = policy.get('reputation_scoring', {}).get('tiers', {})
        
        return {
            "tiers": tiers,
            "scoring_methodology": policy.get('reputation_scoring', {}).get('factors', {}),
            "policy_version": policy.get('version', 'unknown')
        }
    except Exception as e:
        logger.error(f"Error getting reputation tiers: {e}")
        raise HTTPException(status_code=500, detail="Failed to get reputation tiers")

@router.post("/policy/refresh")
async def refresh_policy() -> Dict[str, Any]:
    """Refresh policy configuration from file"""
    try:
        success = policy_service.refresh_policy()
        
        if success:
            return {
                "status": "success",
                "message": "Policy refreshed successfully",
                "summary": policy_service.get_policy_summary()
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to refresh policy")
            
    except Exception as e:
        logger.error(f"Error refreshing policy: {e}")
        raise HTTPException(status_code=500, detail="Failed to refresh policy")

@router.get("/policy/enforcement")
async def get_enforcement_settings() -> Dict[str, Any]:
    """Get current policy enforcement settings"""
    try:
        policy = policy_service.policy
        enforcement = policy.get('enforcement', {})
        
        return {
            "enforcement": enforcement,
            "dynamic_rules": policy.get('dynamic_rules', {}),
            "monitoring": policy.get('monitoring', {}),
            "policy_version": policy.get('version', 'unknown')
        }
    except Exception as e:
        logger.error(f"Error getting enforcement settings: {e}")
        raise HTTPException(status_code=500, detail="Failed to get enforcement settings")