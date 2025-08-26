"""
WebSocket Routes (STEP 6)
API endpoints for WebSocket streaming and real-time data management
"""

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from typing import Dict, Any, List
import logging
import json
from datetime import datetime

from services.cryptocompare_websocket import get_cryptocompare_client
from services.realtime_data_integrator import get_realtime_integrator
from services.websocket_service import WebSocketConnectionManager

logger = logging.getLogger(__name__)
router = APIRouter()

# Global WebSocket connection manager
websocket_manager = WebSocketConnectionManager()

@router.get("/websocket/status")
async def get_websocket_status() -> Dict[str, Any]:
    """Get WebSocket connection and streaming status"""
    try:
        # Get CryptoCompare WebSocket status
        cc_client = get_cryptocompare_client()
        cc_status = cc_client.get_connection_status() if cc_client else {"is_connected": False}
        
        # Get real-time integrator status
        rt_integrator = get_realtime_integrator()
        rt_status = rt_integrator.get_realtime_status() if rt_integrator else {"is_running": False}
        
        return {
            "cryptocompare_websocket": cc_status,
            "realtime_integrator": rt_status,
            "websocket_connections": {
                "total_connections": websocket_manager.connection_count,
                "connections_by_stream": {
                    stream_type: len(connections) 
                    for stream_type, connections in websocket_manager.connections.items()
                }
            },
            "status_timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting WebSocket status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get WebSocket status")

@router.get("/realtime/peg-metrics")
async def get_realtime_peg_metrics() -> Dict[str, Any]:
    """Get real-time peg stability metrics"""
    try:
        rt_integrator = get_realtime_integrator()
        if not rt_integrator:
            return {
                "message": "Real-time integration not available",
                "peg_metrics": {}
            }
        
        peg_metrics = rt_integrator.get_peg_metrics()
        
        return {
            "peg_metrics": peg_metrics,
            "symbols_tracked": list(peg_metrics.keys()),
            "last_updated": datetime.utcnow().isoformat(),
            "data_source": "cryptocompare_websocket"
        }
    except Exception as e:
        logger.error(f"Error getting real-time peg metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get real-time peg metrics")

@router.get("/realtime/liquidity-metrics")
async def get_realtime_liquidity_metrics() -> Dict[str, Any]:
    """Get real-time liquidity metrics"""
    try:
        rt_integrator = get_realtime_integrator()
        if not rt_integrator:
            return {
                "message": "Real-time integration not available",
                "liquidity_metrics": {}
            }
        
        liquidity_metrics = rt_integrator.get_liquidity_metrics()
        
        return {
            "liquidity_metrics": liquidity_metrics,
            "symbols_tracked": list(liquidity_metrics.keys()),
            "last_updated": datetime.utcnow().isoformat(),
            "data_source": "cryptocompare_websocket"
        }
    except Exception as e:
        logger.error(f"Error getting real-time liquidity metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get real-time liquidity metrics")

@router.post("/websocket/start")
async def start_websocket_services() -> Dict[str, Any]:
    """Start WebSocket services (CryptoCompare client and real-time integrator)"""
    try:
        from services.cryptocompare_websocket import start_cryptocompare_websocket
        from services.realtime_data_integrator import start_realtime_integration
        
        # Start CryptoCompare WebSocket client
        await start_cryptocompare_websocket()
        
        # Start real-time data integrator
        await start_realtime_integration()
        
        return {
            "message": "WebSocket services started successfully",
            "services_started": [
                "cryptocompare_websocket",
                "realtime_data_integrator"
            ],
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error starting WebSocket services: {e}")
        raise HTTPException(status_code=500, detail="Failed to start WebSocket services")

@router.post("/websocket/stop")
async def stop_websocket_services() -> Dict[str, Any]:
    """Stop WebSocket services"""
    try:
        from services.cryptocompare_websocket import stop_cryptocompare_websocket
        from services.realtime_data_integrator import stop_realtime_integration
        
        # Stop real-time data integrator
        await stop_realtime_integration()
        
        # Stop CryptoCompare WebSocket client
        await stop_cryptocompare_websocket()
        
        return {
            "message": "WebSocket services stopped successfully",
            "services_stopped": [
                "realtime_data_integrator",
                "cryptocompare_websocket"
            ],
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error stopping WebSocket services: {e}")
        raise HTTPException(status_code=500, detail="Failed to stop WebSocket services")

# WebSocket streaming endpoints
@router.websocket("/stream/syi/live")
async def websocket_syi_live(websocket: WebSocket):
    """WebSocket endpoint for live StableYield Index updates"""
    await websocket.accept()
    await websocket_manager.connect(websocket, 'syi_live')
    
    try:
        while True:
            # Keep connection alive and handle incoming messages
            try:
                data = await websocket.receive_text()
                # Echo back for keep-alive (client can send ping)
                if data == "ping":
                    await websocket.send_text("pong")
            except WebSocketDisconnect:
                logger.info("WebSocket disconnected from SYI live stream")
                break
    except Exception as e:
        logger.error(f"Error in SYI live WebSocket: {e}")
    finally:
        await websocket_manager.disconnect(websocket)

@router.websocket("/stream/peg-metrics")
async def websocket_peg_metrics(websocket: WebSocket):
    """WebSocket endpoint for real-time peg stability metrics"""
    await websocket.accept()
    await websocket_manager.connect(websocket, 'peg_metrics')
    
    try:
        while True:
            try:
                data = await websocket.receive_text()
                if data == "ping":
                    await websocket.send_text("pong")
            except WebSocketDisconnect:
                logger.info("WebSocket disconnected from peg metrics stream")
                break
    except Exception as e:
        logger.error(f"Error in peg metrics WebSocket: {e}")
    finally:
        await websocket_manager.disconnect(websocket)

@router.websocket("/stream/liquidity-metrics")
async def websocket_liquidity_metrics(websocket: WebSocket):
    """WebSocket endpoint for real-time liquidity metrics"""
    await websocket.accept()
    await websocket_manager.connect(websocket, 'liquidity_metrics')
    
    try:
        while True:
            try:
                data = await websocket.receive_text()
                if data == "ping":
                    await websocket.send_text("pong")
            except WebSocketDisconnect:
                logger.info("WebSocket disconnected from liquidity metrics stream")
                break
    except Exception as e:
        logger.error(f"Error in liquidity metrics WebSocket: {e}")
    finally:
        await websocket_manager.disconnect(websocket)

@router.websocket("/stream/ray/all")
async def websocket_ray_all(websocket: WebSocket):
    """WebSocket endpoint for all RAY (Risk-Adjusted Yield) updates"""
    await websocket.accept()
    await websocket_manager.connect(websocket, 'ray_all')
    
    try:
        while True:
            try:
                data = await websocket.receive_text()
                if data == "ping":
                    await websocket.send_text("pong")
            except WebSocketDisconnect:
                logger.info("WebSocket disconnected from RAY all stream")
                break
    except Exception as e:
        logger.error(f"Error in RAY all WebSocket: {e}")
    finally:
        await websocket_manager.disconnect(websocket)

@router.websocket("/stream/constituents")
async def websocket_constituents(websocket: WebSocket):
    """WebSocket endpoint for SYI constituents updates"""
    await websocket.accept()
    await websocket_manager.connect(websocket, 'constituents')
    
    try:
        while True:
            try:
                data = await websocket.receive_text()
                if data == "ping":
                    await websocket.send_text("pong")
            except WebSocketDisconnect:
                logger.info("WebSocket disconnected from constituents stream")
                break
    except Exception as e:
        logger.error(f"Error in constituents WebSocket: {e}")
    finally:
        await websocket_manager.disconnect(websocket)

@router.get("/websocket/test-data")
async def get_websocket_test_data() -> Dict[str, Any]:
    """Get test data for WebSocket streaming (for development/testing)"""
    try:
        return {
            "test_syi_update": {
                "type": "syi_live_update",
                "data": {
                    "index_value": 1.0456,
                    "constituent_count": 6,
                    "calculation_timestamp": datetime.utcnow().isoformat(),
                    "quality_metrics": {
                        "overall_quality": 0.85,
                        "avg_confidence": 0.78
                    }
                },
                "timestamp": datetime.utcnow().isoformat()
            },
            "test_peg_update": {
                "type": "peg_metrics_update",
                "data": {
                    "USDT": {
                        "symbol": "USDT",
                        "current_price": 1.0001,
                        "current_deviation": 0.0001,
                        "peg_stability_score": 0.995,
                        "assessment": "Excellent"
                    },
                    "USDC": {
                        "symbol": "USDC",
                        "current_price": 0.9999,
                        "current_deviation": 0.0001,
                        "peg_stability_score": 0.998,
                        "assessment": "Excellent"
                    }
                },
                "timestamp": datetime.utcnow().isoformat()
            },
            "test_liquidity_update": {
                "type": "liquidity_metrics_update",
                "data": {
                    "USDT": {
                        "symbol": "USDT",
                        "avg_spread_bps": 2.5,
                        "total_depth_usd": 5000000,
                        "liquidity_score": 0.92,
                        "assessment": "Excellent"
                    },
                    "USDC": {
                        "symbol": "USDC",
                        "avg_spread_bps": 1.8,
                        "total_depth_usd": 8000000,
                        "liquidity_score": 0.96,
                        "assessment": "Excellent"
                    }
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    except Exception as e:
        logger.error(f"Error generating test data: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate test data")

@router.post("/websocket/broadcast-test")
async def broadcast_test_data() -> Dict[str, Any]:
    """Broadcast test data to all connected WebSocket clients (for testing)"""
    try:
        # Broadcast test SYI update
        await websocket_manager.broadcast('syi_live', {
            "type": "syi_live_update",
            "data": {
                "index_value": 1.0456,
                "constituent_count": 6,
                "calculation_timestamp": datetime.utcnow().isoformat(),
                "quality_metrics": {"overall_quality": 0.85},
                "test_broadcast": True
            },
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Broadcast test peg metrics
        await websocket_manager.broadcast('peg_metrics', {
            "type": "peg_metrics_update",
            "data": {
                "USDT": {
                    "symbol": "USDT",
                    "current_price": 1.0001,
                    "peg_stability_score": 0.995,
                    "assessment": "Excellent",
                    "test_broadcast": True
                }
            },
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Get connection counts for response
        connections_notified = sum(len(conns) for conns in websocket_manager.connections.values())
        
        return {
            "message": "Test data broadcasted successfully",
            "connections_notified": connections_notified,
            "streams_updated": ["syi_live", "peg_metrics"],
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error broadcasting test data: {e}")
        raise HTTPException(status_code=500, detail="Failed to broadcast test data")