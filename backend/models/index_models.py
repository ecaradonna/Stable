from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

class StablecoinConstituent(BaseModel):
    """Individual stablecoin data for index calculation"""
    symbol: str
    name: str
    market_cap: float
    weight: float
    raw_apy: float
    peg_score: float  # 0-1, where 1 is perfect peg
    liquidity_score: float  # 0-1, where 1 is perfect liquidity
    counterparty_score: float  # 0-1, where 1 is lowest risk
    ray: float  # Risk-Adjusted Yield
    last_updated: datetime

class IndexValue(BaseModel):
    """StableYield Index value at a point in time"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime
    index_id: str  # e.g., "SYI" for StableYield Index
    value: float  # The calculated index value
    methodology_version: str = "1.0"
    constituents: List[StablecoinConstituent]
    metadata: Optional[Dict[str, Any]] = {}
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class IndexHistoryQuery(BaseModel):
    """Query parameters for historical index data"""
    index_id: str = "SYI"
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    interval: str = "1m"  # 1m, 5m, 15m, 1h, 1d
    limit: Optional[int] = 1000

# TODO: PRODUCTION UPGRADE NEEDED
# These models are designed for the current demo implementation
# For production, consider:
# 1. Adding more sophisticated risk scoring models
# 2. Supporting multiple index methodologies
# 3. Adding data validation and quality checks
# 4. Implementing proper error handling for missing data