"""
CryptoCompare WebSocket Client Service (STEP 6)
Real-time streaming of price and market data from CryptoCompare WebSocket API
"""

import asyncio
import json
import websockets
import logging
from typing import Dict, Any, Callable, Optional, List
from datetime import datetime
import os
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class CCMessageType(Enum):
    TRADE = "0"
    CURRENT_QUOTE = "2"
    AGGREGATE_INDEX = "5"
    ORDERBOOK_L1 = "8"
    TICKER = "24"

@dataclass
class CCPriceUpdate:
    symbol: str
    price: float
    volume_24h: float
    timestamp: datetime
    source: str = "cryptocompare_ws"

@dataclass
class CCOrderBookUpdate:
    symbol: str
    bid_price: float
    bid_quantity: float
    ask_price: float
    ask_quantity: float
    timestamp: datetime
    source: str = "cryptocompare_ws"

class CryptoCompareWebSocketClient:
    """CryptoCompare WebSocket client for real-time data streaming"""
    
    def __init__(self):
        self.api_key = os.getenv('CC_API_KEY_STABLEYIELD', 'DEMO_KEY')
        self.base_url = "wss://streamer.cryptocompare.com/v2"
        self.connection = None
        self.is_connected = False
        self.subscriptions = set()
        self.price_callbacks = []
        self.orderbook_callbacks = []
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 10
        self.reconnect_delay = 5
        
        # StableYield Index constituents we want to track
        self.tracked_symbols = ['USDT', 'USDC', 'DAI', 'TUSD', 'FRAX', 'USDP', 'PYUSD']
        
    async def connect(self):
        """Establish WebSocket connection to CryptoCompare"""
        try:
            # Build connection URL with API key
            url = f"{self.base_url}?api_key={self.api_key}"
            
            logger.info(f"🔌 Connecting to CryptoCompare WebSocket...")
            self.connection = await websockets.connect(url)
            self.is_connected = True
            self.reconnect_attempts = 0
            
            logger.info("✅ Connected to CryptoCompare WebSocket")
            
            # Start listening for messages
            asyncio.create_task(self._listen_for_messages())
            
            # Subscribe to stablecoin data
            await self._subscribe_to_stablecoins()
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to CryptoCompare WebSocket: {e}")
            self.is_connected = False
            await self._schedule_reconnect()
    
    async def disconnect(self):
        """Disconnect from WebSocket"""
        if self.connection and not self.connection.closed:
            await self.connection.close()
        self.is_connected = False
        logger.info("❌ Disconnected from CryptoCompare WebSocket")
    
    async def _subscribe_to_stablecoins(self):
        """Subscribe to real-time data for stablecoin constituents"""
        try:
            # Subscribe to ticker data (price, volume, market cap)
            ticker_subscription = {
                "action": "SubAdd",
                "subs": [f"24~CCCAGG~{symbol}~USD" for symbol in self.tracked_symbols]
            }
            
            await self._send_message(ticker_subscription)
            
            # Subscribe to orderbook data for liquidity analysis
            orderbook_subscription = {
                "action": "SubAdd", 
                "subs": [f"8~CCCAGG~{symbol}~USD" for symbol in self.tracked_symbols]
            }
            
            await self._send_message(orderbook_subscription)
            
            # Subscribe to trade data for real-time price updates
            trade_subscription = {
                "action": "SubAdd",
                "subs": [f"0~CCCAGG~{symbol}~USD" for symbol in self.tracked_symbols]
            }
            
            await self._send_message(trade_subscription)
            
            logger.info(f"📡 Subscribed to real-time data for {len(self.tracked_symbols)} stablecoins")
            
        except Exception as e:
            logger.error(f"❌ Failed to subscribe to stablecoin data: {e}")
    
    async def _send_message(self, message: Dict[str, Any]):
        """Send message to WebSocket"""
        if self.connection and self.is_connected:
            try:
                await self.connection.send(json.dumps(message))
                logger.debug(f"📤 Sent: {message}")
            except Exception as e:
                logger.error(f"❌ Failed to send message: {e}")
                await self._handle_connection_error()
    
    async def _listen_for_messages(self):
        """Listen for incoming WebSocket messages"""
        try:
            async for message in self.connection:
                try:
                    await self._process_message(message)
                except Exception as e:
                    logger.error(f"❌ Error processing message: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.warning("🔌 WebSocket connection closed")
            self.is_connected = False
            await self._schedule_reconnect()
        except Exception as e:
            logger.error(f"❌ Error in message listener: {e}")
            await self._handle_connection_error()
    
    async def _process_message(self, raw_message: str):
        """Process incoming WebSocket message"""
        try:
            # CryptoCompare sends messages in a specific format
            data = json.loads(raw_message)
            
            # Handle different message types
            if isinstance(data, dict):
                message_type = data.get("TYPE")
                
                if message_type == "24":  # Ticker data
                    await self._handle_ticker_message(data)
                elif message_type == "0":  # Trade data
                    await self._handle_trade_message(data)
                elif message_type == "8":  # Orderbook L1
                    await self._handle_orderbook_message(data)
                elif message_type == "20":  # Welcome/status message
                    logger.info(f"📋 CryptoCompare status: {data}")
                else:
                    logger.debug(f"📨 Unhandled message type {message_type}: {data}")
                    
        except json.JSONDecodeError:
            logger.warning(f"❌ Invalid JSON received: {raw_message[:100]}...")
        except Exception as e:
            logger.error(f"❌ Error processing message: {e}")
    
    async def _handle_ticker_message(self, data: Dict[str, Any]):
        """Handle ticker (price/volume) message"""
        try:
            # Extract ticker data
            symbol = data.get("FROMSYMBOL", "").upper()
            if symbol not in self.tracked_symbols:
                return
            
            price = float(data.get("PRICE", 0))
            volume_24h = float(data.get("VOLUME24HOUR", 0))
            
            if price > 0:
                price_update = CCPriceUpdate(
                    symbol=symbol,
                    price=price,
                    volume_24h=volume_24h,
                    timestamp=datetime.utcnow(),
                    source="cryptocompare_ws"
                )
                
                # Notify all registered callbacks
                for callback in self.price_callbacks:
                    try:
                        await callback(price_update)
                    except Exception as e:
                        logger.error(f"❌ Error in price callback: {e}")
                
                logger.debug(f"💰 Price update: {symbol} = ${price:.4f} (Vol: ${volume_24h:,.0f})")
                
        except Exception as e:
            logger.error(f"❌ Error handling ticker message: {e}")
    
    async def _handle_trade_message(self, data: Dict[str, Any]):
        """Handle trade message for real-time price updates"""
        try:
            symbol = data.get("FSYM", "").upper()
            if symbol not in self.tracked_symbols:
                return
            
            price = float(data.get("P", 0))
            quantity = float(data.get("Q", 0))
            
            if price > 0:
                # Create price update from trade data
                price_update = CCPriceUpdate(
                    symbol=symbol,
                    price=price,
                    volume_24h=quantity,  # Use trade quantity as volume indicator
                    timestamp=datetime.utcnow(),
                    source="cryptocompare_ws_trade"
                )
                
                # Notify callbacks
                for callback in self.price_callbacks:
                    try:
                        await callback(price_update)
                    except Exception as e:
                        logger.error(f"❌ Error in trade callback: {e}")
                
                logger.debug(f"📈 Trade update: {symbol} = ${price:.4f} (Qty: {quantity})")
                
        except Exception as e:
            logger.error(f"❌ Error handling trade message: {e}")
    
    async def _handle_orderbook_message(self, data: Dict[str, Any]):
        """Handle orderbook L1 (best bid/ask) message"""
        try:
            symbol = data.get("FSYM", "").upper()
            if symbol not in self.tracked_symbols:
                return
            
            bid_price = float(data.get("BID", 0))
            ask_price = float(data.get("ASK", 0))
            bid_quantity = float(data.get("BIDQ", 0))
            ask_quantity = float(data.get("ASKQ", 0))
            
            if bid_price > 0 and ask_price > 0:
                orderbook_update = CCOrderBookUpdate(
                    symbol=symbol,
                    bid_price=bid_price,
                    bid_quantity=bid_quantity,
                    ask_price=ask_price,
                    ask_quantity=ask_quantity,
                    timestamp=datetime.utcnow(),
                    source="cryptocompare_ws"
                )
                
                # Notify orderbook callbacks
                for callback in self.orderbook_callbacks:
                    try:
                        await callback(orderbook_update)
                    except Exception as e:
                        logger.error(f"❌ Error in orderbook callback: {e}")
                
                spread = ask_price - bid_price
                spread_pct = (spread / bid_price) * 100 if bid_price > 0 else 0
                
                logger.debug(f"📊 Orderbook: {symbol} Bid=${bid_price:.4f} Ask=${ask_price:.4f} Spread={spread_pct:.3f}%")
                
        except Exception as e:
            logger.error(f"❌ Error handling orderbook message: {e}")
    
    async def _handle_connection_error(self):
        """Handle connection errors and attempt reconnection"""
        self.is_connected = False
        if self.connection:
            await self.connection.close()
        await self._schedule_reconnect()
    
    async def _schedule_reconnect(self):
        """Schedule reconnection attempt"""
        if self.reconnect_attempts < self.max_reconnect_attempts:
            self.reconnect_attempts += 1
            delay = self.reconnect_delay * (2 ** (self.reconnect_attempts - 1))  # Exponential backoff
            
            logger.info(f"🔄 Scheduling reconnect attempt {self.reconnect_attempts}/{self.max_reconnect_attempts} in {delay}s")
            
            await asyncio.sleep(delay)
            await self.connect()
        else:
            logger.error(f"❌ Max reconnection attempts ({self.max_reconnect_attempts}) reached. Giving up.")
    
    def register_price_callback(self, callback: Callable[[CCPriceUpdate], None]):
        """Register callback for price updates"""
        self.price_callbacks.append(callback)
        logger.info(f"📝 Registered price callback: {callback.__name__}")
    
    def register_orderbook_callback(self, callback: Callable[[CCOrderBookUpdate], None]):
        """Register callback for orderbook updates"""
        self.orderbook_callbacks.append(callback)
        logger.info(f"📝 Registered orderbook callback: {callback.__name__}")
    
    def get_connection_status(self) -> Dict[str, Any]:
        """Get current connection status"""
        return {
            "is_connected": self.is_connected,
            "reconnect_attempts": self.reconnect_attempts,
            "subscriptions": len(self.subscriptions),
            "tracked_symbols": self.tracked_symbols,
            "price_callbacks": len(self.price_callbacks),
            "orderbook_callbacks": len(self.orderbook_callbacks),
            "api_key_configured": self.api_key != 'DEMO_KEY'
        }

# Global WebSocket client instance
cc_websocket_client = None

async def start_cryptocompare_websocket():
    """Start the global CryptoCompare WebSocket client"""
    global cc_websocket_client
    
    if cc_websocket_client is None:
        cc_websocket_client = CryptoCompareWebSocketClient()
        await cc_websocket_client.connect()
        logger.info("🚀 CryptoCompare WebSocket client started")
    else:
        logger.info("⚠️ CryptoCompare WebSocket client already running")

async def stop_cryptocompare_websocket():
    """Stop the global CryptoCompare WebSocket client"""
    global cc_websocket_client
    
    if cc_websocket_client:
        await cc_websocket_client.disconnect()
        cc_websocket_client = None
        logger.info("🛑 CryptoCompare WebSocket client stopped")

def get_cryptocompare_client() -> Optional[CryptoCompareWebSocketClient]:
    """Get the global CryptoCompare WebSocket client"""
    return cc_websocket_client