"""
Command Line Interface for PegCheck
Usage: python -m pegcheck.cli --symbols USDT,USDC,DAI --pretty
"""

import argparse
import json
import sys
import asyncio
from typing import List

from .core.config import DEFAULT_SYMBOLS
from .core.compute import compute_peg_analysis
from .sources import coingecko, cryptocompare, chainlink, uniswap

def parse_symbols(symbols_str: str) -> List[str]:
    """Parse comma-separated symbols string"""
    return [s.strip().upper() for s in symbols_str.split(',') if s.strip()]

async def run_peg_check(symbols: List[str], pretty: bool = False, 
                       with_oracle: bool = False, with_dex: bool = False) -> dict:
    """
    Run peg check analysis
    """
    print(f"🔍 Checking peg stability for: {', '.join(symbols)}")
    print("📊 Fetching data from sources...")
    
    # Fetch data from CeFi sources
    print("  • CoinGecko...")
    cg_prices = coingecko.fetch(symbols)
    
    print("  • CryptoCompare...")  
    cc_prices = cryptocompare.fetch(symbols)
    
    # Optional: Chainlink oracles
    chainlink_prices = None
    if with_oracle:
        print("  • Chainlink Oracles...")
        # TODO: Implement chainlink module
        chainlink_prices = {}
    
    # Optional: Uniswap v3 TWAP
    uniswap_prices = None
    if with_dex:
        print("  • Uniswap v3 TWAP...")
        # TODO: Implement uniswap module  
        uniswap_prices = {}
    
    print("🧮 Computing peg analysis...")
    
    # Run peg analysis
    payload = compute_peg_analysis(
        coingecko_prices=cg_prices,
        cryptocompare_prices=cc_prices,
        chainlink_prices=chainlink_prices,
        uniswap_prices=uniswap_prices,
        symbols=symbols
    )
    
    # Convert to JSON-serializable format
    result = {
        "as_of": payload.as_of,
        "symbols": payload.symbols,
        "coingecko": payload.coingecko,
        "cryptocompare": payload.cryptocompare,
        "chainlink": payload.chainlink,
        "uniswap": payload.uniswap,
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
                "sources_used": r.sources_used,
                "timestamp": r.timestamp
            } for r in payload.reports
        ],
        "cefi_consistency": payload.cefi_consistency,
        "config": payload.config,
        "summary": {
            "total_symbols": len(payload.symbols),
            "total_depegs": payload.total_depegs,
            "max_deviation_bps": payload.max_deviation_bps
        }
    }
    
    return result

def format_output(result: dict, pretty: bool = False) -> str:
    """Format output for display"""
    if pretty:
        # Pretty formatted output
        output_lines = []
        output_lines.append("╭─────────────────────────────────────────────╮")
        output_lines.append("│           PegCheck Analysis Report          │")
        output_lines.append("╰─────────────────────────────────────────────╯")
        output_lines.append("")
        
        summary = result.get("summary", {})
        output_lines.append(f"📈 Symbols Analyzed: {summary.get('total_symbols', 0)}")
        output_lines.append(f"🚨 Depegs Detected: {summary.get('total_depegs', 0)}")
        output_lines.append(f"📊 Max Deviation: {summary.get('max_deviation_bps', 0):.1f} bps")
        output_lines.append("")
        
        # Individual symbol reports
        for report in result.get("reports", []):
            symbol = report["symbol"]
            status = report["status"]
            bps_diff = report["bps_diff"]
            avg_ref = report["avg_ref"]
            sources = ", ".join(report["sources_used"])
            
            # Status emoji
            status_emoji = "🟢" if status == "normal" else "🟡" if status == "warning" else "🔴"
            
            output_lines.append(f"{status_emoji} {symbol}")
            output_lines.append(f"   Price: ${avg_ref:.6f}")
            output_lines.append(f"   Deviation: {bps_diff:.1f} bps ({status})")
            output_lines.append(f"   Sources: {sources}")
            output_lines.append("")
        
        # CeFi consistency
        consistency = result.get("cefi_consistency", {})
        if consistency:
            output_lines.append("📡 CeFi Source Consistency:")
            for symbol, diff in consistency.items():
                if not (isinstance(diff, float) and (diff != diff)):  # Check for NaN
                    output_lines.append(f"   {symbol}: {diff:.2f}% difference")
            output_lines.append("")
        
        return "\n".join(output_lines)
    else:
        # JSON output
        return json.dumps(result, indent=2)

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="PegCheck - Stablecoin Peg Monitoring System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m pegcheck.cli --symbols USDT,USDC,DAI --pretty
  python -m pegcheck.cli --symbols USDT,USDC --with_oracle --pretty
  python -m pegcheck.cli --symbols USDT,DAI --with_dex --pretty
        """
    )
    
    parser.add_argument(
        "--symbols",
        type=str,
        default=",".join(DEFAULT_SYMBOLS[:4]),  # Use first 4 default symbols
        help="Comma-separated list of symbols to check (default: USDT,USDC,DAI,BUSD)"
    )
    
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty formatted output instead of JSON"
    )
    
    parser.add_argument(
        "--with_oracle", 
        action="store_true",
        help="Include Chainlink oracle data (requires ETH_RPC_URL)"
    )
    
    parser.add_argument(
        "--with_dex",
        action="store_true", 
        help="Include Uniswap v3 TWAP data (requires ETH_RPC_URL)"
    )
    
    args = parser.parse_args()
    
    # Parse symbols
    symbols = parse_symbols(args.symbols)
    if not symbols:
        print("❌ Error: No valid symbols provided")
        sys.exit(1)
    
    try:
        # Run peg check
        result = asyncio.run(run_peg_check(
            symbols=symbols,
            pretty=args.pretty,
            with_oracle=args.with_oracle,
            with_dex=args.with_dex
        ))
        
        # Format and display output
        output = format_output(result, args.pretty)
        print(output)
        
        # Exit with non-zero code if depegs detected
        summary = result.get("summary", {})
        if summary.get("total_depegs", 0) > 0:
            sys.exit(2)  # Depegs detected
        else:
            sys.exit(0)  # All good
            
    except Exception as e:
        print(f"❌ Error running peg check: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()