"""
Data Validator Service
Validates incoming data against canonical schema definitions
"""

import json
import jsonschema
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import logging
import os

logger = logging.getLogger(__name__)

class DataValidator:
    def __init__(self):
        self.schema = self._load_canonical_schema()
        self.validator = jsonschema.Draft7Validator(self.schema)
        
    def _load_canonical_schema(self) -> Dict[str, Any]:
        """Load canonical entities schema"""
        try:
            schema_path = os.path.join(os.path.dirname(__file__), "../../schema/canonical_entities.json")
            with open(schema_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load canonical schema: {e}")
            return {}
    
    def validate_stablecoin(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate stablecoin entity"""
        errors = []
        
        # Required fields
        required_fields = ['canonical_id', 'name', 'symbol', 'peg_currency', 'mechanism']
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")
        
        # Canonical ID format
        if 'canonical_id' in data:
            if not data['canonical_id'].isupper() or not data['canonical_id'].isalnum():
                errors.append("canonical_id must be uppercase alphanumeric")
        
        # Valid peg currency
        if 'peg_currency' in data:
            valid_currencies = ['USD', 'EUR', 'GBP', 'CHF']
            if data['peg_currency'] not in valid_currencies:
                errors.append(f"Invalid peg_currency: {data['peg_currency']}")
        
        # Valid mechanism
        if 'mechanism' in data:
            valid_mechanisms = ['collateralized', 'algorithmic', 'hybrid']
            if data['mechanism'] not in valid_mechanisms:
                errors.append(f"Invalid mechanism: {data['mechanism']}")
        
        return len(errors) == 0, errors
    
    def validate_protocol(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate protocol entity"""
        errors = []
        
        # Required fields
        required_fields = ['canonical_id', 'name', 'protocol_type', 'reputation_score']
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")
        
        # Canonical ID format (lowercase with underscores)
        if 'canonical_id' in data:
            if not data['canonical_id'].islower() or not all(c.isalnum() or c == '_' for c in data['canonical_id']):
                errors.append("canonical_id must be lowercase alphanumeric with underscores")
        
        # Valid protocol types
        if 'protocol_type' in data:
            valid_types = ['lending', 'amm', 'stable_pool', 'yield_farming', 'liquid_staking']
            if data['protocol_type'] not in valid_types:
                errors.append(f"Invalid protocol_type: {data['protocol_type']}")
        
        # Reputation score bounds
        if 'reputation_score' in data:
            score = data['reputation_score']
            if not isinstance(score, (int, float)) or score < 0 or score > 1:
                errors.append("reputation_score must be between 0 and 1")
        
        return len(errors) == 0, errors
    
    def validate_yield_data(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate yield data entity"""
        errors = []
        
        # Required fields
        required_fields = ['pool_id', 'timestamp', 'apy_base', 'tvl_usd']
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")
        
        # APY bounds validation
        if 'apy_base' in data:
            apy = data['apy_base']
            if not isinstance(apy, (int, float)):
                errors.append("apy_base must be a number")
            elif apy < 0:
                errors.append("apy_base cannot be negative")
            elif apy > 100:  # 100% APY outlier threshold
                errors.append(f"apy_base {apy}% exceeds outlier threshold (100%)")
            elif apy > 50:   # 50% reasonable maximum
                logger.warning(f"High APY detected: {apy}% - requires review")
        
        # TVL bounds validation
        if 'tvl_usd' in data:
            tvl = data['tvl_usd']
            if not isinstance(tvl, (int, float)):
                errors.append("tvl_usd must be a number")
            elif tvl < 1000:  # Minimum TVL threshold
                errors.append(f"tvl_usd ${tvl:,.0f} below minimum threshold ($1,000)")
        
        # Timestamp validation
        if 'timestamp' in data:
            try:
                timestamp = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
                age = datetime.utcnow() - timestamp.replace(tzinfo=None)
                
                if age > timedelta(minutes=30):  # Data freshness threshold
                    errors.append(f"Data is stale: {age.total_seconds()/60:.1f} minutes old")
                elif age > timedelta(minutes=10):  # Stale warning
                    logger.warning(f"Data approaching staleness: {age.total_seconds()/60:.1f} minutes old")
                    
            except ValueError as e:
                errors.append(f"Invalid timestamp format: {e}")
        
        # Reward APY validation
        if 'apy_reward' in data and data['apy_reward'] > 0:
            if 'apy_total' in data:
                expected_total = data['apy_base'] + data['apy_reward']
                actual_total = data['apy_total']
                if abs(expected_total - actual_total) > 0.01:  # Allow small rounding differences
                    errors.append(f"APY calculation mismatch: base({data['apy_base']}) + reward({data['apy_reward']}) != total({actual_total})")
        
        return len(errors) == 0, errors
    
    def normalize_stablecoin_id(self, raw_symbol: str) -> Optional[str]:
        """Normalize raw symbol to canonical stablecoin ID"""
        if not raw_symbol:
            return None
            
        # Get canonical mappings
        mappings = self.schema.get('canonical_mappings', {}).get('stablecoins', {})
        
        # Direct match
        symbol_upper = raw_symbol.upper()
        if symbol_upper in mappings:
            return symbol_upper
            
        # Check synonyms
        for canonical_id, config in mappings.items():
            synonyms = config.get('synonyms', [])
            if symbol_upper in [s.upper() for s in synonyms]:
                return canonical_id
                
        logger.warning(f"Unknown stablecoin symbol: {raw_symbol}")
        return None
    
    def normalize_protocol_id(self, raw_protocol: str) -> Optional[str]:
        """Normalize raw protocol name to canonical protocol ID"""
        if not raw_protocol:
            return None
            
        # Get canonical mappings  
        mappings = self.schema.get('canonical_mappings', {}).get('protocols', {})
        
        # Direct match
        protocol_lower = raw_protocol.lower()
        if protocol_lower in mappings:
            return protocol_lower
            
        # Check synonyms
        for canonical_id, config in mappings.items():
            synonyms = config.get('synonyms', [])
            if protocol_lower in [s.lower() for s in synonyms]:
                return canonical_id
                
        # Partial matching for common cases
        if 'aave' in protocol_lower:
            return 'aave_v3'
        elif 'compound' in protocol_lower:
            return 'compound_v3'
        elif 'curve' in protocol_lower:
            return 'curve'
            
        logger.warning(f"Unknown protocol: {raw_protocol}")
        return None
    
    def get_protocol_reputation(self, protocol_id: str) -> float:
        """Get reputation score for protocol"""
        mappings = self.schema.get('canonical_mappings', {}).get('protocols', {})
        protocol_config = mappings.get(protocol_id, {})
        return protocol_config.get('reputation_score', 0.5)  # Default medium reputation
    
    def is_institutional_grade(self, tvl_usd: float, protocol_id: str = None) -> bool:
        """Check if pool meets institutional grade requirements"""
        institutional_min_tvl = 10_000_000  # $10M minimum
        
        if tvl_usd < institutional_min_tvl:
            return False
            
        # Additional protocol reputation requirement for institutional grade
        if protocol_id:
            reputation = self.get_protocol_reputation(protocol_id)
            return reputation >= 0.8  # High reputation required
            
        return True
    
    def validate_and_normalize_yield_data(self, raw_data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], List[str]]:
        """Validate and normalize raw yield data to canonical format"""
        errors = []
        normalized_data = {}
        
        try:
            # Normalize stablecoin symbol
            raw_symbol = raw_data.get('symbol', raw_data.get('asset', ''))
            canonical_stablecoin = self.normalize_stablecoin_id(raw_symbol)
            if not canonical_stablecoin:
                errors.append(f"Cannot normalize stablecoin symbol: {raw_symbol}")
                return False, {}, errors
                
            # Normalize protocol
            raw_protocol = raw_data.get('project', raw_data.get('protocol', ''))
            canonical_protocol = self.normalize_protocol_id(raw_protocol)
            if not canonical_protocol:
                errors.append(f"Cannot normalize protocol: {raw_protocol}")
                return False, {}, errors
            
            # Build normalized data structure
            normalized_data = {
                'pool_id': raw_data.get('pool_id', f"{canonical_protocol}_{canonical_stablecoin}"),
                'timestamp': datetime.utcnow().isoformat(),
                'stablecoin_id': canonical_stablecoin,
                'protocol_id': canonical_protocol,
                'chain_id': raw_data.get('chain', 'ethereum').lower(),
                'apy_base': float(raw_data.get('apy', raw_data.get('latestAnnualPercentageRate', 0))),
                'tvl_usd': float(raw_data.get('tvlUsd', raw_data.get('tvl', 0))),
                'data_quality': {
                    'is_stale': False,
                    'confidence_score': 0.9,  # High confidence for direct API data
                    'source_reliability': 'high'
                },
                'metadata': {
                    'original_data': raw_data,
                    'normalization_timestamp': datetime.utcnow().isoformat()
                }
            }
            
            # Add optional fields if present
            if 'apy_reward' in raw_data:
                normalized_data['apy_reward'] = float(raw_data['apy_reward'])
                normalized_data['apy_total'] = normalized_data['apy_base'] + normalized_data['apy_reward']
            
            # Validate the normalized data
            is_valid, validation_errors = self.validate_yield_data(normalized_data)
            errors.extend(validation_errors)
            
            return is_valid, normalized_data, errors
            
        except Exception as e:
            errors.append(f"Normalization error: {str(e)}")
            return False, {}, errors