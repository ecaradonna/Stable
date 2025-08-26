"""
Real-Time Data Integrator Service (STEP 6)
Integrates real-time WebSocket data with the existing yield and index calculation system
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import asdict
from collections import defaultdict, deque

from .cryptocompare_websocket import CCPriceUpdate, CCOrderBookUpdate, get_cryptocompare_client
from .websocket_service import WebSocketConnectionManager
from .yield_aggregator import YieldAggregator
from .ray_calculator import RAYCalculator
from .syi_compositor import SYICompositor

logger = logging.getLogger(__name__)

class RealTimeDataIntegrator:
    """Integrates real-time market data with StableYield calculations"""
    
    def __init__(self):
        self.websocket_manager = WebSocketConnectionManager()
        self.yield_aggregator = YieldAggregator()
        self.ray_calculator = RAYCalculator()
        self.syi_compositor = SYICompositor()
        
        # Price data cache (last 100 updates per symbol)
        self.price_cache: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        
        # Orderbook data cache (last 50 updates per symbol)
        self.orderbook_cache: Dict[str, deque] = defaultdict(lambda: deque(maxlen=50))
        
        # Peg stability metrics cache
        self.peg_metrics: Dict[str, Dict[str, Any]] = {}
        
        # Liquidity metrics cache
        self.liquidity_metrics: Dict[str, Dict[str, Any]] = {}
        
        # Last calculation timestamps
        self.last_peg_calculation = {}
        self.last_liquidity_calculation = {}
        self.last_syi_calculation = None
        
        # Calculation intervals (in seconds)
        self.peg_calculation_interval = 30  # 30 seconds
        self.liquidity_calculation_interval = 60  # 1 minute
        self.syi_calculation_interval = 60  # 1 minute
        
        # Real-time flags
        self.is_running = False
        self.tasks = []
    
    async def start(self):
        """Start the real-time data integration"""
        if self.is_running:
            logger.warning("⚠️ Real-time data integrator already running")
            return
        
        self.is_running = True
        logger.info("🚀 Starting real-time data integrator...")
        
        # Get CryptoCompare WebSocket client and register callbacks
        cc_client = get_cryptocompare_client()
        if cc_client:
            cc_client.register_price_callback(self._handle_price_update)
            cc_client.register_orderbook_callback(self._handle_orderbook_update)
            
            # Start background calculation tasks
            self.tasks = [
                asyncio.create_task(self._peg_stability_calculator()),
                asyncio.create_task(self._liquidity_metrics_calculator()),
                asyncio.create_task(self._syi_realtime_calculator()),
                asyncio.create_task(self._websocket_broadcaster())
            ]
            
            logger.info("✅ Real-time data integrator started")
        else:
            logger.error("❌ CryptoCompare WebSocket client not available")
    
    async def stop(self):
        """Stop the real-time data integration"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        # Cancel all background tasks
        for task in self.tasks:
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self.tasks, return_exceptions=True)
        
        logger.info("🛑 Real-time data integrator stopped")
    
    async def _handle_price_update(self, price_update: CCPriceUpdate):
        """Handle incoming price updates from WebSocket"""
        try:
            symbol = price_update.symbol
            
            # Add to price cache
            self.price_cache[symbol].append({
                'price': price_update.price,
                'volume_24h': price_update.volume_24h,
                'timestamp': price_update.timestamp,
                'source': price_update.source
            })
            
            logger.debug(f"💰 Cached price update: {symbol} = ${price_update.price:.4f}")
            
            # Trigger peg stability calculation if enough time has passed
            last_calc = self.last_peg_calculation.get(symbol, datetime.min)
            if (datetime.utcnow() - last_calc).total_seconds() >= self.peg_calculation_interval:
                await self._calculate_peg_stability(symbol)
                
        except Exception as e:
            logger.error(f"❌ Error handling price update: {e}")
    
    async def _handle_orderbook_update(self, orderbook_update: CCOrderBookUpdate):
        """Handle incoming orderbook updates from WebSocket"""
        try:
            symbol = orderbook_update.symbol
            
            # Add to orderbook cache
            self.orderbook_cache[symbol].append({
                'bid_price': orderbook_update.bid_price,
                'bid_quantity': orderbook_update.bid_quantity,
                'ask_price': orderbook_update.ask_price,
                'ask_quantity': orderbook_update.ask_quantity,
                'timestamp': orderbook_update.timestamp,
                'source': orderbook_update.source
            })
            
            # Calculate spread for liquidity analysis
            spread = orderbook_update.ask_price - orderbook_update.bid_price
            spread_pct = (spread / orderbook_update.bid_price) * 100 if orderbook_update.bid_price > 0 else 0
            
            logger.debug(f"📊 Cached orderbook: {symbol} Spread={spread_pct:.3f}%")
            
            # Trigger liquidity calculation if enough time has passed
            last_calc = self.last_liquidity_calculation.get(symbol, datetime.min)
            if (datetime.utcnow() - last_calc).total_seconds() >= self.liquidity_calculation_interval:
                await self._calculate_liquidity_metrics(symbol)
                
        except Exception as e:
            logger.error(f"❌ Error handling orderbook update: {e}")
    
    async def _calculate_peg_stability(self, symbol: str):
        """Calculate real-time peg stability metrics"""
        try:
            prices = list(self.price_cache[symbol])
            if len(prices) < 10:  # Need at least 10 data points
                return
            
            # Get recent prices (last 30 minutes worth)
            cutoff_time = datetime.utcnow() - timedelta(minutes=30)
            recent_prices = [p for p in prices if p['timestamp'] >= cutoff_time]
            
            if not recent_prices:
                return
            
            # Calculate peg stability metrics
            price_values = [p['price'] for p in recent_prices]
            target_peg = 1.0  # USD peg target
            
            # Calculate deviations from peg
            deviations = [abs(price - target_peg) for price in price_values]
            max_deviation = max(deviations)
            avg_deviation = sum(deviations) / len(deviations)
            current_deviation = abs(recent_prices[-1]['price'] - target_peg)
            
            # Calculate peg stability score (0-1, where 1 is perfect peg)
            # Penalize based on maximum deviation in the period
            if max_deviation <= 0.005:  # Within 0.5%
                peg_score = 1.0
            elif max_deviation <= 0.01:  # Within 1%
                peg_score = 0.95
            elif max_deviation <= 0.02:  # Within 2%
                peg_score = 0.85 - (max_deviation - 0.01) * 10
            else:
                peg_score = max(0.0, 0.5 - (max_deviation - 0.02) * 5)
            
            # Store peg metrics
            self.peg_metrics[symbol] = {
                'symbol': symbol,
                'current_price': recent_prices[-1]['price'],
                'current_deviation': current_deviation,
                'max_deviation_30min': max_deviation,
                'avg_deviation_30min': avg_deviation,
                'peg_stability_score': peg_score,
                'data_points': len(recent_prices),
                'calculation_timestamp': datetime.utcnow().isoformat(),
                'assessment': 'Excellent' if peg_score > 0.95 else
                           'Good' if peg_score > 0.85 else
                           'Fair' if peg_score > 0.70 else 'Poor'
            }
            
            self.last_peg_calculation[symbol] = datetime.utcnow()
            
            logger.debug(f"🎯 Peg stability: {symbol} Score={peg_score:.3f} Dev={current_deviation:.4f}")
            
        except Exception as e:
            logger.error(f"❌ Error calculating peg stability for {symbol}: {e}")
    
    async def _calculate_liquidity_metrics(self, symbol: str):
        """Calculate real-time liquidity metrics"""
        try:
            orderbooks = list(self.orderbook_cache[symbol])
            if len(orderbooks) < 5:  # Need at least 5 data points
                return
            
            # Get recent orderbooks (last 10 minutes)
            cutoff_time = datetime.utcnow() - timedelta(minutes=10)
            recent_books = [ob for ob in orderbooks if ob['timestamp'] >= cutoff_time]
            
            if not recent_books:
                return
            
            # Calculate liquidity metrics
            spreads = []
            bid_depths = []
            ask_depths = []
            
            for book in recent_books:
                spread = book['ask_price'] - book['bid_price']
                spread_pct = (spread / book['bid_price']) * 100 if book['bid_price'] > 0 else 0
                spreads.append(spread_pct)
                
                bid_depths.append(book['bid_quantity'])
                ask_depths.append(book['ask_quantity'])
            
            # Calculate metrics
            avg_spread = sum(spreads) / len(spreads)
            avg_bid_depth = sum(bid_depths) / len(bid_depths)
            avg_ask_depth = sum(ask_depths) / len(ask_depths)
            avg_total_depth = avg_bid_depth + avg_ask_depth
            
            # Calculate liquidity score (0-1, where 1 is perfect liquidity)
            # Lower spreads and higher depth = better liquidity
            spread_score = max(0.0, 1.0 - (avg_spread / 0.50))  # 0.5% spread gets 0 score
            depth_score = min(1.0, avg_total_depth / 1_000_000)  # $1M depth gets perfect score
            
            liquidity_score = (spread_score * 0.6) + (depth_score * 0.4)
            
            # Store liquidity metrics
            self.liquidity_metrics[symbol] = {
                'symbol': symbol,
                'avg_spread_bps': avg_spread * 100,  # Convert to basis points
                'avg_bid_depth_usd': avg_bid_depth,
                'avg_ask_depth_usd': avg_ask_depth,
                'total_depth_usd': avg_total_depth,
                'liquidity_score': liquidity_score,
                'data_points': len(recent_books),
                'calculation_timestamp': datetime.utcnow().isoformat(),
                'assessment': 'Excellent' if liquidity_score > 0.90 else
                             'Good' if liquidity_score > 0.75 else
                             'Fair' if liquidity_score > 0.60 else 'Poor'
            }
            
            self.last_liquidity_calculation[symbol] = datetime.utcnow()
            
            logger.debug(f"💧 Liquidity: {symbol} Score={liquidity_score:.3f} Spread={avg_spread:.2f}bp")
            
        except Exception as e:
            logger.error(f"❌ Error calculating liquidity metrics for {symbol}: {e}")
    
    async def _peg_stability_calculator(self):
        """Background task for peg stability calculations"""
        while self.is_running:
            try:
                await asyncio.sleep(self.peg_calculation_interval)
                
                # Calculate peg stability for all symbols with data
                for symbol in self.price_cache.keys():
                    await self._calculate_peg_stability(symbol)
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Error in peg stability calculator: {e}")
    
    async def _liquidity_metrics_calculator(self):
        """Background task for liquidity metrics calculations"""
        while self.is_running:
            try:
                await asyncio.sleep(self.liquidity_calculation_interval)
                
                # Calculate liquidity metrics for all symbols with data
                for symbol in self.orderbook_cache.keys():
                    await self._calculate_liquidity_metrics(symbol)
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Error in liquidity calculator: {e}")
    
    async def _syi_realtime_calculator(self):
        """Background task for real-time SYI calculations"""
        while self.is_running:
            try:
                await asyncio.sleep(self.syi_calculation_interval)
                
                # Skip calculation if no real-time data available
                if not self.peg_metrics and not self.liquidity_metrics:
                    continue
                
                # Get current yield data
                current_yields = await self.yield_aggregator.get_all_yields()
                
                # Enhance yield data with real-time metrics
                enhanced_yields = []
                for yield_data in current_yields:
                    symbol = yield_data.get('stablecoin', yield_data.get('canonical_stablecoin_id', 'Unknown'))
                    
                    # Add real-time peg metrics
                    if symbol in self.peg_metrics:
                        if 'metadata' not in yield_data:
                            yield_data['metadata'] = {}
                        yield_data['metadata']['realtime_peg_metrics'] = self.peg_metrics[symbol]
                    
                    # Add real-time liquidity metrics
                    if symbol in self.liquidity_metrics:
                        if 'metadata' not in yield_data:
                            yield_data['metadata'] = {}
                        yield_data['metadata']['realtime_liquidity_metrics'] = self.liquidity_metrics[symbol]
                    
                    enhanced_yields.append(yield_data)
                
                # Calculate real-time SYI if we have enhanced data
                if enhanced_yields:
                    syi_composition = self.syi_compositor.compose_syi(enhanced_yields)
                    
                    # Store SYI data for broadcasting
                    self.last_syi_data = {
                        'index_value': syi_composition.index_value,
                        'constituent_count': syi_composition.constituent_count,
                        'calculation_timestamp': syi_composition.calculation_timestamp,
                        'quality_metrics': syi_composition.quality_metrics,
                        'enhanced_with_realtime': True,
                        'realtime_symbols': list(set(self.peg_metrics.keys()) | set(self.liquidity_metrics.keys()))
                    }
                    
                    self.last_syi_calculation = datetime.utcnow()
                    
                    logger.info(f"📊 Real-time SYI: {syi_composition.index_value:.4f} ({syi_composition.constituent_count} constituents)")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Error in SYI real-time calculator: {e}")
    
    async def _websocket_broadcaster(self):
        """Background task for broadcasting real-time data via WebSocket"""
        while self.is_running:
            try:
                await asyncio.sleep(5)  # Broadcast every 5 seconds
                
                # Broadcast peg metrics
                if self.peg_metrics:
                    await self.websocket_manager.broadcast('peg_metrics', {
                        'type': 'peg_metrics_update',
                        'data': self.peg_metrics,
                        'timestamp': datetime.utcnow().isoformat()
                    })
                
                # Broadcast liquidity metrics  
                if self.liquidity_metrics:
                    await self.websocket_manager.broadcast('liquidity_metrics', {
                        'type': 'liquidity_metrics_update',
                        'data': self.liquidity_metrics,
                        'timestamp': datetime.utcnow().isoformat()
                    })
                
                # Broadcast SYI updates
                if hasattr(self, 'last_syi_data'):
                    await self.websocket_manager.broadcast('syi_live', {
                        'type': 'syi_live_update',
                        'data': self.last_syi_data,
                        'timestamp': datetime.utcnow().isoformat()
                    })
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Error in WebSocket broadcaster: {e}")
    
    def get_realtime_status(self) -> Dict[str, Any]:
        """Get current real-time integration status"""
        return {
            'is_running': self.is_running,
            'price_cache_symbols': list(self.price_cache.keys()),
            'orderbook_cache_symbols': list(self.orderbook_cache.keys()),
            'peg_metrics_available': list(self.peg_metrics.keys()),
            'liquidity_metrics_available': list(self.liquidity_metrics.keys()),
            'last_syi_calculation': self.last_syi_calculation.isoformat() if self.last_syi_calculation else None,
            'calculation_intervals': {
                'peg_stability': f"{self.peg_calculation_interval}s",
                'liquidity_metrics': f"{self.liquidity_calculation_interval}s", 
                'syi_calculation': f"{self.syi_calculation_interval}s"
            },
            'active_tasks': len([t for t in self.tasks if not t.done()]),
            'websocket_connections': self.websocket_manager.connection_count
        }
    
    def get_peg_metrics(self) -> Dict[str, Any]:
        """Get current peg stability metrics"""
        return self.peg_metrics.copy()
    
    def get_liquidity_metrics(self) -> Dict[str, Any]:
        """Get current liquidity metrics"""
        return self.liquidity_metrics.copy()

# Global real-time integrator instance
realtime_integrator = None

async def start_realtime_integration():
    """Start the global real-time data integrator"""
    global realtime_integrator
    
    if realtime_integrator is None:
        realtime_integrator = RealTimeDataIntegrator()
        await realtime_integrator.start()
        logger.info("🚀 Real-time data integrator started")
    else:
        logger.info("⚠️ Real-time data integrator already running")

async def stop_realtime_integration():
    """Stop the global real-time data integrator"""
    global realtime_integrator
    
    if realtime_integrator:
        await realtime_integrator.stop()
        realtime_integrator = None
        logger.info("🛑 Real-time data integrator stopped")

def get_realtime_integrator() -> Optional[RealTimeDataIntegrator]:
    """Get the global real-time data integrator"""
    return realtime_integrator