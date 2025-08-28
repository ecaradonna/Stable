"""
CryptoCompare API Example
Demonstrates fetching spot prices and historical data
"""

import sys
import os

# Add pegcheck to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pegcheck.sources import cryptocompare

def main():
    print("🔍 CryptoCompare API Example")
    print("=" * 40)
    
    # Test symbols
    symbols = ["USDT", "USDC", "DAI"]
    
    print(f"📊 Fetching spot prices for {', '.join(symbols)}...")
    spot_prices = cryptocompare.fetch(symbols)
    
    for symbol, price in spot_prices.items():
        if price != price:  # Check for NaN
            print(f"  {symbol}: No data available")
        else:
            print(f"  {symbol}: ${price:.6f}")
    
    print("\n📈 Fetching historical data (last 10 days for USDT)...")
    historical_daily = cryptocompare.histoday("USDT", limit=10)
    
    if historical_daily:
        print("  Date                  | Price")
        print("  --------------------- | --------")
        for timestamp, price in historical_daily[-10:]:  # Last 10 entries
            from datetime import datetime
            date_str = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M")
            print(f"  {date_str} | ${price:.6f}")
    else:
        print("  No historical data available")
    
    print("\n⏰ Fetching recent minute data (last 60 minutes, 5-min aggregation for USDC)...")
    historical_minute = cryptocompare.histominute("USDC", limit=60, aggregate=5)
    
    if historical_minute:
        print("  Time                  | Price")
        print("  --------------------- | --------")
        for timestamp, price in historical_minute[-12:]:  # Last 12 entries (1 hour in 5-min intervals)
            from datetime import datetime
            time_str = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M")
            print(f"  {time_str} | ${price:.6f}")
    else:
        print("  No minute data available")
    
    print("\n📊 Multi-symbol full data...")
    full_data = cryptocompare.multiple_symbols_full_data(["USDT", "USDC", "DAI"])
    
    for symbol, data in full_data.items():
        print(f"  {symbol}:")
        print(f"    Price: ${data.get('price', 0):.6f}")
        print(f"    24h Volume: ${data.get('volume_24h', 0):,.0f}")
        print(f"    24h Change: {data.get('change_24h', 0):+.2f}%")
        print(f"    Market Cap: ${data.get('market_cap', 0):,.0f}")

if __name__ == "__main__":
    main()