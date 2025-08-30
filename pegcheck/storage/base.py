"""
Base storage interface for pegcheck data persistence
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Tuple
from datetime import datetime

from ..core.models import PegCheckPayload, PegReport

class BaseStorage(ABC):
    """Abstract base class for storage backends"""
    
    @abstractmethod
    async def store_peg_check(self, payload: PegCheckPayload) -> bool:
        """Store a complete peg check payload"""
        pass
    
    @abstractmethod
    async def get_peg_history(self, symbol: str, hours: int = 24) -> List[Tuple[datetime, float, str]]:
        """Get peg history for a symbol (timestamp, price, status)"""
        pass
    
    @abstractmethod
    async def get_latest_peg_check(self, symbols: Optional[List[str]] = None) -> Optional[PegCheckPayload]:
        """Get the latest peg check data"""
        pass
    
    @abstractmethod
    async def get_source_reliability(self, source: str, hours: int = 168) -> Dict[str, float]:
        """Get source reliability metrics over time period"""
        pass
    
    @abstractmethod
    async def cleanup_old_data(self, days_to_keep: int = 30) -> int:
        """Clean up old data and return number of records deleted"""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, any]:
        """Check storage backend health"""
        pass