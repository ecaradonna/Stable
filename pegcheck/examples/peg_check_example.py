"""
PegCheck Example
Demonstrates full peg monitoring functionality
"""

import sys
import os
import asyncio
import json

# Add pegcheck to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pegcheck.core.compute import compute_peg_analysis
from pegcheck.sources import coingecko, cryptocompare

async def run_example():
    print("🔍 PegCheck Full Example")
    print("=" * 50)
    
    # Test symbols
    symbols = ["USDT", "USDC", "DAI", "BUSD"]
    
    print(f"📊 Checking peg stability for: {', '.join(symbols)}")
    print("\n🌐 Fetching data from sources...")
    
    # Fetch from CoinGecko
    print("  • CoinGecko...")
    cg_prices = coingecko.fetch(symbols)
    
    # Fetch from CryptoCompare
    print("  • CryptoCompare...")
    cc_prices = cryptocompare.fetch(symbols)
    
    print("\n📈 Source Data:")
    print("Symbol | CoinGecko  | CryptoCompare")
    print("-------|------------|-------------")
    for symbol in symbols:
        cg_price = cg_prices.get(symbol, float('nan'))
        cc_price = cc_prices.get(symbol, float('nan'))
        
        cg_str = f"${cg_price:.6f}" if cg_price == cg_price else "N/A"
        cc_str = f"${cc_price:.6f}" if cc_price == cc_price else "N/A"
        
        print(f"{symbol:<6} | {cg_str:<10} | {cc_str}")
    
    print("\n🧮 Computing peg analysis...")
    
    # Run peg analysis
    payload = compute_peg_analysis(
        coingecko_prices=cg_prices,
        cryptocompare_prices=cc_prices,
        symbols=symbols
    )
    
    print("\n📊 Peg Analysis Results:")
    print("=" * 70)
    
    for report in payload.reports:
        status_emoji = "🟢" if report.status.value == "normal" else "🟡" if report.status.value == "warning" else "🔴"
        
        print(f"{status_emoji} {report.symbol}")
        print(f"   Average Reference: ${report.avg_ref:.6f}")
        print(f"   Deviation: {report.bps_diff:.1f} basis points ({report.status.value.upper()})")
        print(f"   Confidence: {report.confidence:.2f}")
        print(f"   Sources: {', '.join(report.sources_used)}")
        
        if report.is_depeg:
            print(f"   ⚠️  DEPEG DETECTED!")
        
        print()
    
    print("📈 Summary:")
    print(f"   Total symbols: {len(payload.reports)}")
    print(f"   Depegs detected: {payload.total_depegs}")
    print(f"   Max deviation: {payload.max_deviation_bps:.1f} bps")
    
    print("\n🔄 CeFi Source Consistency:")
    for symbol, consistency in payload.cefi_consistency.items():
        if consistency == consistency:  # Not NaN
            status = "✅" if consistency < 1.0 else "⚠️" if consistency < 5.0 else "❌"
            print(f"   {symbol}: {consistency:.2f}% difference {status}")
        else:
            print(f"   {symbol}: Cannot calculate (missing data)")
    
    print(f"\n💾 Full JSON payload available with {len(payload.reports)} reports")
    
    # Optional: Save to file
    save_to_file = input("\n💾 Save results to JSON file? (y/N): ").lower().startswith('y')
    if save_to_file:
        output_data = {
            "as_of": payload.as_of,
            "symbols": payload.symbols,
            "coingecko": payload.coingecko,
            "cryptocompare": payload.cryptocompare,
            "reports": [
                {
                    "symbol": r.symbol,
                    "avg_ref": r.avg_ref,
                    "abs_diff": r.abs_diff,
                    "pct_diff": r.pct_diff,
                    "bps_diff": r.bps_diff,
                    "is_depeg": r.is_depeg,
                    "status": r.status.value,
                    "confidence": r.confidence,
                    "sources_used": r.sources_used
                } for r in payload.reports
            ],
            "cefi_consistency": payload.cefi_consistency,
            "summary": {
                "total_symbols": len(payload.symbols),
                "total_depegs": payload.total_depegs,
                "max_deviation_bps": payload.max_deviation_bps
            }
        }
        
        filename = f"pegcheck_results_{payload.as_of}.json"
        with open(filename, 'w') as f:
            json.dump(output_data, f, indent=2, default=str)
        
        print(f"✅ Results saved to {filename}")

if __name__ == "__main__":
    asyncio.run(run_example())