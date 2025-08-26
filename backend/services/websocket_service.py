"""
WebSocket Service for StableYield Index Real-Time Streaming
Handles WebSocket connections for live index updates and data streaming
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Set, Optional
import websockets
from websockets.server import WebSocketServerProtocol
from dataclasses import asdict

logger = logging.getLogger(__name__)

class WebSocketConnectionManager:
    """Manages WebSocket connections and broadcasting"""
    
    def __init__(self):
        self.connections: Dict[str, Set[WebSocketServerProtocol]] = {
            'syi_live': set(),
            'constituents': set(),
            'ray_all': set(),
            'peg_metrics': set(),
            'liquidity_metrics': set()
        }
        self.connection_count = 0
    
    async def connect(self, websocket: WebSocketServerProtocol, stream_type: str):
        """Add new WebSocket connection"""
        if stream_type in self.connections:
            self.connections[stream_type].add(websocket)
            self.connection_count += 1
            logger.info(f"✅ WebSocket connected to {stream_type} (total: {self.connection_count})")
            
            # Send welcome message
            await self._send_welcome_message(websocket, stream_type)
        else:
            await websocket.close(code=4000, reason="Invalid stream type")
    
    async def disconnect(self, websocket: WebSocketServerProtocol):
        """Remove WebSocket connection"""
        for stream_type, connections in self.connections.items():
            if websocket in connections:
                connections.remove(websocket)
                self.connection_count -= 1
                logger.info(f"❌ WebSocket disconnected from {stream_type} (total: {self.connection_count})")
                break
    
    async def broadcast_to_stream(self, stream_type: str, data: Dict):
        """Broadcast data to all connections in a stream"""
        if stream_type not in self.connections:
            return
        
        connections = self.connections[stream_type].copy()
        if not connections:
            return
        
        message = json.dumps({
            'type': stream_type,
            'timestamp': datetime.utcnow().isoformat(),
            'data': data
        })
        
        # Send to all connections concurrently
        disconnected = []
        for websocket in connections:
            try:
                await websocket.send(message)
            except websockets.exceptions.ConnectionClosed:
                disconnected.append(websocket)
            except Exception as e:
                logger.error(f"Error sending to WebSocket: {e}")
                disconnected.append(websocket)
        
        # Clean up disconnected websockets
        for websocket in disconnected:
            await self.disconnect(websocket)
        
        logger.debug(f"📡 Broadcasted to {len(connections) - len(disconnected)} {stream_type} connections")
    
    async def broadcast(self, stream_type: str, data: Dict):
        """Alias for broadcast_to_stream for compatibility"""
        await self.broadcast_to_stream(stream_type, data)
    
    async def _send_welcome_message(self, websocket: WebSocketServerProtocol, stream_type: str):
        """Send welcome message with stream info"""
        welcome = {
            'type': 'welcome',
            'stream': stream_type,
            'timestamp': datetime.utcnow().isoformat(),
            'message': f'Connected to StableYield {stream_type} stream'
        }
        await websocket.send(json.dumps(welcome))
    
    def get_connection_stats(self) -> Dict:
        """Get connection statistics"""
        return {
            'total_connections': self.connection_count,
            'streams': {
                stream: len(connections) 
                for stream, connections in self.connections.items()
            }
        }

class WebSocketService:
    """Main WebSocket service for StableYield Index streaming"""
    
    def __init__(self, index_storage=None):
        self.manager = WebSocketConnectionManager()
        self.index_storage = index_storage
        self.running = False
        self.server = None
        
        # Stream configurations
        self.stream_configs = {
            'syi': {
                'path': '/stream/syi/live',
                'update_interval': 60,  # 1 minute
                'description': 'Live StableYield Index updates'
            },
            'constituents': {
                'path': '/stream/constituents/all', 
                'update_interval': 60,
                'description': 'All constituent updates'
            },
            'ray': {
                'path': '/stream/ray/all',
                'update_interval': 300,  # 5 minutes
                'description': 'Risk-Adjusted Yield updates'
            },
            'metrics': {
                'path': '/stream/metrics/peg',
                'update_interval': 180,  # 3 minutes
                'description': 'Peg stability metrics'
            }
        }
    
    async def start_server(self, host: str = "0.0.0.0", port: int = 8002):
        """Start WebSocket server"""
        try:
            self.server = await websockets.serve(
                self.handle_connection,
                host,
                port,
                ping_interval=30,
                ping_timeout=10,
                close_timeout=10,
                max_size=2**20,  # 1MB max message size
                max_queue=32
            )
            
            self.running = True
            logger.info(f"🚀 WebSocket server started on ws://{host}:{port}")
            
            # Start background tasks
            asyncio.create_task(self._periodic_index_broadcast())
            asyncio.create_task(self._periodic_stats_log())
            
            return self.server
            
        except Exception as e:
            logger.error(f"❌ Failed to start WebSocket server: {e}")
            raise
    
    async def stop_server(self):
        """Stop WebSocket server"""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            self.running = False
            logger.info("✅ WebSocket server stopped")
    
    async def handle_connection(self, websocket: WebSocketServerProtocol, path: str):
        """Handle individual WebSocket connections"""
        try:
            # Determine stream type from path
            stream_type = self._get_stream_type_from_path(path)
            if not stream_type:
                await websocket.close(code=4000, reason="Invalid stream path")
                return
            
            # Add connection to manager
            await self.manager.connect(websocket, stream_type)
            
            # Send initial data
            await self._send_initial_data(websocket, stream_type)
            
            # Handle incoming messages (for subscriptions, etc.)
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self._handle_client_message(websocket, stream_type, data)
                except json.JSONDecodeError:
                    await websocket.send(json.dumps({
                        'type': 'error',
                        'message': 'Invalid JSON message'
                    }))
                except Exception as e:
                    logger.error(f"Error handling client message: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.debug("WebSocket connection closed normally")
        except Exception as e:
            logger.error(f"WebSocket connection error: {e}")
        finally:
            await self.manager.disconnect(websocket)
    
    def _get_stream_type_from_path(self, path: str) -> Optional[str]:
        """Extract stream type from WebSocket path"""
        if '/stream/syi/' in path:
            return 'syi_live'
        elif '/stream/constituents/' in path:
            return 'constituents'
        elif '/stream/ray/' in path:
            return 'ray_all'
        elif '/stream/metrics/' in path:
            return 'peg_metrics'
        return None
    
    async def _send_initial_data(self, websocket: WebSocketServerProtocol, stream_type: str):
        """Send initial data when client connects"""
        try:
            if stream_type == 'syi_live' and self.index_storage:
                # Send current index value
                current_index = await self.index_storage.get_latest_index_value()
                if current_index:
                    await websocket.send(json.dumps({
                        'type': 'initial_data',
                        'data': {
                            'value': current_index.value,
                            'timestamp': current_index.timestamp.isoformat(),
                            'constituents_count': len(current_index.constituents)
                        }
                    }))
            
        except Exception as e:
            logger.error(f"Error sending initial data: {e}")
    
    async def _handle_client_message(self, websocket: WebSocketServerProtocol, stream_type: str, data: Dict):
        """Handle messages from clients"""
        message_type = data.get('type')
        
        if message_type == 'subscribe':
            # Handle subscription preferences
            symbols = data.get('symbols', [])
            await websocket.send(json.dumps({
                'type': 'subscription_confirmed',
                'symbols': symbols
            }))
            
        elif message_type == 'ping':
            # Handle ping/pong
            await websocket.send(json.dumps({
                'type': 'pong',
                'timestamp': datetime.utcnow().isoformat()
            }))
    
    async def _periodic_index_broadcast(self):
        """Periodically broadcast index updates"""
        while self.running:
            try:
                if self.index_storage:
                    # Get latest index data
                    current_index = await self.index_storage.get_latest_index_value()
                    if current_index:
                        # Broadcast to SYI stream
                        await self.manager.broadcast_to_stream('syi_live', {
                            'value': current_index.value,
                            'timestamp': current_index.timestamp.isoformat(),
                            'constituents_count': len(current_index.constituents),
                            'methodology_version': current_index.methodology_version
                        })
                        
                        # Broadcast constituents data
                        constituents_data = []
                        for constituent in current_index.constituents:
                            constituents_data.append({
                                'symbol': constituent.symbol,
                                'weight': constituent.weight,
                                'ray': constituent.ray,
                                'peg_score': constituent.peg_score,
                                'liquidity_score': constituent.liquidity_score
                            })
                        
                        await self.manager.broadcast_to_stream('constituents', {
                            'constituents': constituents_data,
                            'index_value': current_index.value
                        })
                
                await asyncio.sleep(60)  # Broadcast every minute
                
            except Exception as e:
                logger.error(f"Error in periodic broadcast: {e}")
                await asyncio.sleep(30)  # Retry after 30 seconds
    
    async def _periodic_stats_log(self):
        """Log connection statistics periodically"""
        while self.running:
            try:
                stats = self.manager.get_connection_stats()
                if stats['total_connections'] > 0:
                    logger.info(f"📊 WebSocket stats: {stats}")
                
                await asyncio.sleep(300)  # Log every 5 minutes
                
            except Exception as e:
                logger.error(f"Error logging stats: {e}")
                await asyncio.sleep(60)
    
    # Public methods for broadcasting data from external services
    async def broadcast_index_update(self, index_data: Dict):
        """Broadcast index update to all connected clients"""
        await self.manager.broadcast_to_stream('syi_live', index_data)
    
    async def broadcast_ray_update(self, ray_data: Dict):
        """Broadcast RAY update to all connected clients"""  
        await self.manager.broadcast_to_stream('ray_all', ray_data)
    
    async def broadcast_peg_metrics(self, peg_data: Dict):
        """Broadcast peg stability metrics"""
        await self.manager.broadcast_to_stream('peg_metrics', peg_data)
    
    def get_service_status(self) -> Dict:
        """Get WebSocket service status"""
        return {
            'running': self.running,
            'server_running': self.server is not None,
            'connections': self.manager.get_connection_stats(),
            'streams_available': list(self.stream_configs.keys())
        }

# Global WebSocket service instance
_websocket_service = None

async def get_websocket_service(index_storage=None) -> WebSocketService:
    """Get or create global WebSocket service instance"""
    global _websocket_service
    if _websocket_service is None:
        _websocket_service = WebSocketService(index_storage)
    return _websocket_service

async def start_websocket_server(index_storage=None, host: str = "0.0.0.0", port: int = 8002):
    """Start the global WebSocket server"""
    service = await get_websocket_service(index_storage)
    return await service.start_server(host, port)

async def stop_websocket_server():
    """Stop the global WebSocket server"""
    global _websocket_service
    if _websocket_service:
        await _websocket_service.stop_server()

# TODO: PRODUCTION IMPLEMENTATION CHECKLIST
# 1. Add authentication and authorization for WebSocket connections
# 2. Implement rate limiting to prevent abuse
# 3. Add SSL/TLS support for secure WebSocket connections (WSS)
# 4. Set up load balancing for multiple WebSocket server instances
# 5. Add comprehensive monitoring and alerting
# 6. Implement message queuing for high availability
# 7. Add data compression for large messages
# 8. Set up proper logging and observability
# 9. Add circuit breaker pattern for external dependencies
# 10. Implement graceful shutdown and connection draining