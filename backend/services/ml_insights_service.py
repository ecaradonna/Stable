"""
Machine Learning & AI Insights Service (STEP 8)
Advanced ML models for yield prediction, anomaly detection, and market intelligence
"""

import asyncio
import logging
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import json
from pathlib import Path
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error
import joblib
import warnings
warnings.filterwarnings('ignore')

from .yield_aggregator import YieldAggregator
from .ray_calculator import RAYCalculator
from .syi_compositor import SYICompositor
from .batch_analytics_service import get_batch_analytics_service

logger = logging.getLogger(__name__)

@dataclass
class YieldPrediction:
    symbol: str
    current_yield: float
    predicted_yield_1d: float
    predicted_yield_7d: float
    predicted_yield_30d: float
    confidence_1d: float
    confidence_7d: float
    confidence_30d: float
    trend_direction: str  # "up", "down", "stable"
    prediction_timestamp: datetime

@dataclass
class AnomalyAlert:
    symbol: str
    anomaly_type: str  # "yield_spike", "yield_drop", "risk_increase", "liquidity_drop"
    severity: str  # "low", "medium", "high", "critical"
    current_value: float
    expected_value: float
    deviation_magnitude: float
    confidence_score: float
    timestamp: datetime
    description: str

@dataclass
class MarketInsight:
    insight_type: str  # "trend", "opportunity", "risk", "correlation"
    title: str
    description: str
    impact_level: str  # "low", "medium", "high"
    confidence: float
    supporting_data: Dict[str, Any]
    timestamp: datetime
    expiry_date: Optional[datetime] = None

@dataclass
class PortfolioOptimization:
    optimization_type: str  # "risk_parity", "max_sharpe", "min_variance"
    recommended_weights: Dict[str, float]
    expected_return: float
    expected_risk: float
    sharpe_ratio: float
    diversification_score: float
    current_vs_optimal: Dict[str, Any]
    timestamp: datetime

class MLInsightsService:
    """Machine Learning service for advanced yield analytics and predictions"""
    
    def __init__(self):
        self.yield_aggregator = YieldAggregator()
        self.ray_calculator = RAYCalculator()
        self.syi_compositor = SYICompositor()
        
        # ML Models
        self.yield_predictor = None
        self.anomaly_detector = None
        self.risk_predictor = None
        self.market_segmentation = None
        
        # Data preprocessing
        self.feature_scaler = StandardScaler()
        self.target_scaler = MinMaxScaler()
        
        # Model storage paths
        self.models_dir = Path("/app/data/ml_models")
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # Insights storage
        self.insights_cache = []
        self.predictions_cache = {}
        self.anomalies_cache = []
        
        # Configuration
        self.config = {
            "prediction_horizons": [1, 7, 30],  # days
            "anomaly_sensitivity": 0.15,  # contamination rate
            "min_training_samples": 100,
            "model_retrain_frequency": "weekly",
            "feature_importance_threshold": 0.01,
            "confidence_threshold": 0.70,
            "max_cache_size": 10000,
            "insight_retention_days": 30
        }
        
        self.is_initialized = False
    
    async def initialize(self):
        """Initialize ML models and load historical data"""
        if self.is_initialized:
            return
        
        logger.info("🤖 Initializing ML Insights Service...")
        
        try:
            # Load historical data
            historical_data = await self._load_historical_data()
            
            if len(historical_data) >= self.config["min_training_samples"]:
                # Train ML models
                await self._train_yield_predictor(historical_data)
                await self._train_anomaly_detector(historical_data)
                await self._train_risk_predictor(historical_data)
                await self._train_market_segmentation(historical_data)
                
                logger.info(f"✅ ML models trained with {len(historical_data)} samples")
            else:
                logger.warning(f"⚠️ Insufficient data for training ({len(historical_data)} < {self.config['min_training_samples']})")
                await self._initialize_default_models()
            
            self.is_initialized = True
            logger.info("✅ ML Insights Service initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize ML Insights Service: {e}")
            await self._initialize_default_models()
    
    async def _load_historical_data(self) -> pd.DataFrame:
        """Load historical data for ML training"""
        # Get historical data from batch analytics service
        batch_service = get_batch_analytics_service()
        
        if batch_service and batch_service.historical_data:
            df = pd.DataFrame(batch_service.historical_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp')
            
            # Create features
            df = self._create_features(df)
            
            return df
        else:
            # Fallback: create synthetic data for testing
            logger.warning("⚠️ No historical data available, generating synthetic data for testing")
            return self._generate_synthetic_data()
    
    def _create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create features for ML models"""
        # Time-based features
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['month'] = df['timestamp'].dt.month
        
        # Technical indicators
        for symbol in df['symbol'].unique():
            symbol_data = df[df['symbol'] == symbol].copy()
            
            # Moving averages
            symbol_data['ma_7'] = symbol_data['apy'].rolling(7).mean()
            symbol_data['ma_30'] = symbol_data['apy'].rolling(30).mean()
            
            # Volatility
            symbol_data['volatility_7'] = symbol_data['apy'].rolling(7).std()
            symbol_data['volatility_30'] = symbol_data['apy'].rolling(30).std()
            
            # Trend indicators
            symbol_data['trend_7'] = symbol_data['apy'] - symbol_data['ma_7']
            symbol_data['trend_30'] = symbol_data['apy'] - symbol_data['ma_30']
            
            # Risk-adjusted metrics
            symbol_data['ray_trend'] = symbol_data['ray'].diff()
            symbol_data['risk_penalty_trend'] = symbol_data['risk_penalty'].diff()
            
            df.loc[df['symbol'] == symbol, ['ma_7', 'ma_30', 'volatility_7', 'volatility_30', 
                                          'trend_7', 'trend_30', 'ray_trend', 'risk_penalty_trend']] = symbol_data[
                ['ma_7', 'ma_30', 'volatility_7', 'volatility_30', 'trend_7', 'trend_30', 'ray_trend', 'risk_penalty_trend']].values
        
        # Fill NaN values
        df = df.fillna(method='bfill').fillna(method='ffill')
        
        return df
    
    def _generate_synthetic_data(self) -> pd.DataFrame:
        """Generate synthetic historical data for testing"""
        np.random.seed(42)
        
        symbols = ['USDT', 'USDC', 'DAI', 'TUSD', 'FRAX']
        start_date = datetime.now() - timedelta(days=90)
        
        data = []
        for i in range(1000):  # 1000 synthetic data points
            timestamp = start_date + timedelta(hours=i * 2)  # Every 2 hours
            symbol = np.random.choice(symbols)
            
            # Generate realistic yield patterns
            base_yield = {
                'USDT': 4.5, 'USDC': 4.2, 'DAI': 3.8, 'TUSD': 4.0, 'FRAX': 5.2
            }[symbol]
            
            # Add noise and trends
            noise = np.random.normal(0, 0.5)
            trend = np.sin(i * 0.01) * 0.3  # Cyclical pattern
            apy = max(0.1, base_yield + noise + trend)
            
            # Generate correlated RAY and risk metrics
            ray = apy * (0.8 + np.random.normal(0, 0.1))
            risk_penalty = min(0.8, max(0.0, 0.2 + np.random.normal(0, 0.05)))
            confidence_score = min(1.0, max(0.3, 0.8 + np.random.normal(0, 0.1)))
            
            data.append({
                'timestamp': timestamp,
                'symbol': symbol,
                'apy': apy,
                'ray': ray,
                'risk_penalty': risk_penalty,
                'confidence_score': confidence_score,
                'peg_stability_score': min(1.0, max(0.7, 0.95 + np.random.normal(0, 0.02))),
                'liquidity_score': min(1.0, max(0.5, 0.85 + np.random.normal(0, 0.05)))
            })
        
        df = pd.DataFrame(data)
        return self._create_features(df)
    
    async def _train_yield_predictor(self, data: pd.DataFrame):
        """Train yield prediction model"""
        try:
            # Prepare features and targets
            feature_cols = ['hour', 'day_of_week', 'month', 'ma_7', 'ma_30', 
                           'volatility_7', 'volatility_30', 'trend_7', 'trend_30',
                           'ray', 'risk_penalty', 'confidence_score', 
                           'peg_stability_score', 'liquidity_score']
            
            # Filter out rows with NaN values
            clean_data = data.dropna(subset=feature_cols + ['apy'])
            
            if len(clean_data) < 50:
                logger.warning("⚠️ Insufficient clean data for yield predictor training")
                return
            
            X = clean_data[feature_cols].values
            y = clean_data['apy'].values
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Scale features
            X_train_scaled = self.feature_scaler.fit_transform(X_train)
            X_test_scaled = self.feature_scaler.transform(X_test)
            
            # Train model
            self.yield_predictor = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )
            
            self.yield_predictor.fit(X_train_scaled, y_train)
            
            # Evaluate model
            y_pred = self.yield_predictor.predict(X_test_scaled)
            mse = mean_squared_error(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            
            # Save model
            model_path = self.models_dir / "yield_predictor.pkl"
            joblib.dump({
                'model': self.yield_predictor,
                'scaler': self.feature_scaler,
                'feature_cols': feature_cols,
                'metrics': {'mse': mse, 'mae': mae}
            }, model_path)
            
            logger.info(f"✅ Yield predictor trained - MSE: {mse:.4f}, MAE: {mae:.4f}")
            
        except Exception as e:
            logger.error(f"❌ Failed to train yield predictor: {e}")
    
    async def _train_anomaly_detector(self, data: pd.DataFrame):
        """Train anomaly detection model"""
        try:
            # Prepare features for anomaly detection
            feature_cols = ['apy', 'ray', 'risk_penalty', 'volatility_7', 'volatility_30',
                           'peg_stability_score', 'liquidity_score']
            
            clean_data = data.dropna(subset=feature_cols)
            
            if len(clean_data) < 50:
                logger.warning("⚠️ Insufficient data for anomaly detector training")
                return
            
            X = clean_data[feature_cols].values
            
            # Scale features
            X_scaled = self.feature_scaler.fit_transform(X)
            
            # Train anomaly detector
            self.anomaly_detector = IsolationForest(
                contamination=self.config["anomaly_sensitivity"],
                random_state=42,
                n_jobs=-1
            )
            
            self.anomaly_detector.fit(X_scaled)
            
            # Evaluate on training data
            anomaly_scores = self.anomaly_detector.decision_function(X_scaled)
            anomaly_labels = self.anomaly_detector.predict(X_scaled)
            
            # Save model
            model_path = self.models_dir / "anomaly_detector.pkl"
            joblib.dump({
                'model': self.anomaly_detector,
                'scaler': self.feature_scaler,
                'feature_cols': feature_cols
            }, model_path)
            
            anomaly_rate = len(anomaly_labels[anomaly_labels == -1]) / len(anomaly_labels)
            logger.info(f"✅ Anomaly detector trained - Anomaly rate: {anomaly_rate:.2%}")
            
        except Exception as e:
            logger.error(f"❌ Failed to train anomaly detector: {e}")
    
    async def _train_risk_predictor(self, data: pd.DataFrame):
        """Train risk prediction model"""
        try:
            # Prepare features and targets for risk prediction
            feature_cols = ['apy', 'ma_7', 'ma_30', 'volatility_7', 'volatility_30',
                           'peg_stability_score', 'liquidity_score']
            
            clean_data = data.dropna(subset=feature_cols + ['risk_penalty'])
            
            if len(clean_data) < 50:
                logger.warning("⚠️ Insufficient data for risk predictor training")
                return
            
            X = clean_data[feature_cols].values
            y = clean_data['risk_penalty'].values
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Scale features
            X_train_scaled = self.feature_scaler.fit_transform(X_train)
            X_test_scaled = self.feature_scaler.transform(X_test)
            
            # Train model
            self.risk_predictor = RandomForestRegressor(
                n_estimators=100,
                max_depth=8,
                random_state=42,
                n_jobs=-1
            )
            
            self.risk_predictor.fit(X_train_scaled, y_train)
            
            # Evaluate model
            y_pred = self.risk_predictor.predict(X_test_scaled)
            mse = mean_squared_error(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            
            # Save model
            model_path = self.models_dir / "risk_predictor.pkl"
            joblib.dump({
                'model': self.risk_predictor,
                'scaler': self.feature_scaler,
                'feature_cols': feature_cols,
                'metrics': {'mse': mse, 'mae': mae}
            }, model_path)
            
            logger.info(f"✅ Risk predictor trained - MSE: {mse:.4f}, MAE: {mae:.4f}")
            
        except Exception as e:
            logger.error(f"❌ Failed to train risk predictor: {e}")
    
    async def _train_market_segmentation(self, data: pd.DataFrame):
        """Train market segmentation model"""
        try:
            # Prepare features for clustering
            feature_cols = ['apy', 'ray', 'risk_penalty', 'peg_stability_score', 'liquidity_score']
            
            clean_data = data.dropna(subset=feature_cols)
            
            if len(clean_data) < 50:
                logger.warning("⚠️ Insufficient data for market segmentation training")
                return
            
            X = clean_data[feature_cols].values
            
            # Scale features
            X_scaled = self.feature_scaler.fit_transform(X)
            
            # Train clustering model
            self.market_segmentation = KMeans(
                n_clusters=4,  # Conservative, Growth, Aggressive, Speculative
                random_state=42,
                n_init=10
            )
            
            cluster_labels = self.market_segmentation.fit_predict(X_scaled)
            
            # Analyze clusters
            cluster_analysis = {}
            for i in range(4):
                cluster_data = clean_data[cluster_labels == i]
                cluster_analysis[i] = {
                    'count': len(cluster_data),
                    'avg_apy': cluster_data['apy'].mean(),
                    'avg_ray': cluster_data['ray'].mean(),
                    'avg_risk': cluster_data['risk_penalty'].mean(),
                    'avg_peg_stability': cluster_data['peg_stability_score'].mean(),
                    'avg_liquidity': cluster_data['liquidity_score'].mean()
                }
            
            # Save model
            model_path = self.models_dir / "market_segmentation.pkl"
            joblib.dump({
                'model': self.market_segmentation,
                'scaler': self.feature_scaler,
                'feature_cols': feature_cols,
                'cluster_analysis': cluster_analysis
            }, model_path)
            
            logger.info(f"✅ Market segmentation trained - 4 clusters identified")
            
        except Exception as e:
            logger.error(f"❌ Failed to train market segmentation: {e}")
    
    async def _initialize_default_models(self):
        """Initialize default models when insufficient data"""
        logger.info("🔧 Initializing default ML models...")
        
        # Create minimal models for basic functionality
        self.yield_predictor = RandomForestRegressor(n_estimators=10, random_state=42)
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self.risk_predictor = RandomForestRegressor(n_estimators=10, random_state=42)
        self.market_segmentation = KMeans(n_clusters=3, random_state=42)
        
        # Create dummy training data
        X_dummy = np.random.random((50, 10))
        y_dummy = np.random.random(50)
        
        self.yield_predictor.fit(X_dummy, y_dummy)
        self.anomaly_detector.fit(X_dummy)
        self.risk_predictor.fit(X_dummy, y_dummy)
        self.market_segmentation.fit(X_dummy[:, :5])
        
        self.is_initialized = True
        logger.info("✅ Default ML models initialized")
    
    async def predict_yields(self, current_data: List[Dict[str, Any]]) -> List[YieldPrediction]:
        """Generate yield predictions for multiple horizons"""
        if not self.is_initialized:
            await self.initialize()
        
        predictions = []
        
        try:
            for data in current_data:
                # Extract features
                features = self._extract_prediction_features(data)
                
                if features is None:
                    continue
                
                # Make predictions for different horizons
                pred_1d, conf_1d = self._predict_yield_horizon(features, 1)
                pred_7d, conf_7d = self._predict_yield_horizon(features, 7)
                pred_30d, conf_30d = self._predict_yield_horizon(features, 30)
                
                # Determine trend direction
                current_yield = float(data.get('currentYield', 0))
                trend = self._determine_trend_direction(current_yield, pred_7d)
                
                prediction = YieldPrediction(
                    symbol=data.get('stablecoin', 'Unknown'),
                    current_yield=current_yield,
                    predicted_yield_1d=pred_1d,
                    predicted_yield_7d=pred_7d,
                    predicted_yield_30d=pred_30d,
                    confidence_1d=conf_1d,
                    confidence_7d=conf_7d,
                    confidence_30d=conf_30d,
                    trend_direction=trend,
                    prediction_timestamp=datetime.utcnow()
                )
                
                predictions.append(prediction)
            
            # Cache predictions
            for pred in predictions:
                self.predictions_cache[pred.symbol] = pred
            
            logger.info(f"🔮 Generated predictions for {len(predictions)} symbols")
            
        except Exception as e:
            logger.error(f"❌ Error generating yield predictions: {e}")
        
        return predictions
    
    def _extract_prediction_features(self, data: Dict[str, Any]) -> Optional[np.ndarray]:
        """Extract features for prediction from current data"""
        try:
            # Get current time features
            now = datetime.utcnow()
            hour = now.hour
            day_of_week = now.weekday()
            month = now.month
            
            # Get yield data
            apy = float(data.get('currentYield', 0))
            
            # Get metadata if available
            metadata = data.get('metadata', {})
            
            # Extract risk factors from RAY calculation if available
            protocol_info = metadata.get('protocol_info', {})
            ray_data = metadata.get('ray_calculation', {})
            
            ray = ray_data.get('risk_adjusted_yield', apy * 0.85)  # Fallback
            risk_penalty = ray_data.get('risk_penalty', 0.15)  # Fallback
            confidence_score = ray_data.get('confidence_score', 0.75)  # Fallback
            
            peg_stability = protocol_info.get('peg_stability_score', 0.95)  # Fallback
            liquidity_score = protocol_info.get('liquidity_score', 0.80)  # Fallback
            
            # Create feature vector (matching training features)
            features = np.array([
                hour, day_of_week, month,
                apy, apy,  # ma_7, ma_30 (use current as fallback)
                0.5, 0.5,  # volatility_7, volatility_30 (default)
                0.0, 0.0,  # trend_7, trend_30 (default)
                ray, risk_penalty, confidence_score,
                peg_stability, liquidity_score
            ]).reshape(1, -1)
            
            return features
            
        except Exception as e:
            logger.error(f"❌ Error extracting prediction features: {e}")
            return None
    
    def _predict_yield_horizon(self, features: np.ndarray, horizon_days: int) -> Tuple[float, float]:
        """Predict yield for specific horizon"""
        try:
            if self.yield_predictor is None:
                return 0.0, 0.0
            
            # Scale features
            features_scaled = self.feature_scaler.transform(features)
            
            # Make prediction
            prediction = self.yield_predictor.predict(features_scaled)[0]
            
            # Adjust prediction based on horizon (longer horizons = more uncertainty)
            horizon_factor = 1.0 + (horizon_days - 1) * 0.01  # Small adjustment per day
            adjusted_prediction = prediction * horizon_factor
            
            # Calculate confidence (decreases with horizon)
            base_confidence = 0.85
            confidence = base_confidence * (1.0 - horizon_days * 0.01)
            confidence = max(0.3, min(0.95, confidence))
            
            return max(0.1, adjusted_prediction), confidence
            
        except Exception as e:
            logger.error(f"❌ Error predicting yield for horizon {horizon_days}: {e}")
            return 0.0, 0.0
    
    def _determine_trend_direction(self, current: float, predicted: float) -> str:
        """Determine trend direction"""
        if abs(predicted - current) < 0.1:
            return "stable"
        elif predicted > current:
            return "up"
        else:
            return "down"
    
    async def detect_anomalies(self, current_data: List[Dict[str, Any]]) -> List[AnomalyAlert]:
        """Detect anomalies in current market data"""
        if not self.is_initialized:
            await self.initialize()
        
        anomalies = []
        
        try:
            for data in current_data:
                # Extract features for anomaly detection
                features = self._extract_anomaly_features(data)
                
                if features is None:
                    continue
                
                # Detect anomalies
                alerts = self._detect_data_anomalies(data, features)
                anomalies.extend(alerts)
            
            # Cache anomalies
            self.anomalies_cache.extend(anomalies)
            
            # Keep cache size manageable
            if len(self.anomalies_cache) > self.config["max_cache_size"]:
                self.anomalies_cache = self.anomalies_cache[-self.config["max_cache_size"]:]
            
            if anomalies:
                logger.info(f"🚨 Detected {len(anomalies)} anomalies")
            
        except Exception as e:
            logger.error(f"❌ Error detecting anomalies: {e}")
        
        return anomalies
    
    def _extract_anomaly_features(self, data: Dict[str, Any]) -> Optional[np.ndarray]:
        """Extract features for anomaly detection"""
        try:
            apy = float(data.get('currentYield', 0))
            
            # Get metadata
            metadata = data.get('metadata', {})
            ray_data = metadata.get('ray_calculation', {})
            protocol_info = metadata.get('protocol_info', {})
            
            ray = ray_data.get('risk_adjusted_yield', apy * 0.85)
            risk_penalty = ray_data.get('risk_penalty', 0.15)
            peg_stability = protocol_info.get('peg_stability_score', 0.95)
            liquidity_score = protocol_info.get('liquidity_score', 0.80)
            
            # Create feature vector
            features = np.array([
                apy, ray, risk_penalty, 0.5, 0.5,  # volatility fallbacks
                peg_stability, liquidity_score
            ]).reshape(1, -1)
            
            return features
            
        except Exception as e:
            logger.error(f"❌ Error extracting anomaly features: {e}")
            return None
    
    def _detect_data_anomalies(self, data: Dict[str, Any], features: np.ndarray) -> List[AnomalyAlert]:
        """Detect specific types of anomalies"""
        alerts = []
        
        try:
            if self.anomaly_detector is None:
                return alerts
            
            # Scale features
            features_scaled = self.feature_scaler.transform(features)
            
            # Get anomaly score
            anomaly_score = self.anomaly_detector.decision_function(features_scaled)[0]
            is_anomaly = self.anomaly_detector.predict(features_scaled)[0] == -1
            
            if is_anomaly:
                symbol = data.get('stablecoin', 'Unknown')
                current_yield = float(data.get('currentYield', 0))
                
                # Determine anomaly type and severity
                if current_yield > 20:  # Very high yield
                    anomaly_type = "yield_spike"
                    severity = "high" if current_yield > 50 else "medium"
                    description = f"Unusually high yield detected: {current_yield:.2f}%"
                elif current_yield < 1:  # Very low yield
                    anomaly_type = "yield_drop"
                    severity = "medium"
                    description = f"Unusually low yield detected: {current_yield:.2f}%"
                else:
                    anomaly_type = "general_anomaly"
                    severity = "low"
                    description = f"Anomalous market behavior detected for {symbol}"
                
                alert = AnomalyAlert(
                    symbol=symbol,
                    anomaly_type=anomaly_type,
                    severity=severity,
                    current_value=current_yield,
                    expected_value=5.0,  # Rough market average
                    deviation_magnitude=abs(anomaly_score),
                    confidence_score=min(0.95, abs(anomaly_score) / 2),
                    timestamp=datetime.utcnow(),
                    description=description
                )
                
                alerts.append(alert)
        
        except Exception as e:
            logger.error(f"❌ Error detecting data anomalies: {e}")
        
        return alerts
    
    async def generate_market_insights(self, current_data: List[Dict[str, Any]]) -> List[MarketInsight]:
        """Generate AI-powered market insights"""
        insights = []
        
        try:
            # Yield trend analysis
            yield_insights = self._analyze_yield_trends(current_data)
            insights.extend(yield_insights)
            
            # Risk opportunity analysis
            risk_insights = self._analyze_risk_opportunities(current_data)
            insights.extend(risk_insights)
            
            # Market correlation analysis
            correlation_insights = self._analyze_market_correlations(current_data)
            insights.extend(correlation_insights)
            
            # Portfolio optimization insights
            portfolio_insights = self._analyze_portfolio_opportunities(current_data)
            insights.extend(portfolio_insights)
            
            # Cache insights
            self.insights_cache.extend(insights)
            
            # Clean old insights
            cutoff_date = datetime.utcnow() - timedelta(days=self.config["insight_retention_days"])
            self.insights_cache = [
                insight for insight in self.insights_cache 
                if insight.timestamp > cutoff_date
            ]
            
            logger.info(f"💡 Generated {len(insights)} market insights")
            
        except Exception as e:
            logger.error(f"❌ Error generating market insights: {e}")
        
        return insights
    
    def _analyze_yield_trends(self, data: List[Dict[str, Any]]) -> List[MarketInsight]:
        """Analyze yield trends and patterns"""
        insights = []
        
        if not data:
            return insights
        
        yields = [float(d.get('currentYield', 0)) for d in data]
        avg_yield = np.mean(yields)
        max_yield = np.max(yields)
        min_yield = np.min(yields)
        
        # High yield opportunity insight
        if max_yield > avg_yield * 1.5:
            high_yield_symbol = next(
                d.get('stablecoin', 'Unknown') for d in data 
                if float(d.get('currentYield', 0)) == max_yield
            )
            
            insights.append(MarketInsight(
                insight_type="opportunity",
                title=f"High Yield Opportunity in {high_yield_symbol}",
                description=f"{high_yield_symbol} offers {max_yield:.2f}% yield, significantly above market average of {avg_yield:.2f}%",
                impact_level="high",
                confidence=0.85,
                supporting_data={
                    "symbol": high_yield_symbol,
                    "yield": max_yield,
                    "market_average": avg_yield,
                    "premium": (max_yield - avg_yield) / avg_yield
                },
                timestamp=datetime.utcnow(),
                expiry_date=datetime.utcnow() + timedelta(hours=6)
            ))
        
        # Market dispersion insight
        yield_std = np.std(yields)
        if yield_std > avg_yield * 0.3:
            insights.append(MarketInsight(
                insight_type="trend",
                title="High Market Yield Dispersion",
                description=f"Significant yield variation across stablecoins (σ={yield_std:.2f}%) suggests opportunities for yield arbitrage",
                impact_level="medium",
                confidence=0.75,
                supporting_data={
                    "yield_std": yield_std,
                    "yield_range": max_yield - min_yield,
                    "coefficient_variation": yield_std / avg_yield
                },
                timestamp=datetime.utcnow()
            ))
        
        return insights
    
    def _analyze_risk_opportunities(self, data: List[Dict[str, Any]]) -> List[MarketInsight]:
        """Analyze risk-adjusted opportunities"""
        insights = []
        
        # Calculate risk-adjusted metrics
        risk_adjusted_data = []
        for d in data:
            metadata = d.get('metadata', {})
            ray_data = metadata.get('ray_calculation', {})
            
            if ray_data:
                risk_adjusted_data.append({
                    'symbol': d.get('stablecoin', 'Unknown'),
                    'yield': float(d.get('currentYield', 0)),
                    'ray': ray_data.get('risk_adjusted_yield', 0),
                    'risk_penalty': ray_data.get('risk_penalty', 0)
                })
        
        if risk_adjusted_data:
            # Best risk-adjusted opportunity
            best_ray = max(risk_adjusted_data, key=lambda x: x['ray'])
            
            insights.append(MarketInsight(
                insight_type="opportunity",
                title=f"Best Risk-Adjusted Yield: {best_ray['symbol']}",
                description=f"{best_ray['symbol']} offers the best risk-adjusted yield at {best_ray['ray']:.2f}% (RAY) vs {best_ray['yield']:.2f}% gross yield",
                impact_level="high",
                confidence=0.80,
                supporting_data=best_ray,
                timestamp=datetime.utcnow()
            ))
            
            # Low risk opportunity
            low_risk_options = [d for d in risk_adjusted_data if d['risk_penalty'] < 0.20]
            if low_risk_options:
                best_low_risk = max(low_risk_options, key=lambda x: x['ray'])
                
                insights.append(MarketInsight(
                    insight_type="risk",
                    title=f"Low Risk Option: {best_low_risk['symbol']}",
                    description=f"{best_low_risk['symbol']} combines low risk (penalty: {best_low_risk['risk_penalty']:.1%}) with decent RAY of {best_low_risk['ray']:.2f}%",
                    impact_level="medium",
                    confidence=0.85,
                    supporting_data=best_low_risk,
                    timestamp=datetime.utcnow()
                ))
        
        return insights
    
    def _analyze_market_correlations(self, data: List[Dict[str, Any]]) -> List[MarketInsight]:
        """Analyze correlations between different metrics"""
        insights = []
        
        # Simple correlation analysis
        if len(data) >= 3:
            yields = [float(d.get('currentYield', 0)) for d in data]
            
            # Check for correlation patterns
            avg_yield = np.mean(yields)
            high_yield_count = len([y for y in yields if y > avg_yield * 1.2])
            
            if high_yield_count >= len(yields) * 0.6:
                insights.append(MarketInsight(
                    insight_type="trend",
                    title="Market-Wide Yield Expansion",
                    description=f"{high_yield_count}/{len(yields)} stablecoins showing above-average yields, indicating broad market expansion",
                    impact_level="medium",
                    confidence=0.70,
                    supporting_data={
                        "high_yield_count": high_yield_count,
                        "total_count": len(yields),
                        "percentage": high_yield_count / len(yields)
                    },
                    timestamp=datetime.utcnow()
                ))
        
        return insights
    
    def _analyze_portfolio_opportunities(self, data: List[Dict[str, Any]]) -> List[MarketInsight]:
        """Analyze portfolio optimization opportunities"""
        insights = []
        
        if len(data) >= 3:
            # Simple diversification insight
            symbols = [d.get('stablecoin', 'Unknown') for d in data]
            yields = [float(d.get('currentYield', 0)) for d in data]
            
            # Calculate simple portfolio metrics
            equal_weight_return = np.mean(yields)
            max_weight_return = np.max(yields)
            
            potential_improvement = (max_weight_return - equal_weight_return) / equal_weight_return
            
            if potential_improvement > 0.1:  # 10% improvement potential
                best_symbol = symbols[yields.index(max_weight_return)]
                
                insights.append(MarketInsight(
                    insight_type="opportunity",
                    title="Portfolio Optimization Opportunity",
                    description=f"Overweighting {best_symbol} could improve portfolio yield by {potential_improvement:.1%} vs equal weighting",
                    impact_level="medium",
                    confidence=0.65,
                    supporting_data={
                        "best_symbol": best_symbol,
                        "improvement_potential": potential_improvement,
                        "equal_weight_return": equal_weight_return,
                        "max_weight_return": max_weight_return
                    },
                    timestamp=datetime.utcnow()
                ))
        
        return insights
    
    def get_ml_status(self) -> Dict[str, Any]:
        """Get ML service status and metrics"""
        return {
            "service_initialized": self.is_initialized,
            "models_trained": {
                "yield_predictor": self.yield_predictor is not None,
                "anomaly_detector": self.anomaly_detector is not None,
                "risk_predictor": self.risk_predictor is not None,
                "market_segmentation": self.market_segmentation is not None
            },
            "cache_statistics": {
                "predictions_cached": len(self.predictions_cache),
                "insights_cached": len(self.insights_cache),
                "anomalies_cached": len(self.anomalies_cache)
            },
            "configuration": self.config,
            "models_directory": str(self.models_dir),
            "last_update": datetime.utcnow().isoformat()
        }

# Global ML insights service instance
ml_insights_service = None

async def start_ml_insights():
    """Start the global ML insights service"""
    global ml_insights_service
    
    if ml_insights_service is None:
        ml_insights_service = MLInsightsService()
        await ml_insights_service.initialize()
        logger.info("🚀 ML Insights service started")
    else:
        logger.info("⚠️ ML Insights service already running")

async def stop_ml_insights():
    """Stop the global ML insights service"""
    global ml_insights_service
    
    if ml_insights_service:
        ml_insights_service = None
        logger.info("🛑 ML Insights service stopped")

def get_ml_insights_service() -> Optional[MLInsightsService]:
    """Get the global ML insights service"""
    return ml_insights_service