"""
Data models for peg monitoring system
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Union
from enum import Enum
import time

class PegStatus(str, Enum):
    NORMAL = "normal"
    WARNING = "warning"  
    DEPEG = "depeg"

@dataclass
class PricePoint:
    """Single price data point from a source"""
    source: str
    price: float
    timestamp: int
    
    @property
    def is_valid(self) -> bool:
        """Check if price point is valid (not NaN, positive)"""
        import math
        return not math.isnan(self.price) and self.price > 0

@dataclass
class PegReport:
    """Peg analysis report for a single symbol"""
    symbol: str
    avg_ref: float  # Average reference price from CeFi sources
    abs_diff: float  # Absolute difference from $1.00
    pct_diff: float  # Percentage difference from $1.00  
    bps_diff: float  # Basis points difference from $1.00
    is_depeg: bool  # Is currently depegged
    status: PegStatus
    confidence: float  # Confidence score (0-1)
    sources_used: List[str]
    timestamp: int
    
    def __post_init__(self):
        """Calculate derived fields"""
        if not hasattr(self, 'bps_diff'):
            self.bps_diff = abs(self.pct_diff) * 100  # Convert % to basis points

@dataclass  
class PegCheckPayload:
    """Complete peg check result payload"""
    as_of: int  # Unix timestamp
    symbols: List[str]
    reports: List[PegReport]
    
    # Raw price data by source
    coingecko: Dict[str, float] 
    cryptocompare: Dict[str, float]
    
    # Cross-reference analysis
    cefi_consistency: Dict[str, float]  # Consistency between CeFi sources
    
    # Optional data sources
    chainlink: Optional[Dict[str, float]] = None
    uniswap: Optional[Dict[str, float]] = None
    
    # Metadata
    config: Optional[Dict] = None
    errors: Optional[List[str]] = None
    
    @property
    def total_depegs(self) -> int:
        """Count of symbols currently depegged"""
        return sum(1 for r in self.reports if r.is_depeg)
    
    @property 
    def max_deviation_bps(self) -> float:
        """Maximum deviation in basis points"""
        return max([r.bps_diff for r in self.reports], default=0.0)