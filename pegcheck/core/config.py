"""
Configuration for peg monitoring system
"""

import os
from typing import Dict, List

# Default symbols to monitor
DEFAULT_SYMBOLS = ["USDT", "USDC", "DAI", "BUSD", "FRAX", "USDP", "TUSD", "PYUSD"]

# Peg thresholds in basis points (bps)
DEPEG_THRESHOLD_BPS = 50  # 0.50%
WARNING_THRESHOLD_BPS = 25  # 0.25%

# API endpoints and keys
COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"
CRYPTOCOMPARE_BASE_URL = "https://min-api.cryptocompare.com"

# Environment variables
CRYPTOCOMPARE_API_KEY = os.getenv("CRYPTOCOMPARE_API_KEY", "")
ETH_RPC_URL = os.getenv("ETH_RPC_URL", "")

# Chainlink feed addresses (Ethereum mainnet)
CHAINLINK_FEEDS = {
    "USDT": "0x3E7d1eAB13ad0104d2750B8863b489D65364e32D",  # USDT/USD
    "USDC": "0x8fFfFfd4AfB6115b954Bd326cbe7B4BA576818f6",  # USDC/USD  
    "DAI": "0xAed0c38402a5d19df6E4c03F4E2DceD6e29c1ee9",   # DAI/USD
    "BUSD": "0x833D8Eb16D306ed1FbB5D7A2E019e106B960965A",  # BUSD/USD
    "FRAX": "0xB9E1E3A9feFf48998E45Fa90847ed4D467E8BcfD",  # FRAX/USD
}

# Uniswap V3 pool configurations  
UNISWAP_POOLS = {
    "USDT": {
        "address": "0x11b815efB8f581194ae79006d24E0d814B7697F6",  # USDT/ETH 0.05%
        "token0": "0xA0b86a33E6441E2476d8F8F554Daddadbd2ec11c",  # USDT
        "token1": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",  # WETH
        "fee": 500
    },
    "USDC": {
        "address": "0x88e6A0c2dDD26FEEb64F039a2c41296FcB3f5640",  # USDC/ETH 0.05%
        "token0": "0xA0b86a33E6441E2476d8F8F554Daddadbd2ec11c",  # USDC
        "token1": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",  # WETH  
        "fee": 500
    },
    "DAI": {
        "address": "0xC2e9F25Be6257c210d7Adf0D4Cd6E3E881ba25f8",  # DAI/ETH 0.30%
        "token0": "0x6B175474E89094C44Da98b954EedeAC495271d0F",  # DAI
        "token1": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",  # WETH
        "fee": 3000
    }
}

# CoinGecko ID mappings
COINGECKO_IDS = {
    "USDT": "tether",
    "USDC": "usd-coin", 
    "DAI": "dai",
    "BUSD": "binance-usd",
    "FRAX": "frax",
    "USDP": "paxos-standard",
    "TUSD": "true-usd",
    "PYUSD": "paypal-usd"
}

# Request timeouts and retry settings
REQUEST_TIMEOUT = 10
MAX_RETRIES = 3
RETRY_DELAY = 1.0

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")