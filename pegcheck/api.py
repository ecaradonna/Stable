"""
FastAPI server for PegCheck
Usage: uvicorn pegcheck.api:app --reload --port 8000
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict, Any
import asyncio
from datetime import datetime

from .core.config import DEFAULT_SYMBOLS
from .core.compute import compute_peg_analysis
from .sources import coingecko, cryptocompare, chainlink, uniswap

# Create FastAPI app
app = FastAPI(
    title="PegCheck API",
    description="Stablecoin Peg Monitoring System - Real-time peg stability analysis",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "pegcheck-api",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@app.get("/peg-check")
async def peg_check(
    symbols: str = Query(
        default="USDT,USDC,DAI,BUSD",
        description="Comma-separated list of symbols to check"
    ),
    with_oracle: bool = Query(
        default=False,
        description="Include Chainlink oracle data"
    ),
    with_dex: bool = Query(
        default=False, 
        description="Include Uniswap v3 TWAP data"
    ),
    twap_seconds: int = Query(
        default=1800,
        description="TWAP window in seconds (default: 30 minutes)"
    ),
    auto_pool: bool = Query(
        default=True,
        description="Auto-discover pools via subgraph"
    )
):
    """
    Perform peg check analysis for specified stablecoins
    
    Returns comprehensive peg stability analysis including:
    - Current prices from multiple sources
    - Deviation from $1.00 peg in basis points
    - Peg status (normal/warning/depeg)
    - Cross-reference consistency between sources
    """
    try:
        # Parse symbols
        symbol_list = [s.strip().upper() for s in symbols.split(',') if s.strip()]
        if not symbol_list:
            raise HTTPException(status_code=400, detail="No valid symbols provided")
        
        # Validate symbols
        max_symbols = 20
        if len(symbol_list) > max_symbols:
            raise HTTPException(
                status_code=400, 
                detail=f"Too many symbols. Maximum {max_symbols} allowed."
            )
        
        # Fetch data from CeFi sources
        cg_prices = coingecko.fetch(symbol_list)
        cc_prices = cryptocompare.fetch(symbol_list)
        
        # Optional: Chainlink oracles
        chainlink_prices = None
        if with_oracle:
            # TODO: Implement chainlink module when needed
            chainlink_prices = {}
        
        # Optional: Uniswap v3 TWAP  
        uniswap_prices = None
        if with_dex:
            # TODO: Implement uniswap module when needed
            uniswap_prices = {}
        
        # Compute peg analysis
        payload = compute_peg_analysis(
            coingecko_prices=cg_prices,
            cryptocompare_prices=cc_prices,
            chainlink_prices=chainlink_prices,
            uniswap_prices=uniswap_prices,
            symbols=symbol_list
        )
        
        # Convert to API response format
        response = {
            "success": True,
            "timestamp": datetime.utcnow().isoformat(),
            "as_of": payload.as_of,
            "symbols": payload.symbols,
            "data_sources": {
                "coingecko": payload.coingecko,
                "cryptocompare": payload.cryptocompare
            },
            "reports": [
                {
                    "symbol": r.symbol,
                    "price_usd": r.avg_ref,
                    "deviation": {
                        "absolute": r.abs_diff,
                        "percentage": r.pct_diff,
                        "basis_points": r.bps_diff
                    },
                    "peg_status": r.status.value,
                    "is_depegged": r.is_depeg,
                    "confidence": r.confidence,
                    "sources_used": r.sources_used
                } for r in payload.reports
            ],
            "summary": {
                "total_symbols": len(payload.symbols),
                "depegged_count": payload.total_depegs,
                "max_deviation_bps": payload.max_deviation_bps,
                "sources_consistency": payload.cefi_consistency
            },
            "config": payload.config
        }
        
        # Add optional data if requested
        if with_oracle and chainlink_prices:
            response["data_sources"]["chainlink"] = chainlink_prices
        
        if with_dex and uniswap_prices:
            response["data_sources"]["uniswap"] = uniswap_prices
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/symbols")
async def get_supported_symbols():
    """Get list of supported stablecoin symbols"""
    return {
        "supported_symbols": DEFAULT_SYMBOLS,
        "description": "List of stablecoin symbols supported by PegCheck",
        "total_count": len(DEFAULT_SYMBOLS),
        "note": "Additional symbols may be supported if available in data sources"
    }

@app.get("/sources")
async def get_data_sources():
    """Get information about available data sources"""
    return {
        "data_sources": {
            "coingecko": {
                "name": "CoinGecko",
                "type": "CeFi",
                "description": "Primary CeFi price reference",
                "status": "active"
            },
            "cryptocompare": {
                "name": "CryptoCompare", 
                "type": "CeFi",
                "description": "Secondary CeFi price reference for redundancy",
                "status": "active"
            },
            "chainlink": {
                "name": "Chainlink Oracles",
                "type": "Oracle",
                "description": "On-chain price feeds (requires ETH_RPC_URL)",
                "status": "optional"
            },
            "uniswap": {
                "name": "Uniswap v3 TWAP",
                "type": "DEX",
                "description": "Time-weighted average price from Uniswap v3",
                "status": "optional"
            }
        },
        "methodology": {
            "primary_sources": ["coingecko", "cryptocompare"],
            "reference_calculation": "Weighted average (CoinGecko 70%, CryptoCompare 30%)",
            "peg_target": 1.00,
            "thresholds": {
                "warning": "25 basis points",
                "depeg": "50 basis points"
            }
        }
    }

@app.get("/status")
async def get_service_status():
    """Get detailed service status and configuration"""
    import os
    
    # Check API key configuration
    cryptocompare_configured = bool(os.getenv("CRYPTOCOMPARE_API_KEY"))
    eth_rpc_configured = bool(os.getenv("ETH_RPC_URL"))
    
    return {
        "service": "PegCheck API",
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
        "configuration": {
            "cryptocompare_api": "configured" if cryptocompare_configured else "not_configured",
            "ethereum_rpc": "configured" if eth_rpc_configured else "not_configured",
            "chainlink_support": eth_rpc_configured,
            "uniswap_support": eth_rpc_configured
        },
        "capabilities": {
            "cefi_monitoring": True,
            "oracle_monitoring": eth_rpc_configured,
            "dex_monitoring": eth_rpc_configured,
            "historical_analysis": True
        },
        "endpoints": [
            "/health",
            "/peg-check",
            "/symbols", 
            "/sources",
            "/status"
        ]
    }

# Optional: Add example endpoint for testing
@app.get("/example")
async def example_peg_check():
    """Example peg check with default stablecoins"""
    return await peg_check(symbols="USDT,USDC,DAI")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)