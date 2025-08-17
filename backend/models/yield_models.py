from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

class YieldData(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    stablecoin: str
    name: str
    currentYield: float
    source: str
    sourceType: str  # CeFi | DeFi
    riskScore: str   # Low | Medium | High
    change24h: float
    liquidity: str
    lastUpdated: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = None

class YieldDataCreate(BaseModel):
    stablecoin: str
    name: str
    currentYield: float
    source: str
    sourceType: str
    riskScore: str
    liquidity: str
    metadata: Optional[Dict[str, Any]] = None

class HistoricalYield(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    stablecoin: str
    date: datetime
    yield_value: float = Field(alias="yield")
    source: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class HistoricalYieldCreate(BaseModel):
    stablecoin: str
    date: datetime
    yield_value: float = Field(alias="yield")
    source: str

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    name: Optional[str] = None
    signupType: str  # waitlist | newsletter
    interest: Optional[str] = None  # trader | investor | institution | media
    signupDate: datetime = Field(default_factory=datetime.utcnow)
    isActive: bool = True

class UserCreate(BaseModel):
    email: str
    name: Optional[str] = None
    signupType: str
    interest: Optional[str] = None

class WaitlistSignup(UserCreate):
    signupType: str = "waitlist"

class NewsletterSignup(UserCreate):
    signupType: str = "newsletter"