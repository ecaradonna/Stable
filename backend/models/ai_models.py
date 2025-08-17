from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

class ChatMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    user_id: Optional[str] = None
    message: str
    response: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = None

class ChatMessageCreate(BaseModel):
    session_id: str
    user_id: Optional[str] = None
    message: str

class ChatResponse(BaseModel):
    response: str
    session_id: str
    message_id: str
    disclaimer: str = "This is a simulation based on current data. Not financial advice. Always do your own research before making investment decisions."

class AIAlert(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_email: str
    stablecoin: str
    condition: str  # e.g., ">"
    threshold: float
    is_active: bool = True
    last_triggered: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    alert_type: str = "yield_threshold"  # future: risk_score, liquidity, etc.

class AIAlertCreate(BaseModel):
    user_email: str
    stablecoin: str
    condition: str
    threshold: float
    alert_type: str = "yield_threshold"

class AIAlertTrigger(BaseModel):
    alert_id: str
    triggered_at: datetime
    current_value: float
    threshold: float
    message: str