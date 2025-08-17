from fastapi import FastAPI, APIRouter
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List
import uuid
from datetime import datetime
from routes.ai_routes import router as ai_router
from routes.yield_routes import router as yield_router
from routes.user_routes import router as user_router

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(
    title="StableYield API",
    description="API for StableYield.com - The Benchmark for Stablecoin Yields",
    version="1.0.0"
)

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Define Models for legacy endpoints
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

# Legacy endpoints (kept for compatibility)
@api_router.get("/")
async def root():
    return {
        "message": "StableYield API v1.0.0",
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": {
            "yields": "/api/yields",
            "users": "/api/users", 
            "ai": "/api/ai"
        }
    }

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

@api_router.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Test database connection
        await db.command("ping")
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database": db_status,
        "version": "1.0.0"
    }

# Include all routers in the main app
app.include_router(api_router)
app.include_router(ai_router, prefix="/api")
app.include_router(yield_router, prefix="/api")
app.include_router(user_router, prefix="/api")

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    logger.info("StableYield API starting up...")
    logger.info("Available endpoints:")
    logger.info("  - GET /api/ (API info)")
    logger.info("  - GET /api/health (Health check)")
    logger.info("  - GET /api/yields (All yields)")
    logger.info("  - POST /api/users/waitlist (Join waitlist)")
    logger.info("  - POST /api/ai/chat (AI assistant)")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
    logger.info("StableYield API shutting down...")