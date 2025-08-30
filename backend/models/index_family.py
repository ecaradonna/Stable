"""
StableYield Index Family Models
Implements the 4-index family: SY100, SY-CeFi, SY-DeFi, SY-RPI
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Union
from datetime import datetime
from enum import Enum

class IndexCode(str, Enum):
    """Index codes for the StableYield family"""
    SYI = "SYI"          # Original StableYield Index  
    SYC = "SYC"          # StableYield Composite Index (formerly SY100)
    SYCEFI = "SYCEFI"    # CeFi benchmark
    SYDEFI = "SYDEFI"    # DeFi benchmark  
    SYRPI = "SYRPI"      # Risk Premium Index

class IndexMode(str, Enum):
    """Index calculation modes"""
    NORMAL = "Normal"
    BEAR = "Bear"         # DeFi TVL < 20th percentile 
    HIGH_VOL = "High-Vol" # Volatility > 2x rolling mean

class WeightingMethod(str, Enum):
    """Weighting methodologies"""
    EQUAL_RISK = "equal_risk"     # Inverse volatility (SY100)
    CAPACITY = "capacity"         # CeFi capacity weighted  
    TVL_MATURITY = "tvl_maturity" # DeFi TVL * maturity
    EQUAL = "equal"               # Equal weights
    CAP_WEIGHTED = "cap_weighted" # Market cap weighted

class ConstituentType(str, Enum):
    """Types of index constituents"""
    STABLECOIN = "stablecoin"
    CEFI_STRATEGY = "cefi_strategy" 
    DEFI_STRATEGY = "defi_strategy"
    PROTOCOL = "protocol"

class Constituent(BaseModel):
    """Individual constituent of an index"""
    id: str = Field(..., description="Unique identifier")
    symbol: str = Field(..., description="Symbol (USDT, USDC, etc)")
    name: str = Field(..., description="Full name")
    type: ConstituentType = Field(..., description="Type of constituent")
    
    # Financial metrics
    current_apy: Optional[float] = Field(None, description="Current APY")
    apy_effective: Optional[float] = Field(None, description="Effective APY (no incentives)")
    ray: Optional[float] = Field(None, description="Risk-Adjusted Yield")
    
    # Risk scores (0-1)
    peg_score: Optional[float] = Field(None, description="Peg stability score")
    liquidity_score: Optional[float] = Field(None, description="Liquidity depth score") 
    counterparty_score: Optional[float] = Field(None, description="Counterparty risk score")
    s_worst: Optional[float] = Field(None, description="Minimum of all risk scores")
    
    # Market data
    tvl_usd: Optional[float] = Field(None, description="Total Value Locked (USD)")
    market_cap: Optional[float] = Field(None, description="Market capitalization")
    capacity_usd: Optional[float] = Field(None, description="Available capacity (CeFi)")
    
    # Metadata
    platform: Optional[str] = Field(None, description="Platform/Protocol")
    chain: Optional[str] = Field(None, description="Blockchain") 
    jurisdiction: Optional[str] = Field(None, description="Regulatory jurisdiction")
    audit_count: Optional[int] = Field(0, description="Number of audits")
    operational_days: Optional[int] = Field(None, description="Days operational")
    maturity_factor: Optional[float] = Field(1.0, description="Maturity adjustment factor")
    
class IndexWeight(BaseModel):
    """Weight of a constituent in an index"""
    constituent_id: str = Field(..., description="Constituent ID")
    weight: float = Field(..., ge=0, le=1, description="Weight (0-1)")
    weight_percent: float = Field(..., ge=0, le=100, description="Weight as percentage")
    
class IndexValue(BaseModel):
    """Daily index value and metadata"""
    date: datetime = Field(..., description="Calculation date")
    index_code: IndexCode = Field(..., description="Index identifier")
    value: float = Field(..., description="Index value")
    
    # Calculation metadata
    mode: IndexMode = Field(IndexMode.NORMAL, description="Calculation mode")
    confidence: float = Field(1.0, ge=0, le=1, description="Data confidence score")
    hhi: Optional[float] = Field(None, description="Herfindahl-Hirschman Index (concentration)")
    
    # Statistics
    constituent_count: int = Field(0, description="Number of constituents")
    total_tvl: Optional[float] = Field(None, description="Total TVL of constituents") 
    avg_yield: Optional[float] = Field(None, description="Average constituent yield")
    volatility: Optional[float] = Field(None, description="Index volatility")
    
    # Notes and flags
    staleness_flags: List[str] = Field(default_factory=list, description="Data staleness warnings")
    notes: Optional[str] = Field(None, description="Calculation notes")

class IndexConstituents(BaseModel):
    """Index constituents and their weights for a specific date"""
    date: datetime = Field(..., description="Calculation date")
    index_code: IndexCode = Field(..., description="Index identifier")
    constituents: List[Constituent] = Field(..., description="List of constituents")
    weights: List[IndexWeight] = Field(..., description="Constituent weights")
    
    # Metadata
    weighting_method: WeightingMethod = Field(..., description="Weighting methodology used")
    reconstitution_date: Optional[datetime] = Field(None, description="Last reconstitution")
    next_reconstitution: Optional[datetime] = Field(None, description="Next reconstitution")

class IndexSeries(BaseModel):
    """Time series of index values"""
    index_code: IndexCode = Field(..., description="Index identifier")
    start_date: datetime = Field(..., description="Start date")
    end_date: datetime = Field(..., description="End date") 
    frequency: str = Field("daily", description="Data frequency")
    values: List[IndexValue] = Field(..., description="Time series values")
    
    # Performance metrics
    total_return: Optional[float] = Field(None, description="Total return over period")
    annualized_return: Optional[float] = Field(None, description="Annualized return")
    volatility: Optional[float] = Field(None, description="Annualized volatility")
    sharpe_ratio: Optional[float] = Field(None, description="Sharpe ratio")
    max_drawdown: Optional[float] = Field(None, description="Maximum drawdown")

class TBillData(BaseModel):
    """U.S. Treasury Bill data for SY-RPI calculation"""
    date: datetime = Field(..., description="Data date")
    rate_3m: float = Field(..., description="3-month Treasury Bill rate")
    source: str = Field("FRED", description="Data source")
    
class IndexFactsheet(BaseModel):
    """Daily factsheet for index family"""
    date: datetime = Field(..., description="Factsheet date")
    
    # All index values
    syi: Optional[IndexValue] = Field(None, description="Core StableYield Index")
    sy100: Optional[IndexValue] = Field(None, description="Top 100 strategies")
    sy_cefi: Optional[IndexValue] = Field(None, description="CeFi benchmark")
    sy_defi: Optional[IndexValue] = Field(None, description="DeFi benchmark") 
    sy_rpi: Optional[IndexValue] = Field(None, description="Risk Premium Index")
    
    # Market overview
    tbill_3m: Optional[float] = Field(None, description="3M Treasury rate")
    total_stablecoin_mcap: Optional[float] = Field(None, description="Total stablecoin market cap")
    defi_tvl: Optional[float] = Field(None, description="Total DeFi TVL")
    
    # Key metrics
    risk_regime: str = Field("Normal", description="Current risk regime")
    dominant_mode: IndexMode = Field(IndexMode.NORMAL, description="Most common index mode")
    correlation_btc: Optional[float] = Field(None, description="Correlation with BTC")
    
    # Factsheet metadata
    version: str = Field("1.0", description="Factsheet version")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Generation timestamp")

# Response models for API
class IndexResponse(BaseModel):
    """API response for single index query"""
    success: bool = True
    data: IndexValue
    message: str = "Index data retrieved successfully"

class IndexSeriesResponse(BaseModel):
    """API response for index time series"""
    success: bool = True
    data: IndexSeries  
    message: str = "Index series retrieved successfully"

class IndexConstituentsResponse(BaseModel):
    """API response for index constituents"""
    success: bool = True
    data: IndexConstituents
    message: str = "Index constituents retrieved successfully"

class IndexFactsheetResponse(BaseModel):
    """API response for index factsheet"""
    success: bool = True
    data: IndexFactsheet
    message: str = "Index factsheet retrieved successfully"

class IndexFamilyOverview(BaseModel):
    """Overview of all indices in the family"""
    date: datetime = Field(..., description="Data date")
    indices: Dict[IndexCode, IndexValue] = Field(..., description="All index values")
    
    # Family-level metrics
    family_aum: Optional[float] = Field(None, description="Total assets under management")
    total_constituents: int = Field(0, description="Total unique constituents across all indices")
    coverage_ratio: Optional[float] = Field(None, description="Market coverage ratio")
    
    # Cross-index correlations (upper triangular matrix)
    correlations: Optional[Dict[str, float]] = Field(None, description="Inter-index correlations")
    
class IndexFamilyResponse(BaseModel):
    """API response for index family overview"""
    success: bool = True
    data: IndexFamilyOverview
    message: str = "Index family overview retrieved successfully"