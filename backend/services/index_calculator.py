import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import math

from ..models.index_models import IndexValue, StablecoinConstituent
from .crypto_compare_service import CryptoCompareService
from .defillama_service import DefiLlamaService
from .binance_service import BinanceService

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
        self.defillama = DefiLlamaService()
        self.binance = BinanceService()
        
        # Core stablecoins for Phase 1
        self.constituents = [
            {"symbol": "USDT", "name": "Tether"},
            {"symbol": "USDC", "name": "USD Coin"},
            {"symbol": "DAI", "name": "Dai"},
            {"symbol": "TUSD", "name": "TrueUSD"},
            {"symbol": "FRAX", "name": "Frax"},
            {"symbol": "USDP", "name": "Pax Dollar"}
        ]
    
    async def calculate_index(self) -> IndexValue:
        """Calculate the current StableYield Index value"""
        try:
            logger.info("Starting StableYield Index calculation")
            
            # Gather data for all constituents
            constituents_data = []
            total_market_cap = 0
            
            for coin in self.constituents:
                try:
                    constituent = await self._calculate_constituent_data(coin)
                    if constituent:
                        constituents_data.append(constituent)
                        total_market_cap += constituent.market_cap
                except Exception as e:
                    logger.warning(f"Failed to calculate data for {coin['symbol']}: {e}")
                    continue
            
            if not constituents_data:
                raise Exception("No valid constituent data available")
            
            # Calculate weights and final index value
            index_value = 0
            for constituent in constituents_data:
                if total_market_cap > 0:
                    constituent.weight = constituent.market_cap / total_market_cap
                    index_value += constituent.weight * constituent.ray
                else:
                    # Equal weight fallback
                    constituent.weight = 1.0 / len(constituents_data)
                    index_value += constituent.weight * constituent.ray
            
            # Create index record
            result = IndexValue(
                timestamp=datetime.utcnow(),
                index_id="SYI",
                value=round(index_value, 4),
                constituents=constituents_data,
                metadata={
                    "total_market_cap": total_market_cap,
                    "constituent_count": len(constituents_data),
                    "calculation_method": "market_cap_weighted_ray"
                }
            )
            
            logger.info(f"StableYield Index calculated: {result.value}%")
            return result
            
        except Exception as e:
            logger.error(f"Index calculation failed: {e}")
            raise
    
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
            defi_yield = await self.defillama.get_yields_for_token(symbol)
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