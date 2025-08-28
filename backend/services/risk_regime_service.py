"""
Risk Regime Inversion Alert Service
Implements sophisticated risk regime detection based on SYI indicators
"""

import os
import asyncio
import logging
from datetime import date, datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
import json
import numpy as np
from scipy import stats
import pandas as pd
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from models.regime_models import (
    RegimeState, AlertType, AlertLevel,
    RegimeEvaluationRequest, RegimeEvaluationResponse,
    RegimeSignal, RegimeAlert, RegimeHistoryEntry, RegimeHistoryResponse,
    RegimeParameters, RegimeComponent, PegStatus,
    RegimeUpsertRequest, RegimeUpsertResponse,
    RegimeHealthResponse, RegimeStatsResponse
)


class RiskRegimeService:
    """
    Advanced Risk Regime Detection Service
    
    Implements mathematical models for:
    - SYI excess calculation and trend analysis
    - EMA-based spread calculation with volatility normalization
    - Momentum analysis via linear regression
    - Breadth calculation across RAY components
    - Peg stress override mechanism
    - State persistence and cooldown management
    """
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.logger = logging.getLogger(__name__)
        self.params = self._load_parameters()
        
        # Collections
        self.signals_collection = db.regime_signals
        self.state_collection = db.regime_state
        
        # In-memory cache for performance
        self._cache = {
            'last_evaluation': None,
            'historical_data': {},
            'current_state': None
        }
        
        # Alert webhooks
        self.alert_webhooks = self._load_alert_webhooks()
        
    def _load_parameters(self) -> RegimeParameters:
        """Load regime detection parameters from environment or defaults"""
        return RegimeParameters(
            ema_short=int(os.getenv('REGIME_EMA_SHORT', '7')),
            ema_long=int(os.getenv('REGIME_EMA_LONG', '30')),
            z_enter=float(os.getenv('REGIME_Z_ENTER', '0.5')),
            persist_days=int(os.getenv('REGIME_PERSIST_DAYS', '2')),
            cooldown_days=int(os.getenv('REGIME_COOLDOWN_DAYS', '7')),
            breadth_on_max=float(os.getenv('REGIME_BREADTH_ON_MAX', '40.0')),
            breadth_off_min=float(os.getenv('REGIME_BREADTH_OFF_MIN', '60.0')),
            peg_single_bps=int(os.getenv('REGIME_PEG_SINGLE_BPS', '100')),
            peg_agg_bps=int(os.getenv('REGIME_PEG_AGG_BPS', '150')),
            peg_clear_hours=int(os.getenv('REGIME_PEG_CLEAR_HOURS', '24')),
            volatility_epsilon=float(os.getenv('REGIME_VOL_EPSILON', '0.001'))
        )
    
    def _load_alert_webhooks(self) -> Dict[str, str]:
        """Load alert webhook URLs from environment"""
        webhooks = {}
        if slack_url := os.getenv('REGIME_SLACK_WEBHOOK'):
            webhooks['slack'] = slack_url
        if email_url := os.getenv('REGIME_EMAIL_WEBHOOK'):
            webhooks['email'] = email_url
        return webhooks
    
    async def evaluate_regime(self, request: RegimeEvaluationRequest) -> RegimeEvaluationResponse:
        """
        Main regime evaluation function
        
        Implements the complete risk regime detection algorithm:
        1. Calculate SYI excess and technical indicators
        2. Check for peg stress override
        3. Determine regime state based on signal thresholds
        4. Apply persistence and cooldown logic
        5. Generate alerts for state changes
        """
        try:
            eval_date = datetime.strptime(request.date, '%Y-%m-%d').date()
            
            # Get historical data for calculations
            historical_data = await self._get_historical_data(eval_date, days=max(self.params.ema_long + 5, 50))
            
            # Calculate technical indicators
            signal = await self._calculate_signal(request, historical_data)
            
            # Check for peg stress override
            peg_override = self._check_peg_override(request.peg_status)
            
            # Get previous state and cooldown info
            previous_state, cooldown_until, override_until = await self._get_state_info(eval_date)
            
            # Determine new regime state
            new_state = self._determine_regime_state(
                signal, peg_override, previous_state, eval_date, 
                cooldown_until, override_until, historical_data
            )
            
            # Check for regime flip and generate alerts
            alert = None
            if new_state != previous_state:
                alert = self._generate_alert(new_state, previous_state, signal, peg_override)
                
                # Send alert notifications
                if alert and alert.level == AlertLevel.CRITICAL:
                    await self._send_alert_notifications(alert, request.date, new_state, signal)
            
            # Calculate days in state
            days_in_state = await self._calculate_days_in_state(eval_date, new_state)
            
            # Store evaluation results
            await self._store_evaluation(request, signal, new_state, alert, eval_date)
            
            return RegimeEvaluationResponse(
                date=request.date,
                state=new_state,
                signal=signal,
                alert=alert,
                previous_state=previous_state,
                days_in_state=days_in_state,
                cooldown_until=cooldown_until.strftime('%Y-%m-%d') if cooldown_until else None,
                override_until=override_until.strftime('%Y-%m-%d') if override_until else None
            )
            
        except Exception as e:
            self.logger.error(f"Error evaluating regime for {request.date}: {str(e)}")
            raise
    
    async def _calculate_signal(self, request: RegimeEvaluationRequest, historical_data: List[Dict]) -> RegimeSignal:
        """
        Calculate all technical indicators for regime detection
        
        Implements:
        - SYI excess = SYI - T-Bill 3M
        - EMA short (7d) and long (30d) of SYI excess
        - Spread = EMA short - EMA long
        - Volatility = 30d rolling standard deviation
        - Z-score = Spread / max(volatility, epsilon)
        - Slope7 = annualized linear regression slope (7 days)
        - Breadth = % of components with RAY excess > EMA30(RAY excess)
        """
        
        # Current SYI excess
        syi_excess = request.syi - request.tbill_3m
        
        # Prepare data series with current point
        excess_series = []
        dates = []
        
        # Add historical data
        for entry in historical_data:
            if 'syi_excess' in entry:
                excess_series.append(entry['syi_excess'])
                dates.append(entry['date'])
        
        # Add current point
        excess_series.append(syi_excess)
        dates.append(datetime.strptime(request.date, '%Y-%m-%d').date())
        
        # Calculate EMAs
        ema_short = self._calculate_ema(excess_series, self.params.ema_short)
        ema_long = self._calculate_ema(excess_series, self.params.ema_long)
        spread = ema_short - ema_long
        
        # Calculate volatility (30-day rolling)
        if len(excess_series) >= self.params.ema_long:
            recent_data = excess_series[-self.params.ema_long:]
            volatility_30d = np.std(recent_data, ddof=1) if len(recent_data) > 1 else self.params.volatility_epsilon
        else:
            volatility_30d = self.params.volatility_epsilon
        
        # Calculate z-score
        z_score = spread / max(volatility_30d, self.params.volatility_epsilon)
        
        # Calculate 7-day momentum (slope)
        slope7 = self._calculate_momentum(excess_series[-7:] if len(excess_series) >= 7 else excess_series)
        
        # Calculate breadth
        breadth_pct = self._calculate_breadth(request.components, request.tbill_3m, historical_data)
        
        return RegimeSignal(
            syi_excess=syi_excess,
            spread=spread,
            z_score=z_score,
            slope7=slope7,
            breadth_pct=breadth_pct,
            volatility_30d=volatility_30d,
            ema_short=ema_short,
            ema_long=ema_long
        )
    
    def _calculate_ema(self, series: List[float], period: int) -> float:
        """Calculate Exponential Moving Average"""
        if not series:
            return 0.0
            
        if len(series) == 1:
            return series[0]
            
        alpha = 2.0 / (period + 1)
        ema = series[0]
        
        for value in series[1:]:
            ema = alpha * value + (1 - alpha) * ema
            
        return ema
    
    def _calculate_momentum(self, series: List[float]) -> float:
        """
        Calculate annualized momentum using linear regression slope
        Returns annualized slope coefficient
        """
        if len(series) < 2:
            return 0.0
            
        x = np.arange(len(series))
        y = np.array(series)
        
        # Linear regression
        slope, _, _, _, _ = stats.linregress(x, y)
        
        # Annualize the slope (multiply by 365 to get annual rate)
        return slope * 365
    
    def _calculate_breadth(self, components: List[RegimeComponent], tbill_rate: float, historical_data: List[Dict]) -> float:
        """
        Calculate breadth indicator
        Breadth% = % of stablecoins with RAY_excess > EMA30(RAY_excess)
        """
        if not components:
            return 50.0  # Neutral breadth if no components
            
        positive_count = 0
        
        for component in components:
            ray_excess = component.ray - tbill_rate
            
            # Get historical RAY excess for this component (simplified - use current excess)
            # In production, this would calculate EMA30 of historical RAY excess
            historical_ray_excess = self._get_component_ema30(component.symbol, historical_data)
            
            if ray_excess > historical_ray_excess:
                positive_count += 1
        
        return (positive_count / len(components)) * 100
    
    def _get_component_ema30(self, symbol: str, historical_data: List[Dict]) -> float:
        """Get EMA30 of RAY excess for a specific component"""
        # Simplified implementation - use average historical excess
        # In production, this would maintain component-specific historical data
        return 0.01  # Default 1% excess baseline
    
    def _check_peg_override(self, peg_status: Optional[PegStatus]) -> bool:
        """
        Check if peg stress should override regime to Risk-Off
        Override if: max_depeg >= 100 bps OR agg_depeg >= 150 bps
        """
        if not peg_status:
            return False
            
        return (peg_status.max_depeg_bps >= self.params.peg_single_bps or 
                peg_status.agg_depeg_bps >= self.params.peg_agg_bps)
    
    def _determine_regime_state(
        self, signal: RegimeSignal, peg_override: bool, previous_state: Optional[RegimeState],
        eval_date: date, cooldown_until: Optional[date], override_until: Optional[date],
        historical_data: List[Dict]
    ) -> RegimeState:
        """
        Determine regime state based on signal conditions and business logic
        
        Logic:
        1. If peg override active -> OFF_OVERRIDE
        2. If in cooldown period -> maintain previous state
        3. Check persistence requirements for flips
        4. Apply confirmation conditions (momentum or breadth)
        """
        
        # Override logic - always takes priority
        if peg_override:
            return RegimeState.OFF_OVERRIDE
            
        # Check if still in override period
        if override_until and eval_date <= override_until:
            return RegimeState.OFF_OVERRIDE
            
        # Initialize if no previous state
        if previous_state is None:
            return RegimeState.NEU
            
        # Check cooldown period
        if cooldown_until and eval_date <= cooldown_until:
            return previous_state
            
        # Check for regime flip conditions
        current_state = previous_state
        
        # Flip to Risk-Off conditions
        if (previous_state in [RegimeState.ON, RegimeState.NEU] and 
            signal.spread > 0 and signal.z_score >= self.params.z_enter):
            
            # Check persistence
            if self._check_persistence(eval_date, "flip_to_off", historical_data):
                # Check confirmation (momentum > 0 OR breadth >= 60%)
                if signal.slope7 > 0 or signal.breadth_pct >= self.params.breadth_off_min:
                    current_state = RegimeState.OFF
                    
        # Flip to Risk-On conditions  
        elif (previous_state in [RegimeState.OFF, RegimeState.NEU] and 
              signal.spread < 0 and signal.z_score <= -self.params.z_enter):
            
            # Check persistence
            if self._check_persistence(eval_date, "flip_to_on", historical_data):
                # Check confirmation (momentum < 0 OR breadth <= 40%)
                if signal.slope7 < 0 or signal.breadth_pct <= self.params.breadth_on_max:
                    current_state = RegimeState.ON
        
        return current_state
    
    def _check_persistence(self, eval_date: date, flip_type: str, historical_data: List[Dict]) -> bool:
        """
        Check if flip conditions have persisted for required number of days
        """
        # Simplified persistence check - in production would analyze historical signals
        # For now, assume persistence requirement is met if we have enough historical data
        return len(historical_data) >= self.params.persist_days
    
    def _generate_alert(
        self, new_state: RegimeState, previous_state: Optional[RegimeState], 
        signal: RegimeSignal, peg_override: bool
    ) -> Optional[RegimeAlert]:
        """Generate alert for regime changes"""
        
        if new_state == previous_state:
            return None
            
        # Determine alert type and level
        if peg_override:
            alert_type = AlertType.OVERRIDE_PEG
            alert_level = AlertLevel.CRITICAL
            message = f"Peg stress override - forced Risk-Off state"
            conditions = ["Peg stress detected", f"z-score: {signal.z_score:.2f}"]
            
        elif new_state == RegimeState.OFF and previous_state in [RegimeState.ON, RegimeState.NEU]:
            alert_type = AlertType.FLIP_CONFIRMED
            alert_level = AlertLevel.CRITICAL
            message = f"Risk regime flip confirmed: {previous_state.value if previous_state else 'NEU'} → Risk-Off"
            conditions = [
                f"Spread crossed zero upward: {signal.spread:.4f}",
                f"Z-score ≥ threshold: {signal.z_score:.2f}",
                f"Breadth: {signal.breadth_pct:.1f}%"
            ]
            
        elif new_state == RegimeState.ON and previous_state in [RegimeState.OFF, RegimeState.NEU]:
            alert_type = AlertType.FLIP_CONFIRMED  
            alert_level = AlertLevel.CRITICAL
            message = f"Risk regime flip confirmed: {previous_state.value if previous_state else 'NEU'} → Risk-On"
            conditions = [
                f"Spread crossed zero downward: {signal.spread:.4f}",
                f"Z-score ≤ threshold: {signal.z_score:.2f}",
                f"Breadth: {signal.breadth_pct:.1f}%"
            ]
            
        else:
            alert_type = AlertType.EARLY_WARNING
            alert_level = AlertLevel.WARNING
            message = f"Regime state changed: {previous_state.value if previous_state else 'NEU'} → {new_state.value}"
            conditions = [f"Z-score: {signal.z_score:.2f}"]
        
        return RegimeAlert(
            type=alert_type,
            level=alert_level,
            message=message,
            trigger_conditions=conditions
        )
    
    async def _send_alert_notifications(
        self, alert: RegimeAlert, eval_date: str, new_state: RegimeState, signal: RegimeSignal
    ):
        """Send alert notifications to configured webhooks"""
        
        alert_message = f"""[SYI ALERT] {eval_date}
State: {new_state.value} ({new_state.name})
Alert: {alert.type.value}
Spread={signal.spread:.4f} | z={signal.z_score:.2f} | Breadth={signal.breadth_pct:.0f}%
Message: {alert.message}"""

        # Send to configured webhooks
        for webhook_type, webhook_url in self.alert_webhooks.items():
            try:
                await self._send_webhook(webhook_url, alert_message, webhook_type)
                self.logger.info(f"Alert sent to {webhook_type}: {alert.type.value}")
            except Exception as e:
                self.logger.error(f"Failed to send alert to {webhook_type}: {str(e)}")
    
    async def _send_webhook(self, url: str, message: str, webhook_type: str):
        """Send webhook notification"""
        import aiohttp
        
        if webhook_type == 'slack':
            payload = {"text": message}
        else:
            payload = {"message": message, "subject": "Risk Regime Alert"}
            
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status != 200:
                    raise Exception(f"Webhook returned status {response.status}")
    
    async def _get_historical_data(self, eval_date: date, days: int = 50) -> List[Dict]:
        """Get historical regime data for calculations"""
        start_date = eval_date - timedelta(days=days)
        
        cursor = self.signals_collection.find({
            'date': {'$gte': start_date.strftime('%Y-%m-%d'), '$lt': eval_date.strftime('%Y-%m-%d')}
        }).sort('date', 1)
        
        historical_data = []
        async for doc in cursor:
            historical_data.append({
                'date': datetime.strptime(doc['date'], '%Y-%m-%d').date(),
                'syi_excess': doc.get('syi_excess', 0),
                'spread': doc.get('spread', 0),
                'z_score': doc.get('z_score', 0),
                'ema_short': doc.get('ema_short', 0),
                'ema_long': doc.get('ema_long', 0)
            })
        
        return historical_data
    
    async def _get_state_info(self, eval_date: date) -> Tuple[Optional[RegimeState], Optional[date], Optional[date]]:
        """Get previous state and cooldown information"""
        
        # Get most recent state before eval_date
        previous_doc = await self.state_collection.find_one({
            'date': {'$lt': eval_date.strftime('%Y-%m-%d')}
        }, sort=[('date', -1)])
        
        previous_state = None
        cooldown_until = None
        override_until = None
        
        if previous_doc:
            previous_state = RegimeState(previous_doc['state'])
            
            if previous_doc.get('cooldown_until'):
                cooldown_until = datetime.strptime(previous_doc['cooldown_until'], '%Y-%m-%d').date()
                
            if previous_doc.get('override_until'):
                override_until = datetime.strptime(previous_doc['override_until'], '%Y-%m-%d').date()
        
        return previous_state, cooldown_until, override_until
    
    async def _calculate_days_in_state(self, eval_date: date, current_state: RegimeState) -> int:
        """Calculate number of consecutive days in current state"""
        
        days_count = 1  # At least today
        check_date = eval_date - timedelta(days=1)
        
        while True:
            doc = await self.state_collection.find_one({'date': check_date.strftime('%Y-%m-%d')})
            if not doc or doc['state'] != current_state.value:
                break
                
            days_count += 1
            check_date -= timedelta(days=1)
            
            # Prevent infinite loops
            if days_count > 365:
                break
        
        return days_count
    
    async def _store_evaluation(
        self, request: RegimeEvaluationRequest, signal: RegimeSignal, 
        new_state: RegimeState, alert: Optional[RegimeAlert], eval_date: date
    ):
        """Store evaluation results to database"""
        
        # Store signal data
        signal_doc = {
            'date': request.date,
            'syi': request.syi,
            'tbill_3m': request.tbill_3m,
            'syi_excess': signal.syi_excess,
            'spread': signal.spread,
            'z_score': signal.z_score,
            'slope7': signal.slope7,
            'breadth_pct': signal.breadth_pct,
            'volatility_30d': signal.volatility_30d,
            'ema_short': signal.ema_short,
            'ema_long': signal.ema_long,
            'peg_max_bps': request.peg_status.max_depeg_bps if request.peg_status else 0,
            'peg_agg_bps': request.peg_status.agg_depeg_bps if request.peg_status else 0,
            'inserted_at': datetime.utcnow()
        }
        
        await self.signals_collection.replace_one(
            {'date': request.date}, signal_doc, upsert=True
        )
        
        # Store state data
        state_doc = {
            'date': request.date,
            'state': new_state.value,
            'alert_type': alert.type.value if alert else None,
            'alert_level': alert.level.value if alert else None,
            'inserted_at': datetime.utcnow()
        }
        
        # Set cooldown if this is a flip
        if alert and alert.type == AlertType.FLIP_CONFIRMED:
            cooldown_date = eval_date + timedelta(days=self.params.cooldown_days)
            state_doc['cooldown_until'] = cooldown_date.strftime('%Y-%m-%d')
        
        # Set override end if this is peg override
        if new_state == RegimeState.OFF_OVERRIDE:
            override_date = eval_date + timedelta(hours=self.params.peg_clear_hours)
            state_doc['override_until'] = override_date.strftime('%Y-%m-%d')
        
        await self.state_collection.replace_one(
            {'date': request.date}, state_doc, upsert=True
        )
        
        # Update cache
        self._cache['last_evaluation'] = request.date
        self._cache['current_state'] = new_state
    
    async def get_regime_history(
        self, from_date: str, to_date: str, limit: int = 100
    ) -> RegimeHistoryResponse:
        """Get historical regime data"""
        
        # Validate dates
        start_date = datetime.strptime(from_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(to_date, '%Y-%m-%d').date()
        
        if start_date > end_date:
            raise ValueError("from_date must be <= to_date")
        
        # Query signals and states
        pipeline = [
            {
                '$match': {
                    'date': {
                        '$gte': from_date,
                        '$lte': to_date
                    }
                }
            },
            {
                '$lookup': {
                    'from': 'regime_state',
                    'localField': 'date',
                    'foreignField': 'date',
                    'as': 'state_data'
                }
            },
            {
                '$sort': {'date': 1}
            },
            {
                '$limit': limit
            }
        ]
        
        cursor = self.signals_collection.aggregate(pipeline)
        series = []
        
        async for doc in cursor:
            state_data = doc.get('state_data', [{}])[0] if doc.get('state_data') else {}
            
            entry = RegimeHistoryEntry(
                date=doc['date'],
                state=RegimeState(state_data.get('state', 'NEU')),
                syi_excess=doc.get('syi_excess', 0),
                z_score=doc.get('z_score', 0),
                spread=doc.get('spread'),
                slope7=doc.get('slope7'),
                breadth_pct=doc.get('breadth_pct'),
                alert_type=AlertType(state_data['alert_type']) if state_data.get('alert_type') else None
            )
            series.append(entry)
        
        return RegimeHistoryResponse(
            series=series,
            total_entries=len(series),
            from_date=from_date,
            to_date=to_date
        )
    
    async def upsert_regime_data(self, request: RegimeUpsertRequest) -> RegimeUpsertResponse:
        """Upsert regime data (idempotent)"""
        
        eval_date = datetime.strptime(request.date, '%Y-%m-%d').date()
        
        # Check if data already exists
        existing_signal = await self.signals_collection.find_one({'date': request.date})
        existing_state = await self.state_collection.find_one({'date': request.date})
        
        created = False
        if not existing_signal or not existing_state or request.force_recalculate:
            # Perform evaluation
            eval_request = RegimeEvaluationRequest(
                date=request.date,
                syi=request.syi,
                tbill_3m=request.tbill_3m,
                components=request.components,
                peg_status=request.peg_status
            )
            
            eval_response = await self.evaluate_regime(eval_request)
            created = True
            alert_sent = eval_response.alert is not None and eval_response.alert.level == AlertLevel.CRITICAL
            
            return RegimeUpsertResponse(
                date=request.date,
                state=eval_response.state,
                message=f"Regime data {'updated' if existing_signal else 'created'} for {request.date}",
                created=created,
                alert_sent=alert_sent
            )
        else:
            return RegimeUpsertResponse(
                date=request.date,
                state=RegimeState(existing_state['state']),
                message=f"Regime data already exists for {request.date}",
                created=False,
                alert_sent=False
            )
    
    async def get_health_status(self) -> RegimeHealthResponse:
        """Get service health status"""
        
        # Get last evaluation info
        last_doc = await self.signals_collection.find_one(sort=[('date', -1)])
        last_evaluation = last_doc['date'] if last_doc else None
        
        # Count total evaluations
        total_count = await self.signals_collection.count_documents({})
        
        return RegimeHealthResponse(
            timestamp=datetime.utcnow().isoformat() + "Z",
            parameters=self.params,
            last_evaluation=last_evaluation,
            total_evaluations=total_count
        )
    
    async def get_regime_stats(self) -> RegimeStatsResponse:
        """Get regime statistics"""
        
        # Aggregate state statistics
        pipeline = [
            {
                '$group': {
                    '_id': '$state',
                    'count': {'$sum': 1}
                }
            }
        ]
        
        cursor = self.state_collection.aggregate(pipeline)
        state_counts = {}
        total_days = 0
        
        async for doc in cursor:
            state_counts[doc['_id']] = doc['count']
            total_days += doc['count']
        
        # Get current state
        current_doc = await self.state_collection.find_one(sort=[('date', -1)])
        current_state = RegimeState(current_doc['state']) if current_doc else None
        
        # Calculate days in current state
        days_in_current = await self._calculate_days_in_state(
            datetime.now().date(), current_state
        ) if current_state else 0
        
        # Count regime flips
        flip_count = await self.state_collection.count_documents({
            'alert_type': AlertType.FLIP_CONFIRMED.value
        })
        
        # Calculate average regime duration
        avg_duration = total_days / max(flip_count, 1) if flip_count > 0 else 0
        
        return RegimeStatsResponse(
            total_days=total_days,
            risk_on_days=state_counts.get('ON', 0),
            risk_off_days=state_counts.get('OFF', 0) + state_counts.get('OFF_OVERRIDE', 0),
            override_days=state_counts.get('OFF_OVERRIDE', 0),
            total_flips=flip_count,
            avg_regime_duration=avg_duration,
            current_state=current_state,
            days_in_current_state=days_in_current
        )


# Global service instance
_risk_regime_service: Optional[RiskRegimeService] = None


def get_risk_regime_service(db: AsyncIOMotorDatabase) -> RiskRegimeService:
    """Get or create risk regime service instance"""
    global _risk_regime_service
    if _risk_regime_service is None:
        _risk_regime_service = RiskRegimeService(db)
    return _risk_regime_service


async def start_risk_regime_service(db: AsyncIOMotorDatabase) -> RiskRegimeService:
    """Start the risk regime service"""
    global _risk_regime_service
    _risk_regime_service = RiskRegimeService(db)
    
    # Create database indexes
    await _risk_regime_service.signals_collection.create_index("date", unique=True)
    await _risk_regime_service.state_collection.create_index("date", unique=True)
    
    logging.info("Risk Regime Inversion Alert Service started")
    return _risk_regime_service


async def stop_risk_regime_service():
    """Stop the risk regime service"""
    global _risk_regime_service
    if _risk_regime_service:
        _risk_regime_service = None
        logging.info("Risk Regime Inversion Alert Service stopped")