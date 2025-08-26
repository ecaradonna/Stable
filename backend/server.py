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
from routes.devops_routes import router as devops_router
from routes.trading_routes import router as trading_router
from routes.dashboard_routes import router as dashboard_router
from routes.ai_portfolio_routes import router as ai_portfolio_router

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
app.include_router(devops_router, prefix="/api")  # DevOps & Production routes (STEP 10)
app.include_router(trading_router, prefix="/api/trading")  # Advanced Trading Engine routes (STEP 11)
app.include_router(dashboard_router, prefix="/api/dashboard")  # Advanced Analytics Dashboard routes (STEP 12)
app.include_router(ai_portfolio_router, prefix="/api/ai-portfolio")  # AI Portfolio Management routes (STEP 13)

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
    logger.info("⚠️ EMERGENCY STARTUP MODE: Starting essential services only for AI Portfolio testing")
    
    # TEMPORARILY DISABLED: Problematic services that are preventing startup
    # - Index scheduler (validation errors)
    # - WebSocket services (connection loops)
    # - Other background services
    
    # Start AI-Powered Portfolio Management services (STEP 13) - PRIORITY FOR TESTING
    try:
        from services.ai_portfolio_service import start_ai_portfolio
        
        # Start AI Portfolio service
        await start_ai_portfolio()
        logger.info("✅ AI-Powered Portfolio Management service started")
    except Exception as e:
        logger.error(f"❌ Failed to start AI Portfolio service: {e}")
        logger.info("⚠️ Continuing without AI portfolio features")
    
    # Start Trading Engine (needed for AI Portfolio integration)
    try:
        from services.trading_engine_service import start_trading_engine
        
        # Start Trading Engine service
        await start_trading_engine()
        logger.info("✅ Advanced Trading Engine service started")
    except Exception as e:
        logger.error(f"❌ Failed to start Trading Engine service: {e}")
        logger.info("⚠️ Continuing without trading features")
    
    logger.info("✅ Emergency Startup Complete - Essential services running")
    logger.info("🎯 STEP 13 AI Portfolio Management endpoints available:")
    logger.info("  - GET /api/ai-portfolio/status (AI Portfolio service status)")
    logger.info("  - POST /api/ai-portfolio/start (Start AI Portfolio service)")
    logger.info("  - POST /api/ai-portfolio/portfolios (Create AI-managed portfolio)")
    logger.info("  - POST /api/ai-portfolio/rebalancing-signal/{portfolio_id} (Generate rebalancing signal)")
    logger.info("  - POST /api/ai-portfolio/execute-rebalancing/{signal_id} (Execute rebalancing)")
    logger.info("  - GET /api/ai-portfolio/summary (AI Portfolio comprehensive summary)")
    logger.info("Ready for AI Portfolio Management testing!")

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
    
    # Stop DevOps service
    try:
        from services.devops_service import stop_devops
        
        await stop_devops()
        logger.info("✅ DevOps & Production service stopped")
    except Exception as e:
        logger.error(f"❌ Error stopping DevOps service: {e}")
    
    # Stop Trading Engine service
    try:
        from services.trading_engine_service import stop_trading_engine
        
        await stop_trading_engine()
        logger.info("✅ Advanced Trading Engine service stopped")
    except Exception as e:
        logger.error(f"❌ Error stopping Trading Engine service: {e}")
    
    # Stop Dashboard service
    try:
        from services.dashboard_service import stop_dashboard
        
        await stop_dashboard()
        logger.info("✅ Advanced Analytics Dashboard service stopped")
    except Exception as e:
        logger.error(f"❌ Error stopping Dashboard service: {e}")
    
    # Stop AI Portfolio service
    try:
        from services.ai_portfolio_service import stop_ai_portfolio
        
        await stop_ai_portfolio()
        logger.info("✅ AI-Powered Portfolio Management service stopped")
    except Exception as e:
        logger.error(f"❌ Error stopping AI Portfolio service: {e}")
    
    client.close()
    logger.info("StableYield Market Intelligence API shutting down...")