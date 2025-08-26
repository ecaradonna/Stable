"""
Advanced Trading & Execution Engine Service (STEP 11)
Institutional trading engine with order management, portfolio execution, and automated rebalancing
"""

import asyncio
import logging
import uuid
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import json
from pathlib import Path
import aiohttp
from decimal import Decimal, ROUND_HALF_UP

from .yield_aggregator import YieldAggregator
from .ray_calculator import RAYCalculator
from .syi_compositor import SYICompositor
from .ml_insights_service import get_ml_insights_service

logger = logging.getLogger(__name__)

class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"
    OCO = "oco"  # One-Cancels-Other

class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"

class OrderStatus(Enum):
    PENDING = "pending"
    OPEN = "open"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"

class TradeStatus(Enum):
    PENDING = "pending"
    EXECUTED = "executed"
    FAILED = "failed"
    SETTLED = "settled"

@dataclass
class TradingPair:
    base_asset: str  # e.g., "USDT"
    quote_asset: str  # e.g., "USD"
    symbol: str  # e.g., "USDT/USD"
    min_order_size: Decimal
    max_order_size: Decimal
    price_precision: int
    quantity_precision: int
    trading_fee: Decimal
    maker_fee: Decimal
    taker_fee: Decimal

@dataclass
class Order:
    order_id: str
    client_id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: Decimal
    price: Optional[Decimal]
    stop_price: Optional[Decimal]
    status: OrderStatus
    created_at: datetime
    updated_at: datetime
    filled_quantity: Decimal = Decimal('0')
    remaining_quantity: Optional[Decimal] = None
    average_price: Optional[Decimal] = None
    exchange: str = "synthetic"
    time_in_force: str = "GTC"  # Good Till Cancelled
    execution_strategy: str = "optimal"

@dataclass
class Trade:
    trade_id: str
    order_id: str
    client_id: str
    symbol: str
    side: OrderSide
    quantity: Decimal
    price: Decimal
    commission: Decimal
    commission_asset: str
    executed_at: datetime
    status: TradeStatus
    exchange: str
    settlement_date: Optional[datetime] = None

@dataclass
class Position:
    position_id: str
    client_id: str
    symbol: str
    quantity: Decimal
    average_price: Decimal
    current_price: Decimal
    unrealized_pnl: Decimal
    realized_pnl: Decimal
    created_at: datetime
    updated_at: datetime
    margin_used: Decimal = Decimal('0')
    leverage: Decimal = Decimal('1')

@dataclass
class Portfolio:
    portfolio_id: str
    client_id: str
    name: str
    total_value: Decimal
    cash_balance: Decimal
    positions: List[Position]
    target_allocation: Dict[str, Decimal]
    created_at: datetime
    updated_at: datetime
    risk_limit: Decimal = Decimal('100000')  # $100k default
    max_position_size: Decimal = Decimal('0.20')  # 20% max per position

@dataclass
class RebalanceStrategy:
    strategy_id: str
    portfolio_id: str
    name: str
    frequency: str  # "daily", "weekly", "monthly", "on_signal"
    threshold: Decimal  # Rebalance when deviation > threshold
    use_ray_signals: bool
    use_ml_predictions: bool
    risk_budget: Decimal
    max_trades_per_day: int
    is_active: bool
    created_at: datetime

class TradingEngineService:
    """Advanced trading and execution engine for institutional clients"""
    
    def __init__(self):
        # Core services
        self.yield_aggregator = YieldAggregator()
        self.ray_calculator = RAYCalculator()
        self.syi_compositor = SYICompositor()
        
        # Trading data
        self.trading_pairs: Dict[str, TradingPair] = {}
        self.orders: Dict[str, Order] = {}
        self.trades: Dict[str, Trade] = {}
        self.positions: Dict[str, Position] = {}
        self.portfolios: Dict[str, Portfolio] = {}
        self.rebalance_strategies: Dict[str, RebalanceStrategy] = {}
        
        # Exchange connections (simulated)
        self.exchange_connections = {
            "binance": {"connected": True, "latency": 0.05},
            "coinbase": {"connected": True, "latency": 0.08},
            "kraken": {"connected": True, "latency": 0.12},
            "uniswap_v3": {"connected": True, "latency": 0.3},
            "curve": {"connected": True, "latency": 0.4}
        }
        
        # Market data cache
        self.market_prices: Dict[str, Decimal] = {}
        self.order_books: Dict[str, Dict[str, Any]] = {}
        
        # Risk management
        self.risk_limits = {
            "max_order_size": Decimal('1000000'),  # $1M
            "max_position_size": Decimal('5000000'),  # $5M
            "daily_loss_limit": Decimal('100000'),  # $100k
            "max_leverage": Decimal('3'),
            "concentration_limit": Decimal('0.25')  # 25% max per asset
        }
        
        # Configuration
        self.config = {
            "execution": {
                "smart_routing": True,
                "best_execution": True,
                "price_improvement_threshold": 0.0001,  # 1 basis point
                "execution_timeout": 30,  # seconds
                "max_slippage": 0.005  # 50 basis points
            },
            "risk": {
                "pre_trade_checks": True,
                "position_limits": True,
                "correlation_checks": True,
                "stress_testing": True
            },
            "rebalancing": {
                "min_rebalance_amount": Decimal('1000'),
                "max_rebalance_frequency": "daily",
                "transaction_cost_threshold": 0.002,  # 20 basis points
                "drift_tolerance": 0.05  # 5%
            }
        }
        
        # Data storage
        self.trading_dir = Path("/app/data/trading")
        self.trading_dir.mkdir(parents=True, exist_ok=True)
        
        # Background tasks
        self.is_running = False
        self.background_tasks = []
    
    async def start(self):
        """Start the trading engine service"""
        if self.is_running:
            return
        
        self.is_running = True
        logger.info("🚀 Starting Advanced Trading Engine Service...")
        
        # Initialize trading pairs
        await self._initialize_trading_pairs()
        
        # Load existing data
        await self._load_trading_data()
        
        # Initialize market data
        await self._initialize_market_data()
        
        # Start background tasks
        self.background_tasks = [
            asyncio.create_task(self._market_data_updater()),
            asyncio.create_task(self._order_processor()),
            asyncio.create_task(self._position_manager()),
            asyncio.create_task(self._rebalance_scheduler()),
            asyncio.create_task(self._risk_monitor()),
            asyncio.create_task(self._settlement_processor())
        ]
        
        logger.info("✅ Advanced Trading Engine Service started")
    
    async def stop(self):
        """Stop the trading engine service"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()
        
        await asyncio.gather(*self.background_tasks, return_exceptions=True)
        
        # Save data
        await self._save_trading_data()
        
        logger.info("🛑 Advanced Trading Engine Service stopped")
    
    # Trading Pair Management
    async def _initialize_trading_pairs(self):
        """Initialize supported trading pairs"""
        # Major stablecoin pairs
        stablecoin_pairs = [
            ("USDT", "USD", "0.9995", "1.0005", 8, 6, "0.001"),
            ("USDC", "USD", "0.9995", "1.0005", 8, 6, "0.001"),
            ("DAI", "USD", "0.9990", "1.0010", 8, 6, "0.0015"),
            ("TUSD", "USD", "0.9990", "1.0010", 8, 6, "0.0015"),
            ("FRAX", "USD", "0.9985", "1.0015", 8, 6, "0.002"),
            ("USDP", "USD", "0.9990", "1.0010", 8, 6, "0.0015"),
            ("PYUSD", "USD", "0.9985", "1.0015", 8, 6, "0.002")
        ]
        
        for base, quote, min_price, max_price, pprecision, qprecision, fee in stablecoin_pairs:
            symbol = f"{base}/{quote}"
            
            trading_pair = TradingPair(
                base_asset=base,
                quote_asset=quote,
                symbol=symbol,
                min_order_size=Decimal('100'),  # $100 minimum
                max_order_size=Decimal('10000000'),  # $10M maximum
                price_precision=pprecision,
                quantity_precision=qprecision,
                trading_fee=Decimal(fee),
                maker_fee=Decimal(fee) * Decimal('0.8'),  # 20% discount for makers
                taker_fee=Decimal(fee)
            )
            
            self.trading_pairs[symbol] = trading_pair
        
        logger.info(f"📈 Initialized {len(self.trading_pairs)} trading pairs")
    
    async def _initialize_market_data(self):
        """Initialize market data with synthetic prices"""
        for symbol, pair in self.trading_pairs.items():
            # Simulate realistic stablecoin prices with small variations
            base_price = Decimal('1.0000')
            variation = Decimal(str(0.0001 + (hash(symbol) % 20) * 0.0001))  # 0.01% to 0.2% variation
            
            if "USDT" in symbol:
                price = base_price + variation
            elif "USDC" in symbol:
                price = base_price - variation * Decimal('0.5')
            elif "DAI" in symbol:
                price = base_price + variation * Decimal('1.5')
            else:
                price = base_price + variation * Decimal('0.7')
            
            self.market_prices[symbol] = price
            
            # Initialize order book
            self.order_books[symbol] = {
                "bid": price - Decimal('0.0001'),
                "ask": price + Decimal('0.0001'),
                "bid_size": Decimal('50000'),
                "ask_size": Decimal('50000'),
                "spread": Decimal('0.0002'),
                "timestamp": datetime.utcnow()
            }
        
        logger.info(f"💹 Initialized market data for {len(self.market_prices)} symbols")
    
    # Order Management
    async def create_order(self, client_id: str, symbol: str, side: str, order_type: str, 
                          quantity: Decimal, price: Optional[Decimal] = None, 
                          stop_price: Optional[Decimal] = None) -> Order:
        """Create a new trading order"""
        
        # Validate trading pair
        if symbol not in self.trading_pairs:
            raise ValueError(f"Unsupported trading pair: {symbol}")
        
        trading_pair = self.trading_pairs[symbol]
        
        # Validate order parameters
        if quantity < trading_pair.min_order_size:
            raise ValueError(f"Order size {quantity} below minimum {trading_pair.min_order_size}")
        
        if quantity > trading_pair.max_order_size:
            raise ValueError(f"Order size {quantity} exceeds maximum {trading_pair.max_order_size}")
        
        # Pre-trade risk checks
        if self.config["risk"]["pre_trade_checks"]:
            await self._validate_pre_trade_risk(client_id, symbol, side, quantity, price)
        
        # Create order
        order_id = f"order_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        
        order = Order(
            order_id=order_id,
            client_id=client_id,
            symbol=symbol,
            side=OrderSide(side.lower()),
            order_type=OrderType(order_type.lower()),
            quantity=quantity,
            price=price,
            stop_price=stop_price,
            status=OrderStatus.PENDING,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            remaining_quantity=quantity
        )
        
        self.orders[order_id] = order
        
        logger.info(f"📋 Created order {order_id}: {side} {quantity} {symbol} @ {price or 'market'}")
        
        # Queue for execution
        await self._queue_order_for_execution(order)
        
        return order
    
    async def _validate_pre_trade_risk(self, client_id: str, symbol: str, side: str, 
                                     quantity: Decimal, price: Optional[Decimal]):
        """Validate pre-trade risk limits"""
        
        # Check position limits
        current_positions = [p for p in self.positions.values() if p.client_id == client_id]
        
        if side == "buy":
            # Check if buy would exceed concentration limit
            total_portfolio_value = sum(p.quantity * p.current_price for p in current_positions)
            if total_portfolio_value > 0:
                order_value = quantity * (price or self.market_prices[symbol])
                concentration = order_value / (total_portfolio_value + order_value)
                
                if concentration > self.risk_limits["concentration_limit"]:
                    raise ValueError(f"Order would exceed concentration limit of {self.risk_limits['concentration_limit']:.1%}")
        
        # Check order size limits
        order_value = quantity * (price or self.market_prices[symbol])
        if order_value > self.risk_limits["max_order_size"]:
            raise ValueError(f"Order value {order_value} exceeds maximum {self.risk_limits['max_order_size']}")
        
        logger.debug(f"✅ Pre-trade risk checks passed for {client_id}")
    
    async def _queue_order_for_execution(self, order: Order):
        """Queue order for execution processing"""
        # In a real system, this would send to execution queue
        # For simulation, we'll process immediately in background
        asyncio.create_task(self._execute_order(order))
    
    async def _execute_order(self, order: Order):
        """Execute a trading order"""
        try:
            order.status = OrderStatus.OPEN
            order.updated_at = datetime.utcnow()
            
            # Get current market price
            current_price = self.market_prices[order.symbol]
            
            # Determine execution price
            if order.order_type == OrderType.MARKET:
                execution_price = current_price
            elif order.order_type == OrderType.LIMIT:
                if order.side == OrderSide.BUY and order.price >= current_price:
                    execution_price = min(order.price, current_price)
                elif order.side == OrderSide.SELL and order.price <= current_price:
                    execution_price = max(order.price, current_price)
                else:
                    # Limit not reached, keep order open
                    return
            else:
                execution_price = current_price
            
            # Simulate execution delay
            await asyncio.sleep(0.1)
            
            # Calculate trading fees
            trading_pair = self.trading_pairs[order.symbol]
            commission = order.quantity * execution_price * trading_pair.taker_fee
            
            # Create trade record
            trade_id = f"trade_{int(time.time())}_{uuid.uuid4().hex[:8]}"
            
            trade = Trade(
                trade_id=trade_id,
                order_id=order.order_id,
                client_id=order.client_id,
                symbol=order.symbol,
                side=order.side,
                quantity=order.quantity,
                price=execution_price,
                commission=commission,
                commission_asset="USD",
                executed_at=datetime.utcnow(),
                status=TradeStatus.EXECUTED,
                exchange="synthetic"
            )
            
            self.trades[trade_id] = trade
            
            # Update order status
            order.status = OrderStatus.FILLED
            order.filled_quantity = order.quantity
            order.remaining_quantity = Decimal('0')
            order.average_price = execution_price
            order.updated_at = datetime.utcnow()
            
            # Update or create position
            await self._update_position(trade)
            
            logger.info(f"✅ Executed trade {trade_id}: {order.side.value} {order.quantity} {order.symbol} @ {execution_price}")
            
        except Exception as e:
            logger.error(f"❌ Order execution failed {order.order_id}: {e}")
            order.status = OrderStatus.REJECTED
            order.updated_at = datetime.utcnow()
    
    async def _update_position(self, trade: Trade):
        """Update client position after trade execution"""
        position_key = f"{trade.client_id}_{trade.symbol}"
        
        if position_key in self.positions:
            position = self.positions[position_key]
            
            if trade.side == OrderSide.BUY:
                # Increase position
                total_value = (position.quantity * position.average_price) + (trade.quantity * trade.price)
                total_quantity = position.quantity + trade.quantity
                position.average_price = total_value / total_quantity
                position.quantity = total_quantity
            else:
                # Decrease position
                position.quantity -= trade.quantity
                
                # Calculate realized PnL
                realized_pnl = (trade.price - position.average_price) * trade.quantity
                position.realized_pnl += realized_pnl
            
            position.updated_at = datetime.utcnow()
        else:
            # Create new position
            position_id = f"pos_{int(time.time())}_{uuid.uuid4().hex[:8]}"
            
            position = Position(
                position_id=position_id,
                client_id=trade.client_id,
                symbol=trade.symbol,
                quantity=trade.quantity if trade.side == OrderSide.BUY else -trade.quantity,
                average_price=trade.price,
                current_price=trade.price,
                unrealized_pnl=Decimal('0'),
                realized_pnl=Decimal('0'),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            self.positions[position_key] = position
        
        logger.debug(f"📊 Updated position {position_key}: {position.quantity} @ {position.average_price}")
    
    # Portfolio Management
    async def create_portfolio(self, client_id: str, name: str, 
                             target_allocation: Dict[str, Decimal], 
                             initial_cash: Decimal = Decimal('100000')) -> Portfolio:
        """Create a new portfolio for a client"""
        
        portfolio_id = f"portfolio_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        
        portfolio = Portfolio(
            portfolio_id=portfolio_id,
            client_id=client_id,
            name=name,
            total_value=initial_cash,
            cash_balance=initial_cash,
            positions=[],
            target_allocation=target_allocation,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        self.portfolios[portfolio_id] = portfolio
        
        logger.info(f"📁 Created portfolio {portfolio_id} for {client_id}: {name}")
        
        return portfolio
    
    async def get_portfolio_performance(self, portfolio_id: str) -> Dict[str, Any]:
        """Calculate portfolio performance metrics"""
        if portfolio_id not in self.portfolios:
            raise ValueError(f"Portfolio {portfolio_id} not found")
        
        portfolio = self.portfolios[portfolio_id]
        
        # Get current positions
        client_positions = [p for p in self.positions.values() if p.client_id == portfolio.client_id]
        
        # Update current prices and calculate unrealized PnL
        total_value = portfolio.cash_balance
        total_unrealized_pnl = Decimal('0')
        total_realized_pnl = Decimal('0')
        
        for position in client_positions:
            current_price = self.market_prices.get(position.symbol, position.current_price)
            position.current_price = current_price
            
            position_value = position.quantity * current_price
            total_value += position_value
            
            unrealized_pnl = (current_price - position.average_price) * position.quantity
            position.unrealized_pnl = unrealized_pnl
            total_unrealized_pnl += unrealized_pnl
            total_realized_pnl += position.realized_pnl
        
        portfolio.total_value = total_value
        portfolio.updated_at = datetime.utcnow()
        
        # Calculate performance metrics
        total_pnl = total_realized_pnl + total_unrealized_pnl
        total_return = (total_pnl / (total_value - total_pnl)) * 100 if (total_value - total_pnl) != 0 else 0
        
        # Calculate current allocation vs target
        current_allocation = {}
        allocation_drift = {}
        
        for position in client_positions:
            symbol = position.symbol.split('/')[0]  # Get base asset
            position_value = position.quantity * position.current_price
            current_allocation[symbol] = (position_value / total_value) * 100
        
        for asset, target_pct in portfolio.target_allocation.items():
            current_pct = current_allocation.get(asset, Decimal('0'))
            allocation_drift[asset] = current_pct - target_pct
        
        return {
            "portfolio_id": portfolio_id,
            "name": portfolio.name,
            "total_value": float(total_value),
            "cash_balance": float(portfolio.cash_balance),
            "total_pnl": float(total_pnl),
            "realized_pnl": float(total_realized_pnl),
            "unrealized_pnl": float(total_unrealized_pnl),
            "total_return_percent": float(total_return),
            "position_count": len(client_positions),
            "current_allocation": {k: float(v) for k, v in current_allocation.items()},
            "target_allocation": {k: float(v) for k, v in portfolio.target_allocation.items()},
            "allocation_drift": {k: float(v) for k, v in allocation_drift.items()},
            "last_updated": portfolio.updated_at.isoformat()
        }
    
    # Rebalancing System
    async def create_rebalance_strategy(self, portfolio_id: str, name: str, 
                                      frequency: str = "weekly", 
                                      threshold: Decimal = Decimal('0.05'),
                                      use_ray_signals: bool = True,
                                      use_ml_predictions: bool = True) -> RebalanceStrategy:
        """Create an automated rebalancing strategy"""
        
        if portfolio_id not in self.portfolios:
            raise ValueError(f"Portfolio {portfolio_id} not found")
        
        strategy_id = f"strategy_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        
        strategy = RebalanceStrategy(
            strategy_id=strategy_id,
            portfolio_id=portfolio_id,
            name=name,
            frequency=frequency,
            threshold=threshold,
            use_ray_signals=use_ray_signals,
            use_ml_predictions=use_ml_predictions,
            risk_budget=Decimal('0.02'),  # 2% risk budget
            max_trades_per_day=10,
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        self.rebalance_strategies[strategy_id] = strategy
        
        logger.info(f"🔄 Created rebalance strategy {strategy_id}: {name}")
        
        return strategy
    
    async def execute_rebalance(self, strategy_id: str) -> Dict[str, Any]:
        """Execute portfolio rebalancing based on strategy"""
        if strategy_id not in self.rebalance_strategies:
            raise ValueError(f"Rebalance strategy {strategy_id} not found")
        
        strategy = self.rebalance_strategies[strategy_id]
        portfolio = self.portfolios[strategy.portfolio_id]
        
        logger.info(f"🔄 Executing rebalance for strategy {strategy_id}")
        
        # Get current portfolio performance
        performance = await self.get_portfolio_performance(strategy.portfolio_id)
        
        # Check if rebalancing is needed
        max_drift = max(abs(drift) for drift in performance["allocation_drift"].values())
        
        if max_drift < strategy.threshold:
            return {
                "strategy_id": strategy_id,
                "rebalance_needed": False,
                "max_drift": float(max_drift),
                "threshold": float(strategy.threshold),
                "message": "Portfolio within threshold, no rebalancing needed"
            }
        
        # Get RAY signals if enabled
        ray_signals = {}
        if strategy.use_ray_signals:
            ray_signals = await self._get_ray_rebalance_signals(portfolio.client_id)
        
        # Get ML predictions if enabled
        ml_signals = {}
        if strategy.use_ml_predictions:
            ml_signals = await self._get_ml_rebalance_signals(portfolio.client_id)
        
        # Calculate optimal allocation
        optimal_allocation = await self._calculate_optimal_allocation(
            portfolio, performance, ray_signals, ml_signals
        )
        
        # Generate rebalancing trades
        rebalance_trades = await self._generate_rebalance_trades(
            portfolio, performance, optimal_allocation
        )
        
        # Execute rebalancing trades
        executed_trades = []
        for trade_spec in rebalance_trades:
            try:
                order = await self.create_order(
                    client_id=portfolio.client_id,
                    symbol=trade_spec["symbol"],
                    side=trade_spec["side"],
                    order_type="market",
                    quantity=trade_spec["quantity"]
                )
                executed_trades.append({
                    "order_id": order.order_id,
                    "symbol": trade_spec["symbol"],
                    "side": trade_spec["side"],
                    "quantity": float(trade_spec["quantity"]),
                    "reason": trade_spec["reason"]
                })
            except Exception as e:
                logger.error(f"❌ Rebalance trade failed: {e}")
        
        return {
            "strategy_id": strategy_id,
            "rebalance_needed": True,
            "max_drift": float(max_drift),
            "threshold": float(strategy.threshold),
            "optimal_allocation": optimal_allocation,
            "trades_executed": len(executed_trades),
            "executed_trades": executed_trades,
            "ray_signals_used": len(ray_signals),
            "ml_signals_used": len(ml_signals),
            "execution_timestamp": datetime.utcnow().isoformat()
        }
    
    async def _get_ray_rebalance_signals(self, client_id: str) -> Dict[str, Any]:
        """Get RAY-based rebalancing signals"""
        try:
            # Get current yield data
            current_yields = await self.yield_aggregator.get_all_yields()
            
            if not current_yields:
                return {}
            
            # Calculate RAY for all yields
            ray_results = self.ray_calculator.calculate_ray_batch(current_yields)
            
            # Create signals based on RAY ranking
            signals = {}
            for yield_data, ray_result in zip(current_yields, ray_results):
                symbol = yield_data.get('stablecoin', 'Unknown')
                signals[symbol] = {
                    "ray": float(ray_result.risk_adjusted_yield),
                    "risk_penalty": float(ray_result.risk_penalty),
                    "confidence": float(ray_result.confidence_score),
                    "recommendation": "overweight" if ray_result.risk_adjusted_yield > 4.0 else
                                   "underweight" if ray_result.risk_adjusted_yield < 2.0 else "neutral"
                }
            
            return signals
            
        except Exception as e:
            logger.error(f"❌ Error getting RAY signals: {e}")
            return {}
    
    async def _get_ml_rebalance_signals(self, client_id: str) -> Dict[str, Any]:
        """Get ML-based rebalancing signals"""
        try:
            ml_service = get_ml_insights_service()
            if not ml_service:
                return {}
            
            # Get current yield data
            current_yields = await self.yield_aggregator.get_all_yields()
            
            if not current_yields:
                return {}
            
            # Generate ML predictions
            predictions = await ml_service.predict_yields(current_yields)
            insights = await ml_service.generate_market_insights(current_yields)
            
            signals = {}
            
            # Convert predictions to signals
            for pred in predictions:
                signals[pred.symbol] = {
                    "predicted_yield_7d": pred.predicted_yield_7d,
                    "confidence_7d": pred.confidence_7d,
                    "trend_direction": pred.trend_direction,
                    "recommendation": "overweight" if pred.trend_direction == "up" and pred.confidence_7d > 0.7 else
                                   "underweight" if pred.trend_direction == "down" and pred.confidence_7d > 0.7 else "neutral"
                }
            
            # Add insights
            high_impact_opportunities = [
                insight for insight in insights 
                if insight.insight_type == "opportunity" and insight.impact_level == "high"
            ]
            
            if high_impact_opportunities:
                signals["market_insights"] = [
                    {
                        "title": insight.title,
                        "description": insight.description,
                        "confidence": insight.confidence,
                        "supporting_data": insight.supporting_data
                    }
                    for insight in high_impact_opportunities[:3]  # Top 3 insights
                ]
            
            return signals
            
        except Exception as e:
            logger.error(f"❌ Error getting ML signals: {e}")
            return {}
    
    async def _calculate_optimal_allocation(self, portfolio: Portfolio, 
                                          performance: Dict[str, Any],
                                          ray_signals: Dict[str, Any],
                                          ml_signals: Dict[str, Any]) -> Dict[str, float]:
        """Calculate optimal portfolio allocation using RAY and ML signals"""
        
        # Start with target allocation
        optimal_allocation = dict(portfolio.target_allocation)
        
        # Adjust based on RAY signals
        if ray_signals:
            for asset, signal in ray_signals.items():
                if asset in optimal_allocation:
                    ray_adjustment = 0.0
                    
                    if signal["recommendation"] == "overweight" and signal["confidence"] > 0.8:
                        ray_adjustment = 0.02  # +2%
                    elif signal["recommendation"] == "underweight" and signal["confidence"] > 0.8:
                        ray_adjustment = -0.02  # -2%
                    
                    optimal_allocation[asset] = max(0.0, float(optimal_allocation[asset]) + ray_adjustment)
        
        # Adjust based on ML signals
        if ml_signals:
            for asset, signal in ml_signals.items():
                if asset in optimal_allocation and isinstance(signal, dict):
                    ml_adjustment = 0.0
                    
                    if (signal["recommendation"] == "overweight" and 
                        signal["confidence_7d"] > 0.75 and 
                        signal["trend_direction"] == "up"):
                        ml_adjustment = 0.015  # +1.5%
                    elif (signal["recommendation"] == "underweight" and 
                          signal["confidence_7d"] > 0.75 and 
                          signal["trend_direction"] == "down"):
                        ml_adjustment = -0.015  # -1.5%
                    
                    optimal_allocation[asset] = max(0.0, float(optimal_allocation[asset]) + ml_adjustment)
        
        # Normalize to 100%
        total_allocation = sum(optimal_allocation.values())
        if total_allocation > 0:
            optimal_allocation = {k: (v / total_allocation) for k, v in optimal_allocation.items()}
        
        return {k: float(v) for k, v in optimal_allocation.items()}
    
    async def _generate_rebalance_trades(self, portfolio: Portfolio, 
                                       performance: Dict[str, Any],
                                       optimal_allocation: Dict[str, float]) -> List[Dict[str, Any]]:
        """Generate specific trades needed for rebalancing"""
        
        trades = []
        total_value = Decimal(str(performance["total_value"]))
        
        for asset, target_pct in optimal_allocation.items():
            current_pct = performance["current_allocation"].get(asset, 0.0)
            drift = target_pct - current_pct
            
            if abs(drift) > 0.01:  # 1% minimum trade size
                trade_value = total_value * Decimal(str(abs(drift)))
                
                # Find appropriate trading pair
                symbol = f"{asset}/USD"
                if symbol not in self.trading_pairs:
                    continue
                
                current_price = self.market_prices.get(symbol, Decimal('1.0'))
                quantity = trade_value / current_price
                
                # Round to appropriate precision
                trading_pair = self.trading_pairs[symbol]
                quantity = quantity.quantize(
                    Decimal('0.1') ** trading_pair.quantity_precision,
                    rounding=ROUND_HALF_UP
                )
                
                if quantity >= trading_pair.min_order_size:
                    trades.append({
                        "symbol": symbol,
                        "side": "buy" if drift > 0 else "sell",
                        "quantity": quantity,
                        "reason": f"Rebalance {asset}: {current_pct:.1%} -> {target_pct:.1%}"
                    })
        
        return trades
    
    # Background Tasks
    async def _market_data_updater(self):
        """Update market prices and order books"""
        while self.is_running:
            try:
                for symbol in self.trading_pairs.keys():
                    # Simulate price movements (small random walk)
                    current_price = self.market_prices[symbol]
                    change = Decimal(str((hash(f"{symbol}_{time.time()}") % 21 - 10) / 100000))  # ±0.01%
                    new_price = current_price * (Decimal('1') + change)
                    
                    # Keep stablecoin prices near $1
                    new_price = max(Decimal('0.995'), min(Decimal('1.005'), new_price))
                    
                    self.market_prices[symbol] = new_price
                    
                    # Update order book
                    self.order_books[symbol]["bid"] = new_price - Decimal('0.0001')
                    self.order_books[symbol]["ask"] = new_price + Decimal('0.0001')
                    self.order_books[symbol]["timestamp"] = datetime.utcnow()
                
                await asyncio.sleep(1)  # Update every second
                
            except Exception as e:
                logger.error(f"❌ Market data updater error: {e}")
                await asyncio.sleep(5)
    
    async def _order_processor(self):
        """Process pending orders"""
        while self.is_running:
            try:
                # Find orders that need processing
                pending_orders = [
                    order for order in self.orders.values()
                    if order.status in [OrderStatus.PENDING, OrderStatus.OPEN]
                ]
                
                for order in pending_orders:
                    if order.status == OrderStatus.PENDING:
                        await self._execute_order(order)
                
                await asyncio.sleep(0.5)  # Process every 500ms
                
            except Exception as e:
                logger.error(f"❌ Order processor error: {e}")
                await asyncio.sleep(5)
    
    async def _position_manager(self):
        """Update position values and PnL"""
        while self.is_running:
            try:
                for position in self.positions.values():
                    # Update current price
                    current_price = self.market_prices.get(position.symbol, position.current_price)
                    position.current_price = current_price
                    
                    # Calculate unrealized PnL
                    position.unrealized_pnl = (current_price - position.average_price) * position.quantity
                    position.updated_at = datetime.utcnow()
                
                await asyncio.sleep(5)  # Update every 5 seconds
                
            except Exception as e:
                logger.error(f"❌ Position manager error: {e}")
                await asyncio.sleep(10)
    
    async def _rebalance_scheduler(self):
        """Schedule and execute automatic rebalancing"""
        while self.is_running:
            try:
                current_time = datetime.utcnow()
                
                for strategy in self.rebalance_strategies.values():
                    if not strategy.is_active:
                        continue
                    
                    # Check if rebalancing is due
                    should_rebalance = False
                    
                    if strategy.frequency == "daily":
                        should_rebalance = current_time.hour == 9  # 9 AM UTC
                    elif strategy.frequency == "weekly":
                        should_rebalance = current_time.weekday() == 0 and current_time.hour == 9  # Monday 9 AM
                    elif strategy.frequency == "monthly":
                        should_rebalance = current_time.day == 1 and current_time.hour == 9  # 1st of month
                    
                    if should_rebalance:
                        try:
                            await self.execute_rebalance(strategy.strategy_id)
                        except Exception as e:
                            logger.error(f"❌ Scheduled rebalance failed {strategy.strategy_id}: {e}")
                
                await asyncio.sleep(3600)  # Check hourly
                
            except Exception as e:
                logger.error(f"❌ Rebalance scheduler error: {e}")
                await asyncio.sleep(3600)
    
    async def _risk_monitor(self):
        """Monitor positions for risk limit violations"""
        while self.is_running:
            try:
                # Check position limits
                for position in self.positions.values():
                    position_value = position.quantity * position.current_price
                    
                    if position_value > self.risk_limits["max_position_size"]:
                        logger.warning(f"⚠️ Position size limit exceeded: {position.position_id}")
                        # In production, this would trigger alerts/actions
                
                # Check portfolio concentration
                client_exposures = {}
                for position in self.positions.values():
                    if position.client_id not in client_exposures:
                        client_exposures[position.client_id] = {}
                    
                    asset = position.symbol.split('/')[0]
                    position_value = position.quantity * position.current_price
                    
                    if asset not in client_exposures[position.client_id]:
                        client_exposures[position.client_id][asset] = Decimal('0')
                    
                    client_exposures[position.client_id][asset] += position_value
                
                # Check concentration limits
                for client_id, exposures in client_exposures.items():
                    total_exposure = sum(exposures.values())
                    
                    for asset, exposure in exposures.items():
                        if total_exposure > 0:
                            concentration = exposure / total_exposure
                            
                            if concentration > self.risk_limits["concentration_limit"]:
                                logger.warning(f"⚠️ Concentration limit exceeded: {client_id} in {asset}")
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"❌ Risk monitor error: {e}")
                await asyncio.sleep(60)
    
    async def _settlement_processor(self):
        """Process trade settlements"""
        while self.is_running:
            try:
                # Find trades that need settlement
                unsettled_trades = [
                    trade for trade in self.trades.values()
                    if trade.status == TradeStatus.EXECUTED
                ]
                
                for trade in unsettled_trades:
                    # Simulate settlement delay (T+1)
                    if (datetime.utcnow() - trade.executed_at).total_seconds() > 3600:  # 1 hour delay
                        trade.status = TradeStatus.SETTLED
                        trade.settlement_date = datetime.utcnow()
                        
                        logger.debug(f"💰 Trade settled: {trade.trade_id}")
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"❌ Settlement processor error: {e}")
                await asyncio.sleep(300)
    
    # Data Persistence
    async def _load_trading_data(self):
        """Load trading data from storage"""
        try:
            # Load orders
            orders_file = self.trading_dir / "orders.json"
            if orders_file.exists():
                with open(orders_file, 'r') as f:
                    orders_data = json.load(f)
                
                for order_data in orders_data:
                    order = Order(**order_data)
                    order.created_at = datetime.fromisoformat(order_data["created_at"])
                    order.updated_at = datetime.fromisoformat(order_data["updated_at"])
                    order.side = OrderSide(order_data["side"])
                    order.order_type = OrderType(order_data["order_type"])
                    order.status = OrderStatus(order_data["status"])
                    
                    self.orders[order.order_id] = order
            
            # Load other data structures similarly...
            logger.info(f"📂 Loaded {len(self.orders)} orders from storage")
            
        except Exception as e:
            logger.error(f"❌ Error loading trading data: {e}")
    
    async def _save_trading_data(self):
        """Save trading data to storage"""
        try:
            # Save orders
            orders_file = self.trading_dir / "orders.json"
            orders_data = []
            
            for order in self.orders.values():
                order_data = asdict(order)
                order_data["created_at"] = order.created_at.isoformat()
                order_data["updated_at"] = order.updated_at.isoformat()
                order_data["side"] = order.side.value
                order_data["order_type"] = order.order_type.value
                order_data["status"] = order.status.value
                orders_data.append(order_data)
            
            with open(orders_file, 'w') as f:
                json.dump(orders_data, f, indent=2, default=str)
            
            # Save other data structures similarly...
            logger.info(f"💾 Saved {len(self.orders)} orders to storage")
            
        except Exception as e:
            logger.error(f"❌ Error saving trading data: {e}")
    
    # Status and Management
    def get_trading_status(self) -> Dict[str, Any]:
        """Get trading engine status"""
        return {
            "service_running": self.is_running,
            "trading_pairs": len(self.trading_pairs),
            "market_data": {
                "symbols_tracked": len(self.market_prices),
                "last_price_update": max([book["timestamp"] for book in self.order_books.values()]).isoformat() if self.order_books else None
            },
            "orders": {
                "total_orders": len(self.orders),
                "pending_orders": len([o for o in self.orders.values() if o.status == OrderStatus.PENDING]),
                "open_orders": len([o for o in self.orders.values() if o.status == OrderStatus.OPEN]),
                "filled_orders": len([o for o in self.orders.values() if o.status == OrderStatus.FILLED])
            },
            "trades": {
                "total_trades": len(self.trades),
                "executed_trades": len([t for t in self.trades.values() if t.status == TradeStatus.EXECUTED]),
                "settled_trades": len([t for t in self.trades.values() if t.status == TradeStatus.SETTLED])
            },
            "positions": {
                "total_positions": len(self.positions),
                "active_positions": len([p for p in self.positions.values() if p.quantity != 0])
            },
            "portfolios": {
                "total_portfolios": len(self.portfolios),
                "rebalance_strategies": len(self.rebalance_strategies),
                "active_strategies": len([s for s in self.rebalance_strategies.values() if s.is_active])
            },
            "exchanges": {
                "connected_exchanges": len([e for e in self.exchange_connections.values() if e["connected"]]),
                "total_exchanges": len(self.exchange_connections)
            },
            "risk_monitoring": {
                "max_order_size": float(self.risk_limits["max_order_size"]),
                "max_position_size": float(self.risk_limits["max_position_size"]),
                "concentration_limit": float(self.risk_limits["concentration_limit"])
            },
            "last_updated": datetime.utcnow().isoformat()
        }

# Global trading engine service instance
trading_engine_service = None

async def start_trading_engine():
    """Start the global trading engine service"""
    global trading_engine_service
    
    if trading_engine_service is None:
        trading_engine_service = TradingEngineService()
        await trading_engine_service.start()
        logger.info("🚀 Advanced Trading Engine service started")
    else:
        logger.info("⚠️ Advanced Trading Engine service already running")

async def stop_trading_engine():
    """Stop the global trading engine service"""
    global trading_engine_service
    
    if trading_engine_service:
        await trading_engine_service.stop()
        trading_engine_service = None
        logger.info("🛑 Advanced Trading Engine service stopped")

def get_trading_engine_service() -> Optional[TradingEngineService]:
    """Get the global trading engine service"""
    return trading_engine_service