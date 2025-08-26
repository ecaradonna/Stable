#!/usr/bin/env python3
"""
Minimal AI Portfolio Test Server
Tests AI portfolio endpoints without the full server complexity
"""

import asyncio
import sys
import os
sys.path.append('/app/backend')

from fastapi import FastAPI
from routes.ai_portfolio_routes import router as ai_portfolio_router
import uvicorn

# Create minimal app
app = FastAPI(title="AI Portfolio Test Server")
app.include_router(ai_portfolio_router, prefix="/api/ai-portfolio")

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "ai_portfolio_test"}

async def start_test_server():
    """Start the test server"""
    try:
        # Initialize AI portfolio service
        from services.ai_portfolio_service import start_ai_portfolio
        await start_ai_portfolio()
        print("✅ AI Portfolio Service started")
        
        # Start server
        config = uvicorn.Config(app, host="0.0.0.0", port=8002, log_level="info")
        server = uvicorn.Server(config)
        print("🚀 Starting AI Portfolio Test Server on port 8002...")
        await server.serve()
        
    except Exception as e:
        print(f"❌ Error starting test server: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(start_test_server())