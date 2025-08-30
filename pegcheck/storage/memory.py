"""
In-memory storage backend for pegcheck data (testing/development)
"""

import asyncio
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from collections import deque, defaultdict
import time

from .base import BaseStorage
from ..core.models import PegCheckPayload, PegReport

class MemoryStorage(BaseStorage):
    """In-memory storage implementation for testing/development"""
    
    def __init__(self, max_records: int = 1000):
        self.max_records = max_records
        self.peg_checks = deque(maxlen=max_records)  # Store PegCheckPayload objects
        self.source_metrics = defaultdict(list)  # source -> list of metrics
        self._initialized = False
    
    async def initialize(self):
        """Initialize storage (no-op for memory storage)"""
        self._initialized = True
    
    async def store_peg_check(self, payload: PegCheckPayload) -> bool:
        """Store a complete peg check payload"""
        if not self._initialized:
            await self.initialize()
            
        try:
            # Add timestamp for ordering
            payload_with_meta = {
                'timestamp': datetime.utcnow(),
                'payload': payload
            }
            self.peg_checks.append(payload_with_meta)
            return True
            
        except Exception as e:
            print(f"Failed to store peg check in memory: {e}")
            return False
    
    async def get_peg_history(self, symbol: str, hours: int = 24) -> List[Tuple[datetime, float, str]]:
        """Get peg history for a symbol"""
        if not self._initialized:
            await self.initialize()
        
        history = []
        since_time = datetime.utcnow() - timedelta(hours=hours)
        
        for record in self.peg_checks:
            if record['timestamp'] < since_time:
                continue
                
            payload = record['payload']
            for report in payload.reports:
                if report.symbol == symbol and not str(report.avg_ref).lower() == 'nan':
                    history.append((
                        datetime.fromtimestamp(report.timestamp),
                        float(report.avg_ref),
                        report.status.value
                    ))
        
        # Sort by timestamp
        history.sort(key=lambda x: x[0])
        return history
    
    async def get_latest_peg_check(self, symbols: Optional[List[str]] = None) -> Optional[PegCheckPayload]:
        """Get the latest peg check data"""
        if not self._initialized:
            await self.initialize()
            
        if not self.peg_checks:
            return None
        
        # Get the most recent record
        latest_record = self.peg_checks[-1]
        payload = latest_record['payload']
        
        # Filter symbols if specified
        if symbols:
            filtered_reports = [r for r in payload.reports if r.symbol in symbols]
            # Create new payload with filtered reports
            filtered_payload = PegCheckPayload(
                as_of=payload.as_of,
                symbols=symbols,
                reports=filtered_reports,
                coingecko=payload.coingecko,
                cryptocompare=payload.cryptocompare,
                chainlink=payload.chainlink,
                uniswap=payload.uniswap,
                cefi_consistency=payload.cefi_consistency,
                config=payload.config,
                errors=payload.errors
            )
            return filtered_payload
        
        return payload
    
    async def get_source_reliability(self, source: str, hours: int = 168) -> Dict[str, float]:
        """Get source reliability metrics"""
        if not self._initialized:
            await self.initialize()
        
        # For memory storage, we'll calculate based on stored peg checks
        since_time = datetime.utcnow() - timedelta(hours=hours)
        reliability = defaultdict(lambda: {'total': 0, 'success': 0})
        
        for record in self.peg_checks:
            if record['timestamp'] < since_time:
                continue
                
            payload = record['payload']
            
            # Check which symbols had data from this source
            source_data = None
            if source == 'coingecko':
                source_data = payload.coingecko
            elif source == 'cryptocompare':
                source_data = payload.cryptocompare
            elif source == 'chainlink' and payload.chainlink:
                source_data = payload.chainlink
            elif source == 'uniswap' and payload.uniswap:
                source_data = payload.uniswap
            
            if source_data:
                for symbol, price in source_data.items():
                    reliability[symbol]['total'] += 1
                    if not str(price).lower() == 'nan' and price > 0:
                        reliability[symbol]['success'] += 1
        
        # Calculate success rates
        result = {}
        for symbol, stats in reliability.items():
            if stats['total'] > 0:
                success_rate = stats['success'] / stats['total']
                result[symbol] = {
                    'success_rate': success_rate,
                    'avg_response_time_ms': 100.0,  # Mock value
                    'total_requests': stats['total']
                }
        
        return result
    
    async def cleanup_old_data(self, days_to_keep: int = 30) -> int:
        """Clean up old data"""
        if not self._initialized:
            await self.initialize()
        
        cutoff_time = datetime.utcnow() - timedelta(days=days_to_keep)
        original_count = len(self.peg_checks)
        
        # Remove old records
        self.peg_checks = deque(
            [record for record in self.peg_checks if record['timestamp'] >= cutoff_time],
            maxlen=self.max_records
        )
        
        deleted_count = original_count - len(self.peg_checks)
        return deleted_count
    
    async def health_check(self) -> Dict[str, any]:
        """Check storage backend health"""
        if not self._initialized:
            await self.initialize()
        
        return {
            "status": "healthy",
            "backend": "memory",
            "connected": True,
            "records": {
                "peg_checks": len(self.peg_checks),
                "max_records": self.max_records
            },
            "memory_usage": "limited_by_max_records",
            "note": "In-memory storage for development/testing only"
        }
    
    async def close(self):
        """Close storage (no-op for memory storage)"""
        pass

# Convenience function to create default memory storage
def create_memory_storage(max_records: int = 1000) -> MemoryStorage:
    """Create a new memory storage instance"""
    return MemoryStorage(max_records=max_records)