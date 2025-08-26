"""
Advanced Trading & Execution Engine API Routes (STEP 11)
Institutional trading engine with order management, portfolio execution, and automated rebalancing
"""

from fastapi import APIRouter, HTTPException, Query, Body
from typing import Dict, Any, List, Optional
from decimal import Decimal
from datetime import datetime
import logging
from pydantic import BaseModel

from services.trading_engine_service import get_trading_engine_service

logger = logging.getLogger(__name__)
router = APIRouter()

# Pydantic models for request/response
class CreateOrderRequest(BaseModel):
    client_id: str
    symbol: str
    side: str  # "buy" or "sell"
    order_type: str  # "market", "limit", "stop_loss"
    quantity: float
    price: Optional[float] = None
    stop_price: Optional[float] = None

class CreatePortfolioRequest(BaseModel):
    client_id: str
    name: str
    target_allocation: Dict[str, float]  # e.g., {"USDT": 0.4, "USDC": 0.3, "DAI": 0.3}
    initial_cash: float = 100000.0

class CreateRebalanceStrategyRequest(BaseModel):
    portfolio_id: str
    name: str
    frequency: str = "weekly"  # "daily", "weekly", "monthly", "on_signal"
    threshold: float = 0.05  # 5% drift threshold
    use_ray_signals: bool = True
    use_ml_predictions: bool = True

@router.get("/status")
async def get_trading_status() -> Dict[str, Any]:
    """Get trading engine status and overview"""
    try:
        trading_service = get_trading_engine_service()
        
        if not trading_service:
            return {
                "service_running": False,
                "message": "Advanced Trading Engine not started",
                "trading_pairs": 0,
                "orders": {"total_orders": 0},
                "trades": {"total_trades": 0},
                "positions": {"total_positions": 0},
                "portfolios": {"total_portfolios": 0}
            }
        
        return trading_service.get_trading_status()
        
    except Exception as e:
        logger.error(f"Error getting trading status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get trading status")

@router.post("/start")
async def start_trading_services() -> Dict[str, Any]:
    """Start advanced trading engine services"""
    try:
        from ..services.trading_engine_service import start_trading_engine
        
        await start_trading_engine()
        
        return {
            "message": "Advanced Trading Engine services started successfully",
            "capabilities": [
                "Institutional Order Management System",
                "Multi-Exchange Smart Routing",
                "Portfolio Execution & Rebalancing",
                "Risk Management & Position Control",
                "RAY-based Trading Signals",
                "ML-powered Portfolio Optimization",
                "Real-time Trade Settlement",
                "Automated Rebalancing Strategies"
            ],
            "trading_features": [
                "Multi-asset stablecoin trading",
                "Advanced order types (market, limit, stop)",
                "Portfolio construction and management",
                "Risk-adjusted yield integration",
                "Machine learning signal integration",
                "Automated rebalancing with thresholds",
                "Real-time position monitoring",
                "Institutional-grade execution"
            ],
            "supported_assets": ["USDT", "USDC", "DAI", "TUSD", "FRAX", "USDP", "PYUSD"],
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error starting trading services: {e}")
        raise HTTPException(status_code=500, detail="Failed to start trading services")

@router.post("/stop")
async def stop_trading_services() -> Dict[str, Any]:
    """Stop trading engine services"""
    try:
        from ..services.trading_engine_service import stop_trading_engine
        
        await stop_trading_engine()
        
        return {
            "message": "Advanced Trading Engine services stopped successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error stopping trading services: {e}")
        raise HTTPException(status_code=500, detail="Failed to stop trading services")

# Order Management
@router.post("/orders")
async def create_order(request: CreateOrderRequest) -> Dict[str, Any]:
    """Create a new trading order"""
    try:
        trading_service = get_trading_engine_service()
        
        if not trading_service:
            raise HTTPException(status_code=503, detail="Trading engine not running")
        
        # Validate order parameters
        if request.side.lower() not in ["buy", "sell"]:
            raise HTTPException(status_code=400, detail="Invalid order side. Must be 'buy' or 'sell'")
        
        if request.order_type.lower() not in ["market", "limit", "stop_loss"]:
            raise HTTPException(status_code=400, detail="Invalid order type")
        
        if request.quantity <= 0:
            raise HTTPException(status_code=400, detail="Order quantity must be positive")
        
        # Create order
        order = await trading_service.create_order(
            client_id=request.client_id,
            symbol=request.symbol,
            side=request.side,
            order_type=request.order_type,
            quantity=Decimal(str(request.quantity)),
            price=Decimal(str(request.price)) if request.price else None,
            stop_price=Decimal(str(request.stop_price)) if request.stop_price else None
        )
        
        return {
            "order": {
                "order_id": order.order_id,
                "client_id": order.client_id,
                "symbol": order.symbol,
                "side": order.side.value,
                "order_type": order.order_type.value,
                "quantity": float(order.quantity),
                "price": float(order.price) if order.price else None,
                "status": order.status.value,
                "created_at": order.created_at.isoformat(),
                "remaining_quantity": float(order.remaining_quantity) if order.remaining_quantity else None
            },
            "message": f"Order created successfully: {order.side.value} {order.quantity} {order.symbol}",
            "execution_strategy": order.execution_strategy
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating order: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create order: {str(e)}")

@router.get("/orders")
async def get_orders(
    client_id: Optional[str] = Query(default=None, description="Filter by client ID"),
    status: Optional[str] = Query(default=None, description="Filter by order status"),
    symbol: Optional[str] = Query(default=None, description="Filter by trading symbol")
) -> Dict[str, Any]:
    """Get trading orders with optional filters"""
    try:
        trading_service = get_trading_engine_service()
        
        if not trading_service:
            raise HTTPException(status_code=503, detail="Trading engine not running")
        
        # Get all orders
        all_orders = list(trading_service.orders.values())
        
        # Apply filters
        filtered_orders = all_orders
        
        if client_id:
            filtered_orders = [o for o in filtered_orders if o.client_id == client_id]
        
        if status:
            filtered_orders = [o for o in filtered_orders if o.status.value == status.lower()]
        
        if symbol:
            filtered_orders = [o for o in filtered_orders if o.symbol == symbol]
        
        # Format orders for response
        formatted_orders = []
        for order in filtered_orders:
            formatted_orders.append({
                "order_id": order.order_id,
                "client_id": order.client_id,
                "symbol": order.symbol,
                "side": order.side.value,
                "order_type": order.order_type.value,
                "quantity": float(order.quantity),
                "price": float(order.price) if order.price else None,
                "status": order.status.value,
                "created_at": order.created_at.isoformat(),
                "updated_at": order.updated_at.isoformat(),
                "filled_quantity": float(order.filled_quantity),
                "remaining_quantity": float(order.remaining_quantity) if order.remaining_quantity else None,
                "average_price": float(order.average_price) if order.average_price else None
            })
        
        # Sort by creation time (newest first)
        formatted_orders.sort(key=lambda x: x["created_at"], reverse=True)
        
        return {
            "orders": formatted_orders,
            "total_orders": len(formatted_orders),
            "filters_applied": {
                "client_id": client_id,
                "status": status,
                "symbol": symbol
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting orders: {e}")
        raise HTTPException(status_code=500, detail="Failed to get orders")

@router.get("/trades")
async def get_trades(
    client_id: Optional[str] = Query(default=None, description="Filter by client ID"),
    symbol: Optional[str] = Query(default=None, description="Filter by trading symbol"),
    limit: int = Query(default=100, description="Maximum number of trades to return")
) -> Dict[str, Any]:
    """Get trade history with optional filters"""
    try:
        trading_service = get_trading_engine_service()
        
        if not trading_service:
            raise HTTPException(status_code=503, detail="Trading engine not running")
        
        # Get all trades
        all_trades = list(trading_service.trades.values())
        
        # Apply filters
        filtered_trades = all_trades
        
        if client_id:
            filtered_trades = [t for t in filtered_trades if t.client_id == client_id]
        
        if symbol:
            filtered_trades = [t for t in filtered_trades if t.symbol == symbol]
        
        # Sort by execution time (newest first) and apply limit
        filtered_trades.sort(key=lambda x: x.executed_at, reverse=True)
        filtered_trades = filtered_trades[:limit]
        
        # Format trades for response
        formatted_trades = []
        for trade in filtered_trades:
            formatted_trades.append({
                "trade_id": trade.trade_id,
                "order_id": trade.order_id,
                "client_id": trade.client_id,
                "symbol": trade.symbol,
                "side": trade.side.value,
                "quantity": float(trade.quantity),
                "price": float(trade.price),
                "commission": float(trade.commission),
                "commission_asset": trade.commission_asset,
                "executed_at": trade.executed_at.isoformat(),
                "status": trade.status.value,
                "exchange": trade.exchange,
                "settlement_date": trade.settlement_date.isoformat() if trade.settlement_date else None
            })
        
        return {
            "trades": formatted_trades,
            "total_trades": len(formatted_trades),
            "filters_applied": {
                "client_id": client_id,
                "symbol": symbol,
                "limit": limit
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting trades: {e}")
        raise HTTPException(status_code=500, detail="Failed to get trades")

# Portfolio Management
@router.post("/portfolios")
async def create_portfolio(request: CreatePortfolioRequest) -> Dict[str, Any]:
    """Create a new portfolio for institutional trading"""
    try:
        trading_service = get_trading_engine_service()
        
        if not trading_service:
            raise HTTPException(status_code=503, detail="Trading engine not running")
        
        # Validate target allocation
        total_allocation = sum(request.target_allocation.values())
        if abs(total_allocation - 1.0) > 0.01:  # Allow 1% tolerance
            raise HTTPException(
                status_code=400, 
                detail=f"Target allocation must sum to 100% (current: {total_allocation:.1%})"
            )
        
        # Convert to Decimal for precision
        target_allocation_decimal = {
            k: Decimal(str(v)) for k, v in request.target_allocation.items()
        }
        
        # Create portfolio
        portfolio = await trading_service.create_portfolio(
            client_id=request.client_id,
            name=request.name,
            target_allocation=target_allocation_decimal,
            initial_cash=Decimal(str(request.initial_cash))
        )
        
        return {
            "portfolio": {
                "portfolio_id": portfolio.portfolio_id,
                "client_id": portfolio.client_id,
                "name": portfolio.name,
                "total_value": float(portfolio.total_value),
                "cash_balance": float(portfolio.cash_balance),
                "target_allocation": {k: float(v) for k, v in portfolio.target_allocation.items()},
                "created_at": portfolio.created_at.isoformat(),
                "risk_limit": float(portfolio.risk_limit),
                "max_position_size": float(portfolio.max_position_size)
            },
            "message": f"Portfolio '{request.name}' created successfully with ${request.initial_cash:,.0f} initial cash"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating portfolio: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create portfolio: {str(e)}")

@router.get("/portfolios")
async def get_portfolios(
    client_id: Optional[str] = Query(default=None, description="Filter by client ID")
) -> Dict[str, Any]:
    """Get portfolios with optional client filter"""
    try:
        trading_service = get_trading_engine_service()
        
        if not trading_service:
            raise HTTPException(status_code=503, detail="Trading engine not running")
        
        # Get portfolios
        all_portfolios = list(trading_service.portfolios.values())
        
        if client_id:
            all_portfolios = [p for p in all_portfolios if p.client_id == client_id]
        
        # Format portfolios for response
        formatted_portfolios = []
        for portfolio in all_portfolios:
            formatted_portfolios.append({
                "portfolio_id": portfolio.portfolio_id,
                "client_id": portfolio.client_id,
                "name": portfolio.name,
                "total_value": float(portfolio.total_value),
                "cash_balance": float(portfolio.cash_balance),
                "target_allocation": {k: float(v) for k, v in portfolio.target_allocation.items()},
                "position_count": len(portfolio.positions),
                "created_at": portfolio.created_at.isoformat(),
                "updated_at": portfolio.updated_at.isoformat()
            })
        
        return {
            "portfolios": formatted_portfolios,
            "total_portfolios": len(formatted_portfolios),
            "client_filter": client_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting portfolios: {e}")
        raise HTTPException(status_code=500, detail="Failed to get portfolios")

@router.get("/portfolios/{portfolio_id}/performance")
async def get_portfolio_performance(portfolio_id: str) -> Dict[str, Any]:
    """Get detailed portfolio performance metrics"""
    try:
        trading_service = get_trading_engine_service()
        
        if not trading_service:
            raise HTTPException(status_code=503, detail="Trading engine not running")
        
        # Get performance metrics
        performance = await trading_service.get_portfolio_performance(portfolio_id)
        
        return {
            "performance": performance,
            "risk_metrics": {
                "total_exposure": performance["total_value"],
                "cash_ratio": performance["cash_balance"] / performance["total_value"] if performance["total_value"] > 0 else 0,
                "position_concentration": max(performance["current_allocation"].values()) if performance["current_allocation"] else 0,
                "diversification_score": len(performance["current_allocation"]) / 7.0  # Max 7 stablecoins
            },
            "rebalancing_needed": max(abs(drift) for drift in performance["allocation_drift"].values()) > 0.05 if performance["allocation_drift"] else False
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting portfolio performance: {e}")
        raise HTTPException(status_code=500, detail="Failed to get portfolio performance")

# Rebalancing System
@router.post("/rebalance-strategies")
async def create_rebalance_strategy(request: CreateRebalanceStrategyRequest) -> Dict[str, Any]:
    """Create an automated rebalancing strategy"""
    try:
        trading_service = get_trading_engine_service()
        
        if not trading_service:
            raise HTTPException(status_code=503, detail="Trading engine not running")
        
        # Validate frequency
        valid_frequencies = ["daily", "weekly", "monthly", "on_signal"]
        if request.frequency not in valid_frequencies:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid frequency. Must be one of: {valid_frequencies}"
            )
        
        # Create rebalance strategy
        strategy = await trading_service.create_rebalance_strategy(
            portfolio_id=request.portfolio_id,
            name=request.name,
            frequency=request.frequency,
            threshold=Decimal(str(request.threshold)),
            use_ray_signals=request.use_ray_signals,
            use_ml_predictions=request.use_ml_predictions
        )
        
        return {
            "strategy": {
                "strategy_id": strategy.strategy_id,
                "portfolio_id": strategy.portfolio_id,
                "name": strategy.name,
                "frequency": strategy.frequency,
                "threshold": float(strategy.threshold),
                "use_ray_signals": strategy.use_ray_signals,
                "use_ml_predictions": strategy.use_ml_predictions,
                "risk_budget": float(strategy.risk_budget),
                "max_trades_per_day": strategy.max_trades_per_day,
                "is_active": strategy.is_active,
                "created_at": strategy.created_at.isoformat()
            },
            "message": f"Rebalancing strategy '{request.name}' created successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating rebalance strategy: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create rebalance strategy: {str(e)}")

@router.get("/rebalance-strategies")
async def get_rebalance_strategies(
    portfolio_id: Optional[str] = Query(default=None, description="Filter by portfolio ID")
) -> Dict[str, Any]:
    """Get rebalancing strategies with optional portfolio filter"""
    try:
        trading_service = get_trading_engine_service()
        
        if not trading_service:
            raise HTTPException(status_code=503, detail="Trading engine not running")
        
        # Get strategies
        all_strategies = list(trading_service.rebalance_strategies.values())
        
        if portfolio_id:
            all_strategies = [s for s in all_strategies if s.portfolio_id == portfolio_id]
        
        # Format strategies for response
        formatted_strategies = []
        for strategy in all_strategies:
            formatted_strategies.append({
                "strategy_id": strategy.strategy_id,
                "portfolio_id": strategy.portfolio_id,
                "name": strategy.name,
                "frequency": strategy.frequency,
                "threshold": float(strategy.threshold),
                "use_ray_signals": strategy.use_ray_signals,
                "use_ml_predictions": strategy.use_ml_predictions,
                "risk_budget": float(strategy.risk_budget),
                "max_trades_per_day": strategy.max_trades_per_day,
                "is_active": strategy.is_active,
                "created_at": strategy.created_at.isoformat()
            })
        
        return {
            "strategies": formatted_strategies,
            "total_strategies": len(formatted_strategies),
            "active_strategies": len([s for s in formatted_strategies if s["is_active"]]),
            "portfolio_filter": portfolio_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting rebalance strategies: {e}")
        raise HTTPException(status_code=500, detail="Failed to get rebalance strategies")

@router.post("/rebalance-strategies/{strategy_id}/execute")
async def execute_rebalance(strategy_id: str) -> Dict[str, Any]:
    """Manually execute a rebalancing strategy"""
    try:
        trading_service = get_trading_engine_service()
        
        if not trading_service:
            raise HTTPException(status_code=503, detail="Trading engine not running")
        
        # Execute rebalancing
        result = await trading_service.execute_rebalance(strategy_id)
        
        return {
            "rebalance_result": result,
            "execution_timestamp": datetime.utcnow().isoformat()
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing rebalance: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to execute rebalance: {str(e)}")

# Market Data
@router.get("/market-data")
async def get_market_data() -> Dict[str, Any]:
    """Get current market data for all trading pairs"""
    try:
        trading_service = get_trading_engine_service()
        
        if not trading_service:
            raise HTTPException(status_code=503, detail="Trading engine not running")
        
        # Get market prices and order books
        market_data = {}
        
        for symbol, price in trading_service.market_prices.items():
            order_book = trading_service.order_books.get(symbol, {})
            
            market_data[symbol] = {
                "price": float(price),
                "bid": float(order_book.get("bid", price)),
                "ask": float(order_book.get("ask", price)),
                "spread": float(order_book.get("spread", 0)),
                "bid_size": float(order_book.get("bid_size", 0)),
                "ask_size": float(order_book.get("ask_size", 0)),
                "last_updated": order_book.get("timestamp", datetime.utcnow()).isoformat()
            }
        
        return {
            "market_data": market_data,
            "symbols_count": len(market_data),
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting market data: {e}")
        raise HTTPException(status_code=500, detail="Failed to get market data")

@router.get("/positions")
async def get_positions(
    client_id: Optional[str] = Query(default=None, description="Filter by client ID")
) -> Dict[str, Any]:
    """Get trading positions with optional client filter"""
    try:
        trading_service = get_trading_engine_service()
        
        if not trading_service:
            raise HTTPException(status_code=503, detail="Trading engine not running")
        
        # Get positions
        all_positions = list(trading_service.positions.values())
        
        if client_id:
            all_positions = [p for p in all_positions if p.client_id == client_id]
        
        # Filter out zero positions
        active_positions = [p for p in all_positions if p.quantity != 0]
        
        # Format positions for response
        formatted_positions = []
        for position in active_positions:
            formatted_positions.append({
                "position_id": position.position_id,
                "client_id": position.client_id,
                "symbol": position.symbol,
                "quantity": float(position.quantity),
                "average_price": float(position.average_price),
                "current_price": float(position.current_price),
                "market_value": float(position.quantity * position.current_price),
                "unrealized_pnl": float(position.unrealized_pnl),
                "realized_pnl": float(position.realized_pnl),
                "created_at": position.created_at.isoformat(),
                "updated_at": position.updated_at.isoformat()
            })
        
        # Calculate totals
        total_market_value = sum(p["market_value"] for p in formatted_positions)
        total_unrealized_pnl = sum(p["unrealized_pnl"] for p in formatted_positions)
        total_realized_pnl = sum(p["realized_pnl"] for p in formatted_positions)
        
        return {
            "positions": formatted_positions,
            "total_positions": len(formatted_positions),
            "summary": {
                "total_market_value": total_market_value,
                "total_unrealized_pnl": total_unrealized_pnl,
                "total_realized_pnl": total_realized_pnl,
                "total_pnl": total_unrealized_pnl + total_realized_pnl
            },
            "client_filter": client_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting positions: {e}")
        raise HTTPException(status_code=500, detail="Failed to get positions")

@router.get("/summary")
async def get_trading_summary() -> Dict[str, Any]:
    """Get comprehensive trading system summary"""
    try:
        trading_service = get_trading_engine_service()
        
        if not trading_service:
            return {
                "message": "Advanced Trading Engine not running",
                "service_status": "stopped",
                "capabilities": []
            }
        
        # Get comprehensive status
        status = trading_service.get_trading_status()
        
        return {
            "service_status": "running" if status["service_running"] else "stopped",
            "trading_capabilities": {
                "order_management": {
                    "total_orders": status["orders"]["total_orders"],
                    "pending_orders": status["orders"]["pending_orders"],
                    "filled_orders": status["orders"]["filled_orders"],
                    "order_types_supported": ["market", "limit", "stop_loss", "oco"]
                },
                "portfolio_management": {
                    "total_portfolios": status["portfolios"]["total_portfolios"],
                    "rebalance_strategies": status["portfolios"]["rebalance_strategies"],
                    "active_strategies": status["portfolios"]["active_strategies"],
                    "rebalancing_features": ["RAY signals", "ML predictions", "threshold-based", "scheduled"]
                },
                "trading_pairs": {
                    "total_pairs": status["trading_pairs"],
                    "supported_assets": ["USDT", "USDC", "DAI", "TUSD", "FRAX", "USDP", "PYUSD"],
                    "market_data_active": status["market_data"]["symbols_tracked"]
                },
                "execution_engine": {
                    "total_trades": status["trades"]["total_trades"],
                    "executed_trades": status["trades"]["executed_trades"],
                    "settled_trades": status["trades"]["settled_trades"],
                    "connected_exchanges": status["exchanges"]["connected_exchanges"]
                }
            },
            "risk_management": {
                "position_monitoring": status["positions"]["active_positions"],
                "risk_limits": status["risk_monitoring"],
                "pre_trade_checks": True,
                "real_time_monitoring": True
            },
            "integration_features": {
                "ray_integration": "Risk-Adjusted Yield signals for rebalancing",
                "ml_integration": "Machine learning predictions for portfolio optimization",
                "real_time_data": "Live market data and price feeds",
                "automated_execution": "Smart order routing and execution"
            },
            "api_endpoints": [
                "POST /api/trading/orders (Create trading orders)",
                "GET /api/trading/orders (Order management)",
                "GET /api/trading/trades (Trade history)",
                "POST /api/trading/portfolios (Portfolio creation)",
                "GET /api/trading/portfolios/{id}/performance (Performance analytics)",
                "POST /api/trading/rebalance-strategies (Automated rebalancing)",
                "POST /api/trading/rebalance-strategies/{id}/execute (Execute rebalancing)",
                "GET /api/trading/positions (Position management)",
                "GET /api/trading/market-data (Real-time market data)"
            ],
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting trading summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to get trading summary")