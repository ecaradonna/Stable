"""
Peg computation and analysis logic
"""

import math
import time
import statistics
from typing import Dict, List, Optional, Tuple

from .models import PricePoint, PegReport, PegStatus, PegCheckPayload
from .config import DEPEG_THRESHOLD_BPS, WARNING_THRESHOLD_BPS

def merge_cefi_refs(coingecko_prices: Dict[str, float], 
                   cryptocompare_prices: Dict[str, float]) -> Dict[str, float]:
    """
    Merge CeFi reference prices from CoinGecko and CryptoCompare
    CoinGecko is primary, CryptoCompare is secondary for redundancy
    """
    merged = {}
    
    for symbol in set(list(coingecko_prices.keys()) + list(cryptocompare_prices.keys())):
        cg_price = coingecko_prices.get(symbol, float('nan'))
        cc_price = cryptocompare_prices.get(symbol, float('nan'))
        
        # Use CoinGecko as primary if valid
        if not math.isnan(cg_price) and cg_price > 0:
            if not math.isnan(cc_price) and cc_price > 0:
                # Both sources available - use average but weight CoinGecko higher
                merged[symbol] = (cg_price * 0.7) + (cc_price * 0.3)
            else:
                # Only CoinGecko available
                merged[symbol] = cg_price
        elif not math.isnan(cc_price) and cc_price > 0:
            # Only CryptoCompare available  
            merged[symbol] = cc_price
        else:
            # No valid data from either source
            merged[symbol] = float('nan')
    
    return merged

def calculate_cefi_consistency(coingecko_prices: Dict[str, float],
                              cryptocompare_prices: Dict[str, float]) -> Dict[str, float]:
    """
    Calculate consistency between CeFi sources (CoinGecko vs CryptoCompare)
    Returns percentage difference for each symbol
    """
    consistency = {}
    
    for symbol in set(list(coingecko_prices.keys()) + list(cryptocompare_prices.keys())):
        cg_price = coingecko_prices.get(symbol, float('nan'))
        cc_price = cryptocompare_prices.get(symbol, float('nan'))
        
        if not math.isnan(cg_price) and not math.isnan(cc_price) and cg_price > 0 and cc_price > 0:
            # Calculate percentage difference
            diff = abs(cg_price - cc_price) / ((cg_price + cc_price) / 2) * 100
            consistency[symbol] = diff
        else:
            # Can't calculate consistency without both prices
            consistency[symbol] = float('nan')
    
    return consistency

def analyze_peg_deviation(symbol: str, avg_ref_price: float, 
                         sources_used: List[str]) -> PegReport:
    """
    Analyze peg deviation for a single symbol against $1.00 target
    """
    timestamp = int(time.time())
    
    if math.isnan(avg_ref_price) or avg_ref_price <= 0:
        return PegReport(
            symbol=symbol,
            avg_ref=avg_ref_price,
            abs_diff=float('nan'),
            pct_diff=float('nan'),
            bps_diff=float('nan'),
            is_depeg=False,
            status=PegStatus.NORMAL,
            confidence=0.0,
            sources_used=sources_used,
            timestamp=timestamp
        )
    
    # Calculate deviations from $1.00 peg
    abs_diff = abs(avg_ref_price - 1.0)
    pct_diff = abs_diff / 1.0 * 100  # Percentage deviation
    bps_diff = pct_diff * 100  # Basis points deviation
    
    # Determine peg status
    if bps_diff >= DEPEG_THRESHOLD_BPS:
        status = PegStatus.DEPEG
        is_depeg = True
    elif bps_diff >= WARNING_THRESHOLD_BPS:
        status = PegStatus.WARNING
        is_depeg = False
    else:
        status = PegStatus.NORMAL
        is_depeg = False
    
    # Calculate confidence based on number of sources and price reasonableness
    confidence = min(len(sources_used) / 2.0, 1.0)  # Max confidence with 2+ sources
    
    # Reduce confidence for extreme prices
    if avg_ref_price < 0.5 or avg_ref_price > 1.5:
        confidence *= 0.5
    
    return PegReport(
        symbol=symbol,
        avg_ref=avg_ref_price,
        abs_diff=abs_diff,
        pct_diff=pct_diff,
        bps_diff=bps_diff,
        is_depeg=is_depeg,
        status=status,
        confidence=confidence,
        sources_used=sources_used,
        timestamp=timestamp
    )

def compute_peg_analysis(coingecko_prices: Dict[str, float],
                        cryptocompare_prices: Dict[str, float],
                        chainlink_prices: Optional[Dict[str, float]] = None,
                        uniswap_prices: Optional[Dict[str, float]] = None,
                        symbols: Optional[List[str]] = None) -> PegCheckPayload:
    """
    Complete peg analysis computation
    """
    import time
    
    timestamp = int(time.time())
    
    # Determine symbols to analyze
    if symbols is None:
        symbols = list(set(list(coingecko_prices.keys()) + list(cryptocompare_prices.keys())))
    
    # Merge CeFi references
    merged_cefi = merge_cefi_refs(coingecko_prices, cryptocompare_prices)
    
    # Calculate cross-reference consistency
    cefi_consistency = calculate_cefi_consistency(coingecko_prices, cryptocompare_prices)
    
    # Generate reports for each symbol
    reports = []
    for symbol in symbols:
        # Determine which sources have data for this symbol
        sources_used = []
        if symbol in coingecko_prices and not math.isnan(coingecko_prices.get(symbol, float('nan'))):
            sources_used.append("coingecko")
        if symbol in cryptocompare_prices and not math.isnan(cryptocompare_prices.get(symbol, float('nan'))):
            sources_used.append("cryptocompare")
        if chainlink_prices and symbol in chainlink_prices and not math.isnan(chainlink_prices.get(symbol, float('nan'))):
            sources_used.append("chainlink")
        if uniswap_prices and symbol in uniswap_prices and not math.isnan(uniswap_prices.get(symbol, float('nan'))):
            sources_used.append("uniswap")
        
        # Use merged CeFi price as reference
        avg_ref = merged_cefi.get(symbol, float('nan'))
        
        # Generate peg analysis report
        report = analyze_peg_deviation(symbol, avg_ref, sources_used)
        reports.append(report)
    
    return PegCheckPayload(
        as_of=timestamp,
        symbols=symbols,
        coingecko=coingecko_prices,
        cryptocompare=cryptocompare_prices,
        chainlink=chainlink_prices,
        uniswap=uniswap_prices,
        reports=reports,
        cefi_consistency=cefi_consistency,
        config={
            "depeg_threshold_bps": DEPEG_THRESHOLD_BPS,
            "warning_threshold_bps": WARNING_THRESHOLD_BPS
        }
    )