import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import math

from models.index_models import IndexValue, StablecoinConstituent
from services.crypto_compare_service import CryptoCompareService
from services.defi_llama_service import DefiLlamaService
from services.binance_service import BinanceService
from services.ray_calculator import RAYCalculator
from services.syi_compositor import SYICompositor
from services.yield_aggregator import YieldAggregator

logger = logging.getLogger(__name__)

class StableYieldIndexCalculator:
    """
    Core engine for calculating the StableYield Index (SYI)
    
    Formula: SYI_t = Σ(w_i,t * RAY_i,t)
    Where:
    - RAY_i,t = Risk-Adjusted Yield of stablecoin i at time t
    - w_i,t = Market cap weight of stablecoin i
    - RAY = APY × f(peg_stability, liquidity, counterparty_risk)
    """
    
    def __init__(self):
        self.crypto_compare = CryptoCompareService()
        self.defi_llama = DefiLlamaService()
        self.binance = BinanceService()
        self.ray_calculator = RAYCalculator()
        self.syi_compositor = SYICompositor()
        self.yield_aggregator = YieldAggregator()
        
        # Caching
        self.cache = {}
        self.cache_expiry = {}
        self.cache_duration = timedelta(minutes=5)
        
        # Core stablecoins for Phase 1
        self.constituents = [
            {"symbol": "USDT", "name": "Tether"},
            {"symbol": "USDC", "name": "USD Coin"},
            {"symbol": "DAI", "name": "Dai"},
            {"symbol": "TUSD", "name": "TrueUSD"},
            {"symbol": "FRAX", "name": "Frax"},
            {"symbol": "USDP", "name": "Pax Dollar"}
        ]
    
    def _get_fallback_index(self) -> IndexValue:
        """Return a fallback index value when calculation fails"""
        fallback_constituents = [
            StablecoinConstituent(
                symbol="USDT",
                weight=0.4,
                yield_value=3.5,
                liquidity="$83,000,000,000",
                risk_score=0.75,
                source="fallback",
                last_updated=datetime.utcnow().isoformat()
            ),
            StablecoinConstituent(
                symbol="USDC", 
                weight=0.35,
                yield_value=3.2,
                liquidity="$25,000,000,000",
                risk_score=0.90,
                source="fallback",
                last_updated=datetime.utcnow().isoformat()
            ),
            StablecoinConstituent(
                symbol="DAI",
                weight=0.25,
                yield_value=3.0,
                liquidity="$5,000,000,000", 
                risk_score=0.85,
                source="fallback",
                last_updated=datetime.utcnow().isoformat()
            )
        ]
        
        return IndexValue(
            value=1.0325,  # ~3.25% weighted average
            timestamp=datetime.utcnow().isoformat(),
            constituents=fallback_constituents,
            methodology="Fallback Index",
            metadata={
                "calculation_timestamp": datetime.utcnow().isoformat(),
                "constituent_count": 3,
                "methodology": "Emergency Fallback",
                "note": "Using fallback values due to data unavailability"
            }
        )
    
    async def calculate_index(self) -> IndexValue:
        """Calculate the current StableYield Index using RAY methodology"""
        try:
            # Check cache first
            cache_key = "current_index"
            if cache_key in self.cache and datetime.utcnow() < self.cache_expiry[cache_key]:
                logger.debug("Returning cached index value")
                return self.cache[cache_key]
            
            logger.info("Calculating StableYield Index using enhanced RAY methodology")
            
            # Get current yield data through the aggregator (already filtered and sanitized)
            yields_data = await self.yield_aggregator.get_all_yields()
            
            if not yields_data:
                logger.warning("No yield data available for index calculation")
                return self._get_fallback_index()
            
            logger.info(f"Processing {len(yields_data)} yield sources for SYI calculation")
            
            # Use the new SYI Compositor with RAY calculations
            syi_composition = self.syi_compositor.compose_syi(yields_data)
            
            # Convert to IndexValue format for backward compatibility
            constituents = []
            for constituent in syi_composition.constituents:
                # Create StablecoinConstituent objects
                stablecoin_constituent = StablecoinConstituent(
                    symbol=constituent.stablecoin,
                    weight=constituent.weight,
                    yield_value=constituent.ray,  # Use RAY instead of raw APY
                    liquidity=f"${constituent.tvl_usd:,.0f}",
                    risk_score=1 - constituent.risk_penalty,  # Convert penalty to score
                    source=constituent.protocol,
                    last_updated=datetime.utcnow().isoformat()
                )
                constituents.append(stablecoin_constituent)
            
            # Create enhanced metadata
            metadata = {
                "methodology_version": syi_composition.methodology_version,
                "calculation_method": "risk_adjusted_yield_weighted",
                "calculation_timestamp": syi_composition.calculation_timestamp,
                "constituent_count": syi_composition.constituent_count,
                "total_weight": syi_composition.total_weight,
                "quality_metrics": syi_composition.quality_metrics,
                "risk_adjustment_applied": True,
                "data_sources": {
                    "defi_sources": len([c for c in syi_composition.constituents if "DeFi" in str(c.metadata.get('original_yield_data', {}).get('sourceType', ''))]),
                    "cefi_sources": len([c for c in syi_composition.constituents if "CeFi" in str(c.metadata.get('original_yield_data', {}).get('sourceType', ''))]),
                    "total_sources": len(syi_composition.constituents)
                },
                "ray_statistics": {
                    "average_ray": syi_composition.breakdown.get("weighted_average_ray", 0),
                    "average_risk_penalty": syi_composition.breakdown.get("total_risk_penalty", 0),
                    "average_confidence": syi_composition.quality_metrics.get("avg_confidence", 0)
                },
                "diversification": {
                    "protocol_count": syi_composition.quality_metrics.get("protocol_diversity", 0),
                    "stablecoin_count": syi_composition.quality_metrics.get("stablecoin_diversity", 0),
                    "max_constituent_weight": syi_composition.quality_metrics.get("max_constituent_weight", 0)
                }
            }
            
            # Create final IndexValue
            index_value = IndexValue(
                value=syi_composition.index_value,
                timestamp=datetime.utcnow().isoformat(),
                constituents=constituents,
                methodology="Risk-Adjusted Yield Weighted",
                metadata=metadata
            )
            
            # Cache the result
            self.cache[cache_key] = index_value
            self.cache_expiry[cache_key] = datetime.utcnow() + self.cache_duration
            
            logger.info(f"SYI calculated: {syi_composition.index_value:.4f} with {len(constituents)} constituents")
            logger.info(f"Quality metrics: Overall={syi_composition.quality_metrics.get('overall_quality', 0):.2f}, "
                       f"Avg confidence={syi_composition.quality_metrics.get('avg_confidence', 0):.2f}")
            
            return index_value
            
        except Exception as e:
            logger.error(f"Error calculating StableYield Index: {str(e)}")
            return self._get_fallback_index()
    
    async def _calculate_constituent_data(self, coin: Dict) -> Optional[StablecoinConstituent]:
        """Calculate all metrics for a single stablecoin constituent"""
        symbol = coin["symbol"]
        
        try:
            # Get market data
            market_data = await self._get_market_data(symbol)
            if not market_data:
                return None
            
            # Get yield data
            yield_data = await self._get_yield_data(symbol)
            if not yield_data:
                logger.warning(f"No yield data for {symbol}, using fallback")
                yield_data = {"apy": 3.0}  # Conservative fallback
            
            # Calculate risk scores
            peg_score = await self._calculate_peg_score(symbol, market_data)
            liquidity_score = await self._calculate_liquidity_score(symbol, market_data)
            counterparty_score = await self._calculate_counterparty_score(symbol)
            
            # Calculate Risk-Adjusted Yield (RAY)
            raw_apy = yield_data.get("apy", 3.0)
            ray = self._calculate_ray(raw_apy, peg_score, liquidity_score, counterparty_score)
            
            return StablecoinConstituent(
                symbol=symbol,
                name=coin["name"],
                market_cap=market_data.get("market_cap", 0),
                weight=0,  # Will be calculated later
                raw_apy=raw_apy,
                peg_score=peg_score,
                liquidity_score=liquidity_score,
                counterparty_score=counterparty_score,
                ray=ray,
                last_updated=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Failed to calculate constituent data for {symbol}: {e}")
            return None
    
    async def _get_market_data(self, symbol: str) -> Optional[Dict]:
        """Get market cap and price data"""
        try:
            # Try CryptoCompare first
            cc_data = await self.crypto_compare.get_price_data(symbol)
            if cc_data:
                return {
                    "price": cc_data.get("USD", 1.0),
                    "market_cap": cc_data.get("USD", 1.0) * 1000000000,  # Rough estimate
                    "volume_24h": cc_data.get("USD", 0) * 100000000
                }
        except Exception as e:
            logger.warning(f"CryptoCompare market data failed for {symbol}: {e}")
        
        # Fallback market caps (in USD, rough estimates for demo)
        fallback_market_caps = {
            "USDT": 83000000000,  # ~83B
            "USDC": 25000000000,  # ~25B  
            "DAI": 5000000000,    # ~5B
            "TUSD": 500000000,    # ~500M
            "FRAX": 800000000,    # ~800M
            "USDP": 200000000     # ~200M
        }
        
        return {
            "price": 1.0,
            "market_cap": fallback_market_caps.get(symbol, 1000000000),
            "volume_24h": 100000000
        }
    
    async def _get_yield_data(self, symbol: str) -> Optional[Dict]:
        """Get yield data from available sources"""
        try:
            # Try Binance first (even demo data)
            binance_yield = await self.binance.get_earn_products(symbol)
            if binance_yield:
                return {"apy": binance_yield.get("apy", 3.0)}
        except Exception as e:
            logger.warning(f"Binance yield data failed for {symbol}: {e}")
        
        try:
            # Try DefiLlama
            defi_yield = await self.defi_llama.get_yields_for_token(symbol)
            if defi_yield:
                return {"apy": defi_yield}
        except Exception as e:
            logger.warning(f"DefiLlama yield data failed for {symbol}: {e}")
        
        # Fallback yields (demo values)
        fallback_yields = {
            "USDT": 4.2,
            "USDC": 3.8,
            "DAI": 3.5,
            "TUSD": 3.1,
            "FRAX": 2.9,
            "USDP": 3.3
        }
        
        return {"apy": fallback_yields.get(symbol, 3.0)}
    
    async def _calculate_peg_score(self, symbol: str, market_data: Dict) -> float:
        """Calculate peg stability score (0-1, where 1 is perfect peg)"""
        try:
            price = market_data.get("price", 1.0)
            deviation = abs(price - 1.0)
            
            # Score calculation: exponential decay from 1.0
            # Perfect peg = 1.0, 1% deviation = ~0.9, 5% deviation = ~0.6
            score = math.exp(-deviation * 20)
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            logger.warning(f"Peg score calculation failed for {symbol}: {e}")
            return 0.95  # Conservative default
    
    async def _calculate_liquidity_score(self, symbol: str, market_data: Dict) -> float:
        """Calculate liquidity score (0-1, where 1 is perfect liquidity)"""
        try:
            volume_24h = market_data.get("volume_24h", 0)
            market_cap = market_data.get("market_cap", 1)
            
            # Liquidity ratio: daily volume / market cap
            if market_cap > 0:
                liquidity_ratio = volume_24h / market_cap
                # Normalize: good liquidity is 5%+ daily turnover
                score = min(1.0, liquidity_ratio / 0.05)
                return max(0.1, score)  # Minimum 0.1
            
        except Exception as e:
            logger.warning(f"Liquidity score calculation failed for {symbol}: {e}")
        
        # Fallback scores based on known liquidity
        liquidity_scores = {
            "USDT": 0.95,
            "USDC": 0.92,
            "DAI": 0.85,
            "TUSD": 0.70,
            "FRAX": 0.75,
            "USDP": 0.65
        }
        
        return liquidity_scores.get(symbol, 0.70)
    
    async def _calculate_counterparty_score(self, symbol: str) -> float:
        """Calculate counterparty risk score (0-1, where 1 is lowest risk)"""
        # Simplified risk assessment based on stablecoin type and history
        risk_scores = {
            "USDT": 0.75,  # Centralized, some transparency concerns
            "USDC": 0.90,  # Centralized, regulated, transparent
            "DAI": 0.85,   # Decentralized, over-collateralized
            "TUSD": 0.80,  # Centralized, regulated
            "FRAX": 0.75,  # Algorithmic/hybrid, newer
            "USDP": 0.85   # Centralized, regulated
        }
        
        return risk_scores.get(symbol, 0.70)
    
    def _calculate_ray(self, apy: float, peg_score: float, liquidity_score: float, counterparty_score: float) -> float:
        """
        Calculate Risk-Adjusted Yield (RAY)
        RAY = APY × f(peg_stability, liquidity, counterparty_risk)
        
        Current implementation: RAY = APY × (peg_score × liquidity_score × counterparty_score)^0.5
        The square root dampens the penalty for risk factors
        """
        try:
            risk_factor = (peg_score * liquidity_score * counterparty_score) ** 0.5
            ray = apy * risk_factor
            return round(ray, 4)
        except Exception as e:
            logger.error(f"RAY calculation failed: {e}")
            return apy * 0.7  # Conservative fallback

# TODO: PRODUCTION UPGRADES NEEDED
# 1. Replace demo/fallback data with real-time API feeds
# 2. Implement WebSocket connections for live price/volume data
# 3. Add more sophisticated risk scoring models
# 4. Implement data validation and quality checks
# 5. Add circuit breakers for API failures
# 6. Store calculation logs for debugging and compliance