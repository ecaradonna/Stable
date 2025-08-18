from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

class PriceRealtime(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    ts: datetime = Field(default_factory=datetime.utcnow)
    symbol: str
    venue: str
    price_usd: float
    bid: Optional[float] = None
    ask: Optional[float] = None
    mid: Optional[float] = None
    spread_bps: Optional[float] = None
    volume_1m: Optional[float] = None
    source: str = "cryptocompare"

class OrderbookDepth(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    ts: datetime = Field(default_factory=datetime.utcnow)
    symbol: str
    venue: str
    depth_usd_at_10bps: float
    depth_usd_at_20bps: float
    depth_usd_at_50bps: float
    best_bid: float
    best_ask: float

class PegMetrics(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    ts: datetime = Field(default_factory=datetime.utcnow)
    symbol: str
    vw_price_usd: float
    peg_dev_bps: float
    peg_vol_5m_bps: float
    peg_vol_1h_bps: float
    venues_covered: int
    peg_score: float

class LiquidityMetrics(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    ts: datetime = Field(default_factory=datetime.utcnow)
    symbol: str
    liq_score_0_1: float
    depth_10bps_usd: float
    depth_20bps_usd: float
    depth_50bps_usd: float
    avg_spread_bps: float
    venues_covered: int

class RiskAdjustedYield(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    ts: datetime = Field(default_factory=datetime.utcnow)
    strategy_id: str
    symbol: str
    apy: float
    peg_score: float
    liq_score: float
    ry_apy: float
    notes: Optional[str] = None

class StablecoinMetricsResponse(BaseModel):
    symbol: str
    vw_price: float
    peg_dev_bps: float
    peg_vol_5m_bps: float
    liq_score: float
    depth_usd: Dict[str, float]
    avg_spread_bps: float
    asof: str

class RiskAdjustedStrategy(BaseModel):
    strategy_id: str
    platform: str
    symbol: str
    apy: float
    ry_apy: float
    peg_score: float
    liq_score: float
    capacity_usd: float
    lockup_days: int
    risk_tier: str