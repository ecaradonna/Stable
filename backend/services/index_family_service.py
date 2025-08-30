"""
StableYield Index Family Service
Implements calculation logic for SY100, SY-CeFi, SY-DeFi, SY-RPI
Enhanced with real Coinbase API integration for CeFi data
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
import asyncio
from motor.motor_asyncio import AsyncIOMotorDatabase

from models.index_family import (
    IndexCode, IndexMode, IndexValue, Constituent, IndexWeight, 
    IndexConstituents, TBillData, WeightingMethod, ConstituentType,
    IndexFactsheet, IndexFamilyOverview
)
from services.coinbase_service import get_coinbase_service

logger = logging.getLogger(__name__)

class IndexFamilyService:
    """Service for calculating and managing the StableYield Index Family"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.kappa_normal = 2.0  # RAY penalty coefficient (normal mode)
        self.kappa_high_vol = 4.0  # RAY penalty coefficient (high volatility mode)
        
    async def calculate_daily_indices(self, date: datetime) -> Dict[IndexCode, IndexValue]:
        """Calculate all indices for a given date"""
        try:
            logger.info(f"Calculating index family for {date.strftime('%Y-%m-%d')}")
            
            # Load base data
            constituents = await self._load_constituents_data(date)
            tbill_rate = await self._load_tbill_rate(date)
            market_mode = await self._determine_market_mode(date)
            
            # Calculate RAY for all constituents
            constituents = await self._calculate_ray_scores(constituents, market_mode)
            
            results = {}
            
            # Calculate each index
            results[IndexCode.SYRPI] = await self._calculate_sy_rpi(date, constituents, tbill_rate, market_mode)
            results[IndexCode.SYCEFI] = await self._calculate_sy_cefi(date, constituents, market_mode)
            results[IndexCode.SYDEFI] = await self._calculate_sy_defi(date, constituents, market_mode)
            results[IndexCode.SYC] = await self._calculate_syc(date, constituents, market_mode)
            
            # Store results in database
            await self._store_index_values(results)
            
            logger.info(f"Successfully calculated {len(results)} indices for {date.strftime('%Y-%m-%d')}")
            return results
            
        except Exception as e:
            logger.error(f"Error calculating index family for {date}: {str(e)}")
            raise

    async def _load_constituents_data(self, date: datetime) -> List[Constituent]:
        """Load constituent data from multiple sources"""
        constituents = []
        
        # Load stablecoins
        stablecoins = await self._load_stablecoin_data(date)
        constituents.extend(stablecoins)
        
        # Load CeFi strategies
        cefi_strategies = await self._load_cefi_strategies(date)
        constituents.extend(cefi_strategies)
        
        # Load DeFi protocols
        defi_protocols = await self._load_defi_protocols(date)
        constituents.extend(defi_protocols)
        
        logger.info(f"Loaded {len(constituents)} constituents for {date.strftime('%Y-%m-%d')}")
        return constituents
        
    async def _load_stablecoin_data(self, date: datetime) -> List[Constituent]:
        """Load stablecoin yield data"""
        # Mock implementation - in production would query yield aggregator
        stablecoins = [
            Constituent(
                id="USDT",
                symbol="USDT",
                name="Tether USD",
                type=ConstituentType.STABLECOIN,
                current_apy=0.0682,  # 6.82%
                apy_effective=0.0682,
                tvl_usd=83_200_000_000,
                market_cap=83_200_000_000,
                platform="Multiple",
                operational_days=2800
            ),
            Constituent(
                id="USDC", 
                symbol="USDC",
                name="USD Coin",
                type=ConstituentType.STABLECOIN,
                current_apy=0.0521,  # 5.21%
                apy_effective=0.0521,
                tvl_usd=33_400_000_000,
                market_cap=33_400_000_000,
                platform="Multiple", 
                operational_days=2100
            ),
            Constituent(
                id="DAI",
                symbol="DAI", 
                name="Dai Stablecoin",
                type=ConstituentType.STABLECOIN,
                current_apy=0.0734,  # 7.34%
                apy_effective=0.0734,
                tvl_usd=5_300_000_000,
                market_cap=5_300_000_000,
                platform="MakerDAO",
                operational_days=2200
            )
        ]
        
        return stablecoins
        
    async def _load_cefi_strategies(self, date: datetime) -> List[Constituent]:
        """Load CeFi platform strategies with real Coinbase integration"""
        try:
            # Get real Coinbase data
            coinbase_service = get_coinbase_service()
            coinbase_data = await coinbase_service.calculate_cefi_index_contribution()
            
            strategies = []
            
            # Process real Coinbase constituents
            for constituent in coinbase_data.get('constituents', []):
                try:
                    constituent_id = f"coinbase_{constituent['currency'].lower()}"
                    
                    # Skip very small balances
                    if constituent['value_usd'] < 100:  # Minimum $100 USD value
                        continue
                    
                    strategy = Constituent(
                        id=constituent_id,
                        symbol=constituent['currency'],
                        name=f"Coinbase {constituent['currency']} {constituent['account_type'].title()}",
                        type=ConstituentType.CEFI_STRATEGY,
                        current_apy=constituent['annual_yield_rate'] / 100,  # Convert percentage to decimal
                        apy_effective=constituent['annual_yield_rate'] / 100,
                        capacity_usd=constituent['value_usd'] * 10,  # Assume 10x capacity for index calculation
                        platform="Coinbase",
                        jurisdiction="US",
                        audit_count=5,  # Coinbase is well-audited
                        operational_days=2500  # Coinbase has been operational for years
                    )
                    strategies.append(strategy)
                    
                except Exception as e:
                    logger.warning(f"Error processing Coinbase constituent {constituent}: {e}")
                    continue
            
            # Add some additional CeFi platforms for diversity if we have real data
            if strategies:
                additional_strategies = [
                    Constituent(
                        id="gemini_usd",
                        symbol="USD", 
                        name="Gemini Dollar Earn",
                        type=ConstituentType.CEFI_STRATEGY,
                        current_apy=0.0385,  # 3.85%
                        apy_effective=0.0385,
                        capacity_usd=180_000_000,
                        platform="Gemini",
                        jurisdiction="US",
                        audit_count=4,
                        operational_days=1700
                    ),
                    Constituent(
                        id="kraken_usdc",
                        symbol="USDC",
                        name="Kraken USDC Staking",
                        type=ConstituentType.CEFI_STRATEGY,
                        current_apy=0.041,  # 4.1%
                        apy_effective=0.041,
                        capacity_usd=150_000_000,
                        platform="Kraken",
                        jurisdiction="US",
                        audit_count=3,
                        operational_days=2200
                    )
                ]
                strategies.extend(additional_strategies)
                
            # Fallback to enhanced mock data if no real data
            if not strategies:
                logger.info("No Coinbase data available, using enhanced mock CeFi strategies")
                strategies = [
                    Constituent(
                        id="coinbase_usdc_mock",
                        symbol="USDC",
                        name="Coinbase USDC Rewards (Demo)",
                        type=ConstituentType.CEFI_STRATEGY,
                        current_apy=0.042,  # 4.2%
                        apy_effective=0.042,
                        capacity_usd=500_000_000,
                        platform="Coinbase",
                        jurisdiction="US",
                        audit_count=5,
                        operational_days=2500
                    ),
                    Constituent(
                        id="coinbase_eth_mock",
                        symbol="ETH", 
                        name="Coinbase ETH Staking (Demo)",
                        type=ConstituentType.CEFI_STRATEGY,
                        current_apy=0.038,  # 3.8%
                        apy_effective=0.038,
                        capacity_usd=300_000_000,
                        platform="Coinbase",
                        jurisdiction="US",
                        audit_count=5,
                        operational_days=2500
                    ),
                    Constituent(
                        id="gemini_gusd",
                        symbol="GUSD", 
                        name="Gemini Dollar Earn",
                        type=ConstituentType.CEFI_STRATEGY,
                        current_apy=0.0385,  # 3.85%
                        apy_effective=0.0385,
                        capacity_usd=200_000_000,
                        platform="Gemini",
                        jurisdiction="US",
                        audit_count=4,
                        operational_days=1600
                    )
                ]
            
            logger.info(f"Loaded {len(strategies)} CeFi strategies (Coinbase integration: {'active' if coinbase_data.get('constituents') else 'mock'})")
            return strategies
            
        except Exception as e:
            logger.error(f"Error loading CeFi strategies: {e}")
            # Fallback to basic mock data
            return [
                Constituent(
                    id="coinbase_usdc_fallback",
                    symbol="USDC",
                    name="Coinbase USDC Rewards (Fallback)",
                    type=ConstituentType.CEFI_STRATEGY,
                    current_apy=0.042,
                    apy_effective=0.042,
                    capacity_usd=500_000_000,
                    platform="Coinbase",
                    jurisdiction="US",
                    audit_count=5,
                    operational_days=2500
                )
            ]
        
    async def _load_defi_protocols(self, date: datetime) -> List[Constituent]:
        """Load DeFi protocol data"""
        protocols = [
            Constituent(
                id="aave_v3_usdc",
                symbol="USDC",
                name="Aave v3 USDC Supply",
                type=ConstituentType.DEFI_STRATEGY,
                current_apy=0.0892,  # 8.92%
                apy_effective=0.0723,  # Excluding token incentives
                tvl_usd=1_200_000_000,
                platform="Aave v3",
                chain="ethereum",
                audit_count=8,
                operational_days=900,
                maturity_factor=1.15
            ),
            Constituent(
                id="compound_v3_usdt",
                symbol="USDT",
                name="Compound v3 USDT Supply", 
                type=ConstituentType.DEFI_STRATEGY,
                current_apy=0.0657,  # 6.57%
                apy_effective=0.0657,
                tvl_usd=800_000_000,
                platform="Compound v3",
                chain="ethereum", 
                audit_count=6,
                operational_days=1200,
                maturity_factor=1.10
            )
        ]
        
        return protocols

    async def _load_tbill_rate(self, date: datetime) -> float:
        """Load 3-month Treasury Bill rate"""
        # Mock implementation - in production would query FRED API or cache
        try:
            # Check database cache first
            cached = await self.db.treasury_rates.find_one({
                "date": {"$gte": date.replace(hour=0, minute=0, second=0, microsecond=0)},
                "maturity": "3M"
            }, sort=[("date", -1)])
            
            if cached:
                return cached["rate"]
            
            # Mock rate - in production would fetch from FRED
            return 0.0525  # 5.25% (current 3M Treasury rate)
            
        except Exception as e:
            logger.warning(f"Error loading T-Bill rate: {e}, using fallback")
            return 0.0525

    async def _determine_market_mode(self, date: datetime) -> IndexMode:
        """Determine market mode (Normal, Bear, High-Vol)"""
        try:
            # Check DeFi TVL for Bear mode
            total_defi_tvl = await self._get_total_defi_tvl(date)
            historical_tvl = await self._get_historical_defi_tvl(date, days=365)
            
            if historical_tvl and total_defi_tvl:
                tvl_percentile = np.percentile(historical_tvl, 20)
                if total_defi_tvl < tvl_percentile:
                    return IndexMode.BEAR
                    
            # Check volatility for High-Vol mode
            index_returns = await self._get_recent_index_returns(date, days=30)
            if index_returns:
                current_vol = np.std(index_returns) * np.sqrt(365)  # Annualized
                rolling_vol = await self._get_rolling_volatility(date, days=90)
                
                if rolling_vol and current_vol > 2 * rolling_vol:
                    return IndexMode.HIGH_VOL
                    
            return IndexMode.NORMAL
            
        except Exception as e:
            logger.warning(f"Error determining market mode: {e}, using Normal")
            return IndexMode.NORMAL

    async def _calculate_ray_scores(self, constituents: List[Constituent], mode: IndexMode) -> List[Constituent]:
        """Calculate Risk-Adjusted Yield (RAY) for all constituents"""
        kappa = self.kappa_high_vol if mode == IndexMode.HIGH_VOL else self.kappa_normal
        
        for constituent in constituents:
            # Calculate risk scores
            peg_score = await self._calculate_peg_score(constituent)
            liquidity_score = await self._calculate_liquidity_score(constituent)
            counterparty_score = await self._calculate_counterparty_score(constituent)
            
            # S_worst = minimum of all risk scores
            s_worst = min(peg_score, liquidity_score, counterparty_score)
            
            # Calculate RAY = APYeff * exp(-κ * (1 - S_worst))
            apy_eff = constituent.apy_effective or constituent.current_apy or 0
            ray = apy_eff * np.exp(-kappa * (1 - s_worst))
            
            # Update constituent
            constituent.peg_score = peg_score
            constituent.liquidity_score = liquidity_score  
            constituent.counterparty_score = counterparty_score
            constituent.s_worst = s_worst
            constituent.ray = ray
            
        return constituents

    async def _calculate_peg_score(self, constituent: Constituent) -> float:
        """Calculate peg stability score (0-1)"""
        try:
            # Mock implementation - in production would analyze peg deviation
            if constituent.type == ConstituentType.STABLECOIN:
                # Stablecoins generally have good peg stability
                base_score = 0.95
                # Add some realistic variation
                symbol_penalty = {
                    "USDT": 0.02,  # Slightly lower due to historical depegs
                    "USDC": 0.01,  # Very stable
                    "DAI": 0.03,   # Slightly more volatile
                }.get(constituent.symbol, 0.02)
                return max(0.8, base_score - symbol_penalty)
            else:
                # CeFi/DeFi strategies inherit underlying stablecoin peg
                return 0.92
                
        except Exception:
            return 0.85  # Conservative fallback

    async def _calculate_liquidity_score(self, constituent: Constituent) -> float:
        """Calculate liquidity depth score (0-1)"""
        try:
            # Mock implementation based on TVL/market cap
            if constituent.tvl_usd:
                # Higher TVL = better liquidity
                tvl_billions = constituent.tvl_usd / 1_000_000_000
                score = min(0.99, 0.7 + 0.1 * np.log(1 + tvl_billions))
                return max(0.5, score)
            elif constituent.capacity_usd:
                # CeFi capacity-based scoring
                capacity_millions = constituent.capacity_usd / 1_000_000
                score = min(0.95, 0.6 + 0.15 * np.log(1 + capacity_millions))
                return max(0.4, score)
            else:
                return 0.75  # Fallback
                
        except Exception:
            return 0.70

    async def _calculate_counterparty_score(self, constituent: Constituent) -> float:
        """Calculate counterparty risk score (0-1)"""
        try:
            base_score = 0.8
            
            # Audit bonus
            if constituent.audit_count:
                audit_bonus = min(0.15, constituent.audit_count * 0.025)
                base_score += audit_bonus
                
            # Maturity bonus
            if constituent.operational_days and constituent.operational_days > 365:
                maturity_bonus = min(0.1, (constituent.operational_days - 365) / 3650 * 0.1)
                base_score += maturity_bonus
                
            # Platform/jurisdiction bonus
            if constituent.jurisdiction == "US":
                base_score += 0.05
                
            return min(0.99, base_score)
            
        except Exception:
            return 0.80

    async def _calculate_sy_rpi(self, date: datetime, constituents: List[Constituent], 
                               tbill_rate: float, mode: IndexMode) -> IndexValue:
        """Calculate SY-RPI (Risk Premium Index)"""
        try:
            # Get core stablecoin universe (USDT, USDC, DAI, etc.)
            core_stablecoins = [c for c in constituents if c.type == ConstituentType.STABLECOIN]
            
            if not core_stablecoins:
                raise ValueError("No core stablecoins available for SY-RPI calculation")
                
            # Calculate average RAY
            ray_values = [c.ray for c in core_stablecoins if c.ray is not None]
            if not ray_values:
                raise ValueError("No valid RAY values for SY-RPI calculation")
                
            avg_ray = np.mean(ray_values)
            
            # Risk Premium = Average RAY - T-Bill rate
            rpi_value = avg_ray - tbill_rate
            
            # Apply mode-specific adjustments
            if mode == IndexMode.BEAR:
                # Apply EWMA smoothing in bear markets
                previous_rpi = await self._get_previous_index_value(IndexCode.SYRPI, date)
                if previous_rpi:
                    rpi_value = 0.85 * previous_rpi + 0.15 * rpi_value
                    
            return IndexValue(
                date=date,
                index_code=IndexCode.SYRPI,
                value=rpi_value,
                mode=mode,
                confidence=1.0,
                constituent_count=len(core_stablecoins),
                avg_yield=avg_ray,
                notes=f"T-Bill: {tbill_rate:.4f}, Avg RAY: {avg_ray:.4f}"
            )
            
        except Exception as e:
            logger.error(f"Error calculating SY-RPI: {e}")
            raise

    async def _calculate_sy_cefi(self, date: datetime, constituents: List[Constituent], 
                                 mode: IndexMode) -> IndexValue:
        """Calculate SY-CeFi (Centralized Finance Index)"""
        try:
            # Filter CeFi strategies
            cefi_strategies = [c for c in constituents if c.type == ConstituentType.CEFI_STRATEGY]
            
            if not cefi_strategies:
                logger.warning("No CeFi strategies available")
                return IndexValue(
                    date=date,
                    index_code=IndexCode.SYCEFI,
                    value=0.0,
                    mode=mode,
                    confidence=0.0,
                    constituent_count=0
                )
                
            # Capacity-weighted calculation
            total_capacity = sum(c.capacity_usd or 0 for c in cefi_strategies)
            if total_capacity == 0:
                raise ValueError("No valid capacity data for CeFi strategies")
                
            weighted_ray = 0
            for strategy in cefi_strategies:
                if strategy.capacity_usd and strategy.ray:
                    weight = strategy.capacity_usd / total_capacity
                    weighted_ray += weight * strategy.ray
                    
            # Calculate HHI (concentration)
            weights = [c.capacity_usd / total_capacity for c in cefi_strategies if c.capacity_usd]
            hhi = sum(w**2 for w in weights) * 10000  # Scale to 0-10000
            
            return IndexValue(
                date=date,
                index_code=IndexCode.SYCEFI,
                value=weighted_ray,
                mode=mode,
                confidence=1.0,
                hhi=hhi,
                constituent_count=len(cefi_strategies),
                total_tvl=total_capacity,
                avg_yield=np.mean([c.ray for c in cefi_strategies if c.ray])
            )
            
        except Exception as e:
            logger.error(f"Error calculating SY-CeFi: {e}")
            raise

    async def _calculate_sy_defi(self, date: datetime, constituents: List[Constituent], 
                                 mode: IndexMode) -> IndexValue:
        """Calculate SY-DeFi (Decentralized Finance Index)"""
        try:
            # Filter DeFi strategies with eligibility criteria
            defi_strategies = []
            for c in constituents:
                if (c.type == ConstituentType.DEFI_STRATEGY and
                    c.tvl_usd and c.tvl_usd >= 50_000_000 and  # Min $50M TVL
                    c.audit_count and c.audit_count >= 2 and   # Min 2 audits
                    c.operational_days and c.operational_days >= 365):  # Min 12 months
                    defi_strategies.append(c)
                    
            if not defi_strategies:
                logger.warning("No eligible DeFi strategies")
                return IndexValue(
                    date=date,
                    index_code=IndexCode.SYDEFI,
                    value=0.0,
                    mode=mode,
                    confidence=0.0,
                    constituent_count=0
                )
                
            # TVL * Maturity weighted calculation
            total_weighted_tvl = sum((c.tvl_usd or 0) * (c.maturity_factor or 1) for c in defi_strategies)
            if total_weighted_tvl == 0:
                raise ValueError("No valid TVL data for DeFi strategies")
                
            weighted_ray = 0
            for strategy in defi_strategies:
                if strategy.tvl_usd and strategy.ray and strategy.maturity_factor:
                    weight = (strategy.tvl_usd * strategy.maturity_factor) / total_weighted_tvl
                    weighted_ray += weight * strategy.ray
                    
            # Calculate metrics
            total_tvl = sum(c.tvl_usd or 0 for c in defi_strategies)
            weights = [(c.tvl_usd * c.maturity_factor) / total_weighted_tvl 
                      for c in defi_strategies if c.tvl_usd and c.maturity_factor]
            hhi = sum(w**2 for w in weights) * 10000
            
            return IndexValue(
                date=date,
                index_code=IndexCode.SYDEFI,
                value=weighted_ray,
                mode=mode,
                confidence=1.0,
                hhi=hhi,
                constituent_count=len(defi_strategies),
                total_tvl=total_tvl,
                avg_yield=np.mean([c.ray for c in defi_strategies if c.ray])
            )
            
        except Exception as e:
            logger.error(f"Error calculating SY-DeFi: {e}")
            raise

    async def _calculate_syc(self, date: datetime, constituents: List[Constituent], 
                            mode: IndexMode) -> IndexValue:
        """Calculate SYC (StableYield Composite Index)"""
        try:
            # Filter eligible strategies (all types with sufficient data)
            eligible_strategies = []
            for c in constituents:
                if (c.ray is not None and
                    ((c.tvl_usd and c.tvl_usd >= 10_000_000) or  # Min $10M TVL
                     (c.capacity_usd and c.capacity_usd >= 10_000_000)) and  # Or capacity
                    c.operational_days and c.operational_days >= 365):  # Min 12 months
                    eligible_strategies.append(c)
                    
            if len(eligible_strategies) < 10:
                logger.warning(f"Insufficient strategies for SYC: {len(eligible_strategies)}")
                return IndexValue(
                    date=date,
                    index_code=IndexCode.SYC,
                    value=0.0,
                    mode=mode,
                    confidence=0.0,
                    constituent_count=len(eligible_strategies)
                )
                
            # Sort by RAY and take top 100 (or available)
            top_strategies = sorted(eligible_strategies, key=lambda x: x.ray, reverse=True)[:100]
            
            # Calculate volatility for inverse-vol weighting (mock implementation)
            # In production, would use historical RAY volatility
            weights = []
            for strategy in top_strategies:
                # Mock volatility based on strategy type and characteristics
                if strategy.type == ConstituentType.CEFI_STRATEGY:
                    vol = 0.05  # Lower vol for CeFi
                elif strategy.type == ConstituentType.STABLECOIN:
                    vol = 0.08  # Medium vol
                else:  # DeFi
                    vol = 0.12  # Higher vol for DeFi
                    
                # Add some variation
                vol *= (0.8 + 0.4 * np.random.random())
                inverse_vol_weight = 1 / vol
                weights.append(inverse_vol_weight)
                
            # Normalize weights and apply 2% cap
            total_weight = sum(weights)
            normalized_weights = [w / total_weight for w in weights]
            
            # Apply 2% cap per constituent
            capped_weights = [min(w, 0.02) for w in normalized_weights]
            # Renormalize after capping
            total_capped = sum(capped_weights)
            final_weights = [w / total_capped for w in capped_weights]
            
            # Calculate weighted index value
            syc_value = sum(w * s.ray for w, s in zip(final_weights, top_strategies))
            
            # Calculate HHI
            hhi = sum(w**2 for w in final_weights) * 10000
            
            return IndexValue(
                date=date,
                index_code=IndexCode.SYC,
                value=syc_value,
                mode=mode,
                confidence=1.0,
                hhi=hhi,
                constituent_count=len(top_strategies),
                total_tvl=sum(c.tvl_usd or c.capacity_usd or 0 for c in top_strategies),
                avg_yield=np.mean([c.ray for c in top_strategies])
            )
            
        except Exception as e:
            logger.error(f"Error calculating SY100: {e}")
            raise

    # Helper methods
    async def _get_total_defi_tvl(self, date: datetime) -> Optional[float]:
        """Get total DeFi TVL for mode determination"""
        # Mock implementation
        return 50_000_000_000  # $50B

    async def _get_historical_defi_tvl(self, date: datetime, days: int) -> Optional[List[float]]:
        """Get historical DeFi TVL for percentile calculation"""
        # Mock implementation
        base_tvl = 50_000_000_000
        return [base_tvl * (0.8 + 0.4 * np.random.random()) for _ in range(days)]

    async def _get_recent_index_returns(self, date: datetime, days: int) -> Optional[List[float]]:
        """Get recent index returns for volatility calculation"""
        # Mock implementation
        return [0.001 * np.random.randn() for _ in range(days)]

    async def _get_rolling_volatility(self, date: datetime, days: int) -> Optional[float]:
        """Get rolling volatility for mode determination"""
        # Mock implementation
        return 0.15  # 15% annualized

    async def _get_previous_index_value(self, index_code: IndexCode, date: datetime) -> Optional[float]:
        """Get previous index value for smoothing"""
        try:
            previous_date = date - timedelta(days=1)
            result = await self.db.index_values.find_one({
                "index_code": index_code.value,
                "date": {"$lte": previous_date}
            }, sort=[("date", -1)])
            
            return result["value"] if result else None
        except Exception:
            return None

    async def _store_index_values(self, results: Dict[IndexCode, IndexValue]):
        """Store calculated index values in database"""
        try:
            for index_code, index_value in results.items():
                await self.db.index_values.replace_one(
                    {"index_code": index_code.value, "date": index_value.date},
                    index_value.dict(),
                    upsert=True
                )
            logger.info(f"Stored {len(results)} index values")
        except Exception as e:
            logger.error(f"Error storing index values: {e}")
            raise

    async def get_index_value(self, index_code: IndexCode, date: datetime) -> Optional[IndexValue]:
        """Retrieve index value for a specific date"""
        try:
            result = await self.db.index_values.find_one({
                "index_code": index_code.value,
                "date": {"$lte": date}
            }, sort=[("date", -1)])
            
            return IndexValue(**result) if result else None
        except Exception as e:
            logger.error(f"Error retrieving index value: {e}")
            return None

    async def get_index_family_overview(self, date: datetime) -> IndexFamilyOverview:
        """Get overview of all indices for a date"""
        try:
            indices = {}
            for index_code in IndexCode:
                value = await self.get_index_value(index_code, date)
                if value:
                    indices[index_code] = value
                    
            return IndexFamilyOverview(
                date=date,
                indices=indices,
                total_constituents=sum(v.constituent_count for v in indices.values()),
                family_aum=sum(v.total_tvl or 0 for v in indices.values())
            )
        except Exception as e:
            logger.error(f"Error getting index family overview: {e}")
            raise