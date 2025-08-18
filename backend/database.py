import os
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

# Global database connection
_db_client = None
_database = None

async def get_database() -> AsyncIOMotorDatabase:
    """Get the MongoDB database instance"""
    global _db_client, _database
    
    if _database is None:
        mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        db_name = os.environ.get('DB_NAME', 'stableyield')
        
        _db_client = AsyncIOMotorClient(mongo_url)
        _database = _db_client[db_name]
    
    return _database

async def close_database():
    """Close the database connection"""
    global _db_client
    if _db_client:
        _db_client.close()
        _db_client = None
        _database = None