import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from motor.motor_asyncio import AsyncIOMotorDatabase
import pymongo

from ..models.index_models import IndexValue, IndexHistoryQuery

logger = logging.getLogger(__name__)

class IndexStorageService:
    """
    Service for storing and retrieving StableYield Index data
    Uses MongoDB with time-series optimizations
    """
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.index_collection = db.stableyield_index
        self.constituents_collection = db.index_constituents
    
    async def initialize_collections(self):
        """Initialize MongoDB collections with proper indexing"""
        try:
            # Create indexes for efficient time-series queries
            index_indexes = [
                [("timestamp", pymongo.DESCENDING)],
                [("index_id", pymongo.ASCENDING), ("timestamp", pymongo.DESCENDING)],
                [("timestamp", pymongo.DESCENDING), ("index_id", pymongo.ASCENDING)]
            ]
            
            for index in index_indexes:
                try:
                    await self.index_collection.create_index(index)
                except Exception as e:
                    logger.warning(f"Index creation failed (may already exist): {e}")
            
            logger.info("Index storage collections initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize collections: {e}")
    
    async def store_index_value(self, index_value: IndexValue) -> bool:
        """Store a calculated index value"""
        try:
            # Convert to dict for MongoDB storage
            doc = {
                "id": index_value.id,
                "timestamp": index_value.timestamp,
                "index_id": index_value.index_id,
                "value": index_value.value,
                "methodology_version": index_value.methodology_version,
                "metadata": index_value.metadata,
                "constituents": [
                    {
                        "symbol": c.symbol,
                        "name": c.name,
                        "market_cap": c.market_cap,
                        "weight": c.weight,
                        "raw_apy": c.raw_apy,
                        "peg_score": c.peg_score,
                        "liquidity_score": c.liquidity_score,
                        "counterparty_score": c.counterparty_score,
                        "ray": c.ray,
                        "last_updated": c.last_updated
                    }
                    for c in index_value.constituents
                ]
            }
            
            result = await self.index_collection.insert_one(doc)
            
            if result.inserted_id:
                logger.info(f"Stored index value: {index_value.value}% at {index_value.timestamp}")
                return True
            else:
                logger.error("Failed to store index value")
                return False
                
        except Exception as e:
            logger.error(f"Error storing index value: {e}")
            return False
    
    async def get_latest_index_value(self, index_id: str = "SYI") -> Optional[IndexValue]:
        """Get the most recent index value"""
        try:
            doc = await self.index_collection.find_one(
                {"index_id": index_id},
                sort=[("timestamp", pymongo.DESCENDING)]
            )
            
            if doc:
                return self._doc_to_index_value(doc)
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving latest index value: {e}")
            return None
    
    async def get_index_history(self, query: IndexHistoryQuery) -> List[IndexValue]:
        """Get historical index values based on query parameters"""
        try:
            # Build MongoDB query
            mongo_query = {"index_id": query.index_id}
            
            if query.start_date or query.end_date:
                timestamp_filter = {}
                if query.start_date:
                    timestamp_filter["$gte"] = query.start_date
                if query.end_date:
                    timestamp_filter["$lte"] = query.end_date
                mongo_query["timestamp"] = timestamp_filter
            
            # Execute query
            cursor = self.index_collection.find(mongo_query).sort("timestamp", pymongo.DESCENDING)
            
            if query.limit:
                cursor = cursor.limit(query.limit)
            
            docs = []
            async for doc in cursor:
                docs.append(doc)
            
            # Convert to IndexValue objects
            results = [self._doc_to_index_value(doc) for doc in docs]
            
            logger.info(f"Retrieved {len(results)} historical index values")
            return results
            
        except Exception as e:
            logger.error(f"Error retrieving index history: {e}")
            return []
    
    async def get_index_statistics(self, index_id: str = "SYI", days: int = 30) -> Dict:
        """Get statistical summary of index performance"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Aggregation pipeline for statistics
            pipeline = [
                {
                    "$match": {
                        "index_id": index_id,
                        "timestamp": {"$gte": start_date}
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "count": {"$sum": 1},
                        "avg_value": {"$avg": "$value"},
                        "min_value": {"$min": "$value"},
                        "max_value": {"$max": "$value"},
                        "latest_timestamp": {"$max": "$timestamp"},
                        "earliest_timestamp": {"$min": "$timestamp"}
                    }
                }
            ]
            
            result = []
            async for doc in self.index_collection.aggregate(pipeline):
                result.append(doc)
            
            if result:
                stats = result[0]
                return {
                    "index_id": index_id,
                    "period_days": days,
                    "data_points": stats.get("count", 0),
                    "average_value": round(stats.get("avg_value", 0), 4),
                    "min_value": round(stats.get("min_value", 0), 4),
                    "max_value": round(stats.get("max_value", 0), 4),
                    "latest_timestamp": stats.get("latest_timestamp"),
                    "earliest_timestamp": stats.get("earliest_timestamp"),
                    "volatility": round(stats.get("max_value", 0) - stats.get("min_value", 0), 4)
                }
            
            return {"index_id": index_id, "data_points": 0}
            
        except Exception as e:
            logger.error(f"Error calculating index statistics: {e}")
            return {"error": str(e)}
    
    def _doc_to_index_value(self, doc: Dict) -> IndexValue:
        """Convert MongoDB document to IndexValue object"""
        from ..models.index_models import StablecoinConstituent
        
        constituents = []
        for c_doc in doc.get("constituents", []):
            constituents.append(
                StablecoinConstituent(
                    symbol=c_doc["symbol"],
                    name=c_doc["name"],
                    market_cap=c_doc["market_cap"],
                    weight=c_doc["weight"],
                    raw_apy=c_doc["raw_apy"],
                    peg_score=c_doc["peg_score"],
                    liquidity_score=c_doc["liquidity_score"],
                    counterparty_score=c_doc["counterparty_score"],
                    ray=c_doc["ray"],
                    last_updated=c_doc["last_updated"]
                )
            )
        
        return IndexValue(
            id=doc["id"],
            timestamp=doc["timestamp"],
            index_id=doc["index_id"],
            value=doc["value"],
            methodology_version=doc.get("methodology_version", "1.0"),
            constituents=constituents,
            metadata=doc.get("metadata", {})
        )
    
    async def cleanup_old_data(self, days_to_keep: int = 365):
        """Clean up old index data (keep last N days)"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
            
            result = await self.index_collection.delete_many({
                "timestamp": {"$lt": cutoff_date}
            })
            
            logger.info(f"Cleaned up {result.deleted_count} old index records")
            return result.deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
            return 0

# TODO: PRODUCTION UPGRADES NEEDED
# 1. Implement proper time-series database (TimescaleDB/InfluxDB)
# 2. Add data compression for historical records
# 3. Implement backup and disaster recovery
# 4. Add data validation and integrity checks
# 5. Optimize queries for large datasets
# 6. Add monitoring and alerting for data quality issues