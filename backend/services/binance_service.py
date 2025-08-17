import aiohttp
import hmac
import hashlib
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
import os

logger = logging.getLogger(__name__)

class BinanceService:
    def __init__(self):
        self.base_url = "https://api.binance.com"
        self.api_key = os.getenv('BINANCE_API_KEY', 'DEMO_KEY')
        self.api_secret = os.getenv('BINANCE_API_SECRET', 'DEMO_SECRET')
        self.stablecoins = ["USDT", "USDC", "DAI", "TUSD"]
        
    def _generate_signature(self, query_string: str) -> str:
        """Generate signature for Binance API"""
        return hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    async def get_flexible_products(self) -> List[Dict[str, Any]]:
        """Get flexible savings products from Binance"""
        if self.api_key == 'DEMO_KEY':
            # Return demo data when no API key is provided
            return self._get_demo_binance_data()
            
        try:
            timestamp = int(time.time() * 1000)
            query_string = f"timestamp={timestamp}"
            signature = self._generate_signature(query_string)
            
            headers = {
                'X-MBX-APIKEY': self.api_key
            }
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/sapi/v1/simple-earn/flexible/list?{query_string}&signature={signature}"
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('rows', [])
                    else:
                        logger.error(f"Binance API error: {response.status}")
                        return self._get_demo_binance_data()
        except Exception as e:
            logger.error(f"Binance service error: {str(e)}")
            return self._get_demo_binance_data()
    
    def _get_demo_binance_data(self) -> List[Dict[str, Any]]:
        """Demo data for when Binance API is not available"""
        return [
            {
                'asset': 'USDT',
                'latestAnnualPercentageRate': '0.0845',
                'tierAnnualPercentageRate': {
                    'tier': 1,
                    'annualPercentageRate': '0.0845'
                },
                'minPurchaseAmount': '10',
                'purchasedAmount': '1000000',
                'status': 'PURCHASING'
            },
            {
                'asset': 'USDC', 
                'latestAnnualPercentageRate': '0.0712',
                'tierAnnualPercentageRate': {
                    'tier': 1,
                    'annualPercentageRate': '0.0712'
                },
                'minPurchaseAmount': '10',
                'purchasedAmount': '500000',
                'status': 'PURCHASING'
            },
            {
                'asset': 'TUSD',
                'latestAnnualPercentageRate': '0.0423',
                'tierAnnualPercentageRate': {
                    'tier': 1,
                    'annualPercentageRate': '0.0423'
                },
                'minPurchaseAmount': '10',
                'purchasedAmount': '100000',
                'status': 'PURCHASING'
            }
        ]
    
    async def get_stablecoin_yields(self) -> Dict[str, Dict[str, Any]]:
        """Get yields for stablecoins from Binance Earn"""
        products = await self.get_flexible_products()
        yields = {}
        
        for product in products:
            asset = product.get('asset', '')
            if asset in self.stablecoins and product.get('status') == 'PURCHASING':
                apy = float(product.get('latestAnnualPercentageRate', 0)) * 100
                
                yields[asset] = {
                    'stablecoin': asset,
                    'name': self._get_coin_name(asset),
                    'currentYield': apy,
                    'source': 'Binance Earn',
                    'sourceType': 'CeFi',
                    'riskScore': 'Low',  # Binance is considered low risk
                    'liquidity': self._format_liquidity(product.get('purchasedAmount', 0)),
                    'metadata': {
                        'minPurchaseAmount': product.get('minPurchaseAmount'),
                        'tier': product.get('tierAnnualPercentageRate', {}).get('tier', 1)
                    }
                }
        
        return yields
    
    def _get_coin_name(self, asset: str) -> str:
        """Get full name for stablecoin"""
        names = {
            'USDT': 'Tether USD',
            'USDC': 'USD Coin',
            'DAI': 'Dai Stablecoin', 
            'TUSD': 'TrueUSD'
        }
        return names.get(asset, asset)
    
    def _format_liquidity(self, amount: str) -> str:
        """Format amount as liquidity string"""
        try:
            amount_float = float(amount)
            if amount_float >= 1e9:
                return f"${amount_float/1e9:.1f}B"
            elif amount_float >= 1e6:
                return f"${amount_float/1e6:.1f}M"
            else:
                return f"${amount_float:,.0f}"
        except:
            return "N/A"