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
from routes.crypto_compare_routes import router as crypto_router
from routes.index_routes import router as index_router
from routes.production_status_routes import router as production_router
from routes.policy_routes import router as policy_router
from routes.liquidity_routes import router as liquidity_router
from routes.sanitization_routes import router as sanitization_router
from routes.ray_routes import router as ray_router
from routes.websocket_routes import router as websocket_router
from routes.analytics_routes import router as analytics_router
from routes.ml_routes import router as ml_router
from routes.enterprise_routes import router as enterprise_router

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(
    title="StableYield Market Intelligence API",
    description="Professional-grade API for stablecoin yield benchmarks, risk analytics, and market intelligence",
    version="2.0.0"
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
        "message": "StableYield Market Intelligence API v2.0.0",
        "tagline": "The Bloomberg for Stablecoin Yields",
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": {
            "yields": "/api/yields",
            "users": "/api/users", 
            "ai": "/api/ai",
            "market_intelligence": "/api/v1"
        },
        "new_features": {
            "peg_stability_monitoring": "/api/v1/stablecoins/metrics",
            "liquidity_analysis": "/api/v1/liquidity/analysis",
            "risk_adjusted_yields": "/api/v1/strategies/risk-adjusted-yield",
            "peg_stability_ranking": "/api/v1/peg-stability/ranking"
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
    
    # Check CryptoCompare API key
    cc_key_status = "configured" if os.getenv('CC_API_KEY_STABLEYIELD', 'DEMO_KEY') != 'DEMO_KEY' else "demo_mode"
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database": db_status,
        "cryptocompare_api": cc_key_status,
        "openai_api": "configured" if os.getenv('OPENAI_API_KEY') else "not_configured",
        "version": "2.0.0",
        "capabilities": [
            "Real-time yield aggregation",
            "Peg stability monitoring", 
            "Liquidity analysis",
            "Risk-adjusted yield calculations",
            "AI-powered market intelligence"
        ]
    }

# Include all routers in the main app
app.include_router(api_router)
app.include_router(ai_router, prefix="/api")
app.include_router(yield_router, prefix="/api")
app.include_router(user_router, prefix="/api")
app.include_router(crypto_router, prefix="/api")  # New CryptoCompare routes
app.include_router(index_router)  # StableYield Index routes
app.include_router(production_router)  # Production status routes
app.include_router(policy_router, prefix="/api")  # Protocol policy routes
app.include_router(liquidity_router, prefix="/api")  # Liquidity filtering routes
app.include_router(sanitization_router, prefix="/api")  # Yield sanitization routes
app.include_router(ray_router, prefix="/api")  # Risk-Adjusted Yield (RAY) and SYI routes
app.include_router(websocket_router, prefix="/api")  # WebSocket streaming routes (STEP 6)
app.include_router(analytics_router, prefix="/api")  # Batch analytics routes (STEP 7)
app.include_router(ml_router, prefix="/api")  # Machine Learning routes (STEP 8)
app.include_router(enterprise_router, prefix="/api")  # Enterprise Integration routes (STEP 9)

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
    logger.info("StableYield Market Intelligence API v2.0.0 starting up...")
    
    # Start the StableYield Index scheduler
    try:
        from services.index_scheduler import start_index_scheduler
        await start_index_scheduler(db)
        logger.info("✅ StableYield Index scheduler started - calculating every 1 minute")
    except Exception as e:
        logger.error(f"❌ Failed to start index scheduler: {e}")
    
    # Start WebSocket services for real-time streaming (STEP 6)
    try:
        from services.cryptocompare_websocket import start_cryptocompare_websocket
        from services.realtime_data_integrator import start_realtime_integration
        
        # Start CryptoCompare WebSocket client
        await start_cryptocompare_websocket()
        logger.info("✅ CryptoCompare WebSocket client started")
        
        # Start real-time data integrator
        await start_realtime_integration()
        logger.info("✅ Real-time data integrator started")
    except Exception as e:
        logger.error(f"❌ Failed to start WebSocket services: {e}")
        logger.info("⚠️ Continuing without real-time WebSocket features")
    
    # Start Batch Analytics services (STEP 7)
    try:
        from services.batch_analytics_service import start_batch_analytics
        
        # Start batch analytics scheduler
        await start_batch_analytics()
        logger.info("✅ Batch analytics service started")
    except Exception as e:
        logger.error(f"❌ Failed to start batch analytics service: {e}")
        logger.info("⚠️ Continuing without batch analytics features")
    
    # Start Machine Learning services (STEP 8)
    try:
        from services.ml_insights_service import start_ml_insights
        
        # Start ML insights service
        await start_ml_insights()
        logger.info("✅ ML Insights service started")
    except Exception as e:
        logger.error(f"❌ Failed to start ML insights service: {e}")
        logger.info("⚠️ Continuing without ML features")
    
    # Start Enterprise API Gateway services (STEP 9)
    try:
        from services.api_gateway_service import start_api_gateway
        
        # Start API Gateway service
        await start_api_gateway()
        logger.info("✅ Enterprise API Gateway service started")
    except Exception as e:
        logger.error(f"❌ Failed to start API Gateway service: {e}")
        logger.info("⚠️ Continuing without enterprise features")
    
    logger.info("New capabilities enabled:")
    logger.info("  - Real-time StableYield Index calculation")
    logger.info("  - Real-time peg stability monitoring")
    logger.info("  - Liquidity depth analysis")
    logger.info("  - Risk-adjusted yield calculations")
    logger.info("  - Professional market intelligence endpoints")
    logger.info("Available endpoints:")
    logger.info("  - GET /api/index/current (Current StableYield Index)")
    logger.info("  - GET /api/index/live (Live ticker data)")
    logger.info("  - GET /api/index/history (Historical index data)")
    logger.info("  - GET /api/index/constituents (Index constituents)")
    logger.info("  - GET /api/v1/stablecoins/metrics (Peg & liquidity metrics)")
    logger.info("  - GET /api/v1/strategies/risk-adjusted-yield (Risk-adjusted yields)")
    logger.info("  - GET /api/v1/peg-stability/ranking (Peg stability ranking)")  
    logger.info("  - GET /api/v1/liquidity/analysis (Liquidity analysis)")
    logger.info("NEW STEP 5 (RAY & SYI) ENDPOINTS:")
    logger.info("  - GET /api/ray/methodology (RAY calculation methodology)")
    logger.info("  - POST /api/ray/calculate (Calculate RAY for single yield)")
    logger.info("  - GET /api/ray/market-analysis (Market RAY analysis)")
    logger.info("  - GET /api/syi/composition (SYI composition with RAY)")
    logger.info("  - GET /api/syi/methodology (SYI methodology)")
    logger.info("NEW STEP 6 (WEBSOCKET STREAMING) ENDPOINTS:")
    logger.info("  - GET /api/websocket/status (WebSocket connection status)")
    logger.info("  - GET /api/realtime/peg-metrics (Real-time peg stability)")
    logger.info("  - GET /api/realtime/liquidity-metrics (Real-time liquidity)")
    logger.info("  - POST /api/websocket/start (Start WebSocket services)")
    logger.info("  - WS /api/stream/syi/live (Live SYI WebSocket stream)")
    logger.info("  - WS /api/stream/peg-metrics (Peg metrics WebSocket stream)")
    logger.info("  - WS /api/stream/liquidity-metrics (Liquidity WebSocket stream)")
    logger.info("NEW STEP 7 (BATCH ANALYTICS) ENDPOINTS:")
    logger.info("  - GET /api/analytics/status (Batch analytics service status)")
    logger.info("  - POST /api/analytics/start (Start batch analytics service)")
    logger.info("  - POST /api/analytics/jobs/{job_name}/run (Run job manually)")
    logger.info("  - GET /api/analytics/peg-stability (Peg stability analytics)")
    logger.info("  - GET /api/analytics/liquidity (Liquidity analytics)")
    logger.info("  - GET /api/analytics/risk (Advanced risk analytics)")
    logger.info("  - GET /api/analytics/performance (Index performance analytics)")
    logger.info("  - GET /api/analytics/compliance-report (Compliance reporting)")
    logger.info("  - GET /api/analytics/historical-data (Historical data export)")
    logger.info("  - GET /api/analytics/summary (Comprehensive analytics summary)")
    logger.info("NEW STEP 8 (MACHINE LEARNING & AI) ENDPOINTS:")
    logger.info("  - GET /api/ml/status (ML service status and model information)")
    logger.info("  - POST /api/ml/start (Start ML insights service)")
    logger.info("  - GET /api/ml/predictions (Multi-horizon yield predictions)")
    logger.info("  - GET /api/ml/anomalies (AI-powered anomaly detection)")
    logger.info("  - GET /api/ml/insights (AI market insights & recommendations)")
    logger.info("  - GET /api/ml/predictions/{symbol} (Symbol-specific predictions)")
    logger.info("  - POST /api/ml/retrain (Retrain ML models)")
    logger.info("  - GET /api/ml/model-performance (Model performance metrics)")
    logger.info("  - GET /api/ml/feature-importance (Feature importance analysis)")
    logger.info("  - GET /api/ml/summary (Comprehensive ML service summary)")

@app.on_event("shutdown")
async def shutdown_db_client():
    try:
        # Stop the index scheduler
        from services.index_scheduler import stop_index_scheduler
        await stop_index_scheduler()
        logger.info("✅ StableYield Index scheduler stopped")
    except Exception as e:
        logger.error(f"❌ Error stopping scheduler: {e}")
    
    # Stop WebSocket services
    try:
        from services.realtime_data_integrator import stop_realtime_integration
        from services.cryptocompare_websocket import stop_cryptocompare_websocket
        
        await stop_realtime_integration()
        await stop_cryptocompare_websocket()
        logger.info("✅ WebSocket services stopped")
    except Exception as e:
        logger.error(f"❌ Error stopping WebSocket services: {e}")
    
    # Stop batch analytics services
    try:
        from services.batch_analytics_service import stop_batch_analytics
        
        await stop_batch_analytics()
        logger.info("✅ Batch analytics service stopped")
    except Exception as e:
        logger.error(f"❌ Error stopping batch analytics service: {e}")
    
    # Stop ML insights service
    try:
        from services.ml_insights_service import stop_ml_insights
        
        await stop_ml_insights()
        logger.info("✅ ML Insights service stopped")
    except Exception as e:
        logger.error(f"❌ Error stopping ML insights service: {e}")
    
    # Stop API Gateway service
    try:
        from services.api_gateway_service import stop_api_gateway
        
        await stop_api_gateway()
        logger.info("✅ Enterprise API Gateway service stopped")
    except Exception as e:
        logger.error(f"❌ Error stopping API Gateway service: {e}")
    
    client.close()
    logger.info("StableYield Market Intelligence API shutting down...")