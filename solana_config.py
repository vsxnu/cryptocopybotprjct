"""
General Solana configuration settings
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Solana RPC Configuration
SOLANA_RPC_URL = os.getenv('SOLANA_RPC_URL', 'https://api.mainnet-beta.solana.com')
COMMITMENT_LEVEL = 'finalized'

# Alternative API endpoints
SOLSCAN_API_URL = "https://api.solscan.io/v2"  # Updated endpoint with version
JUPITER_API_URL = "https://price.jup.ag/v4"
DEXSCREENER_API_URL = "https://api.dexscreener.com/latest/dex"

# API Headers
SOLSCAN_HEADERS = {
    'Accept': 'application/json',
    'User-Agent': 'Solana-Trading-Bot/1.0',
    'token': os.getenv('SOLSCAN_API_KEY', '')
}

JUPITER_HEADERS = {
    'Accept': 'application/json',
    'User-Agent': 'Solana-Trading-Bot/1.0'
}

DEXSCREENER_HEADERS = {
    'Accept': 'application/json',
    'User-Agent': 'Solana-Trading-Bot/1.0'
}

# RPC rate limiting configuration (ultra-conservative for public RPC)
REQUESTS_PER_MINUTE = 6  # 1 request every 10 seconds
REQUEST_INTERVAL = 60.0 / REQUESTS_PER_MINUTE  # Time between requests in seconds
MAX_RETRIES = 3
INITIAL_RETRY_DELAY = 10  # Start with 10 seconds delay
MAX_RETRY_DELAY = 60  # Maximum 1 minute delay

# Analysis Parameters
MIN_SOL_BALANCE = float(os.getenv('MIN_SOL_BALANCE', '10.0'))
MIN_TRADES_DAY = int(os.getenv('MIN_TRADES_DAY', '5'))
MIN_SUCCESS_RATE = float(os.getenv('MIN_SUCCESS_RATE', '0.7'))
MIN_PROFIT_TRADE = float(os.getenv('MIN_PROFIT_TRADE', '0.02'))
ANALYSIS_PERIOD_DAYS = int(os.getenv('ANALYSIS_PERIOD_DAYS', '7'))
TARGET_DEXES = os.getenv('TARGET_DEXES', 'raydium,orca,jupiter').split(',')

# Common token program IDs
TOKEN_PROGRAM_ID = 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA'
ASSOCIATED_TOKEN_PROGRAM_ID = 'ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL'

# DEX Program IDs
RAYDIUM_PROGRAM_ID = '9W959DqEETiGZocYWCQPaJ6sBmUzgfxXfqGeTEdp3aQP'
ORCA_PROGRAM_ID = 'whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc'
JUPITER_PROGRAM_ID = 'JUP4Fb2cqiRUcaTHdrPC8h2gNsA2ETXiPDD33WcGuJB'

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE_PATH = os.getenv('LOG_FILE_PATH', 'logs/trading_bot.log')

# Monitoring Configuration
MONITORING_INTERVAL = int(os.getenv('MONITORING_INTERVAL', '60'))  # seconds
WALLET_MONITOR_DELAY = 15  # seconds between monitoring each wallet
TRANSACTION_BATCH_SIZE = 1  # number of transactions to fetch at once

# Global rate limiter settings
GLOBAL_RATE_LIMIT = True  # Enable global rate limiting
GLOBAL_REQUEST_INTERVAL = 10.0  # Minimum 10 seconds between any RPC requests

# API Usage flags
USE_SOLSCAN = False  # Disable Solscan API since we don't have a key
USE_JUPITER_PRICE = True  # Use Jupiter API for price data
