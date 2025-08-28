"""
Data models for Risk Regime Inversion Alert system
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from enum import Enum


class RegimeState(str, Enum):
    """Risk regime states"""
    ON = "ON"                    # Risk-On
    OFF = "OFF"                  # Risk-Off
    OFF_OVERRIDE = "OFF_OVERRIDE"  # Risk-Off forced by peg stress
    NEU = "NEU"                  # Neutral (initialization/no signal)


class AlertType(str, Enum):
    """Alert types for regime changes"""
    EARLY_WARNING = "Early-Warning"
    FLIP_CONFIRMED = "Flip Confirmed"
    OVERRIDE_PEG = "Override Peg"
    INVALIDATION = "Invalidation"


class AlertLevel(str, Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class RegimeComponent(BaseModel):
    """Component RAY data for breadth calculation"""
    symbol: str = Field(..., description="Stablecoin symbol")
    ray: float = Field(..., description="Risk-Adjusted Yield in decimal format")


class PegStatus(BaseModel):
    """Peg stress status for override logic"""
    max_depeg_bps: int = Field(..., description="Maximum single depeg in basis points")
    agg_depeg_bps: int = Field(..., description="Aggregate top-5 depeg in basis points")


class RegimeEvaluationRequest(BaseModel):
    """Request payload for regime evaluation"""
    date: str = Field(..., pattern=r'^\d{4}-\d{2}-\d{2}$', description="Evaluation date (YYYY-MM-DD)")
    syi: float = Field(..., ge=0, le=1, description="SYI value in decimal format")
    tbill_3m: float = Field(..., ge=0, le=1, description="3M T-Bill rate in decimal format")
    components: List[RegimeComponent] = Field(default_factory=list, description="RAY components for breadth")
    peg_status: Optional[PegStatus] = Field(None, description="Peg stress status")


class RegimeSignal(BaseModel):
    """Calculated regime signal indicators"""
    syi_excess: float = Field(..., description="SYI minus T-Bill")
    spread: float = Field(..., description="EMA short minus EMA long")
    z_score: float = Field(..., description="Normalized spread (z-score)")
    slope7: float = Field(..., description="7-day momentum (annualized slope)")
    breadth_pct: float = Field(..., description="Breadth percentage")
    volatility_30d: float = Field(..., description="30-day rolling volatility")
    ema_short: float = Field(..., description="7-day EMA of SYI excess")
    ema_long: float = Field(..., description="30-day EMA of SYI excess")


class RegimeAlert(BaseModel):
    """Alert information for regime changes"""
    type: AlertType = Field(..., description="Type of alert")
    level: AlertLevel = Field(..., description="Alert severity level")
    message: str = Field(..., description="Human-readable alert message")
    trigger_conditions: List[str] = Field(default_factory=list, description="Conditions that triggered the alert")


class RegimeEvaluationResponse(BaseModel):
    """Response for regime evaluation"""
    success: bool = Field(True, description="Evaluation success status")
    date: str = Field(..., description="Evaluation date")
    state: RegimeState = Field(..., description="Current regime state")
    signal: RegimeSignal = Field(..., description="Calculated signal indicators")
    alert: Optional[RegimeAlert] = Field(None, description="Alert information if any")
    methodology_version: str = Field("2.0.0", description="Methodology version")
    params_version: str = Field("1.0.0", description="Parameters version")
    previous_state: Optional[RegimeState] = Field(None, description="Previous regime state")
    days_in_state: int = Field(0, description="Days in current state")
    cooldown_until: Optional[str] = Field(None, description="Cooldown end date")
    override_until: Optional[str] = Field(None, description="Override end date")


class RegimeHistoryEntry(BaseModel):
    """Single entry in regime history"""
    date: str = Field(..., description="Date (YYYY-MM-DD)")
    state: RegimeState = Field(..., description="Regime state")
    syi_excess: float = Field(..., description="SYI excess value")
    z_score: float = Field(..., description="Z-score value")
    spread: Optional[float] = Field(None, description="EMA spread")
    slope7: Optional[float] = Field(None, description="7-day momentum")
    breadth_pct: Optional[float] = Field(None, description="Breadth percentage")
    alert_type: Optional[AlertType] = Field(None, description="Alert type if any")


class RegimeHistoryResponse(BaseModel):
    """Response for regime history"""
    success: bool = Field(True, description="Request success status")
    series: List[RegimeHistoryEntry] = Field(..., description="Historical data series")
    total_entries: int = Field(..., description="Total number of entries")
    from_date: str = Field(..., description="Start date of series")
    to_date: str = Field(..., description="End date of series")
    methodology_version: str = Field("2.0.0", description="Methodology version")


class RegimeUpsertRequest(BaseModel):
    """Request for upserting regime data"""
    date: str = Field(..., regex=r'^\d{4}-\d{2}-\d{2}$', description="Date to upsert")
    syi: float = Field(..., ge=0, le=1, description="SYI value")
    tbill_3m: float = Field(..., ge=0, le=1, description="T-Bill rate")
    components: List[RegimeComponent] = Field(default_factory=list, description="RAY components")
    peg_status: Optional[PegStatus] = Field(None, description="Peg status")
    force_recalculate: bool = Field(False, description="Force recalculation if data exists")


class RegimeUpsertResponse(BaseModel):
    """Response for regime upsert"""
    success: bool = Field(True, description="Upsert success status")
    date: str = Field(..., description="Upserted date")
    state: RegimeState = Field(..., description="Calculated regime state")
    message: str = Field(..., description="Operation result message")
    created: bool = Field(..., description="Whether new data was created")
    alert_sent: bool = Field(False, description="Whether alert was sent")


class RegimeParameters(BaseModel):
    """Configuration parameters for regime detection"""
    ema_short: int = Field(7, description="Short EMA period (days)")
    ema_long: int = Field(30, description="Long EMA period (days)")
    z_enter: float = Field(0.5, description="Z-score threshold for entry")
    persist_days: int = Field(2, description="Persistence days required")
    cooldown_days: int = Field(7, description="Cooldown period after flip")
    breadth_on_max: float = Field(40.0, description="Max breadth % for Risk-On")
    breadth_off_min: float = Field(60.0, description="Min breadth % for Risk-Off")
    peg_single_bps: int = Field(100, description="Single peg stress threshold (bps)")
    peg_agg_bps: int = Field(150, description="Aggregate peg stress threshold (bps)")
    peg_clear_hours: int = Field(24, description="Hours to clear peg override")
    volatility_epsilon: float = Field(0.001, description="Minimum volatility for z-score")


class RegimeHealthResponse(BaseModel):
    """Health check response for regime service"""
    service: str = Field("risk_regime", description="Service name")
    status: str = Field("healthy", description="Service status")
    methodology_version: str = Field("2.0.0", description="Methodology version")
    params_version: str = Field("1.0.0", description="Parameters version")
    timestamp: str = Field(..., description="Health check timestamp")
    parameters: RegimeParameters = Field(..., description="Current parameters")
    last_evaluation: Optional[str] = Field(None, description="Last evaluation date")
    total_evaluations: int = Field(0, description="Total evaluations performed")


class RegimeStatsResponse(BaseModel):
    """Statistics response for regime service"""
    total_days: int = Field(0, description="Total days with data")
    risk_on_days: int = Field(0, description="Days in Risk-On state")
    risk_off_days: int = Field(0, description="Days in Risk-Off state")
    override_days: int = Field(0, description="Days in Override state")
    total_flips: int = Field(0, description="Total regime flips")
    avg_regime_duration: float = Field(0.0, description="Average regime duration (days)")
    current_state: Optional[RegimeState] = Field(None, description="Current regime state")
    days_in_current_state: int = Field(0, description="Days in current state")
    last_flip_date: Optional[str] = Field(None, description="Last regime flip date")