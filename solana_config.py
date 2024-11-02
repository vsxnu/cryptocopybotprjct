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

# Trading Pair Criteria
MIN_LIQUIDITY_USD = float(os.getenv('MIN_LIQUIDITY_USD', '1000'))
MIN_DAILY_VOLUME = float(os.getenv('MIN_DAILY_VOLUME', '100000'))
MIN_PRICE_CHANGE = float(os.getenv('MIN_PRICE_CHANGE', '10'))
MAX_PRICE_IMPACT = float(os.getenv('MAX_PRICE_IMPACT', '10000'))

# Wallet Finding Criteria
MIN_SOL_BALANCE = float(os.getenv('MIN_SOL_BALANCE', '1.0'))
MIN_TRADES_DAY = int(os.getenv('MIN_TRADES_DAY', '2'))
MIN_SUCCESS_RATE = float(os.getenv('MIN_SUCCESS_RATE', '0.5'))
MIN_PROFIT_TRADE = float(os.getenv('MIN_PROFIT_TRADE', '0.01'))
ANALYSIS_PERIOD_DAYS = int(os.getenv('ANALYSIS_PERIOD_DAYS', '7'))

# Token Whitelist
DEFAULT_WHITELIST = {
    'SOL': 'So11111111111111111111111111111111111111112',
    'USDC': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',
    'RAY': '4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R',
    'SRM': 'SRMuApVNdxXokk5GT7XD5cUUgXMBCoAz2LHeuAoKWRt',
    'ORCA': 'orcaEKTdK7LKz57vaAYr9QeNsVEPfiu6QeMU1kektZE'
}

# Build whitelist from environment variables
WHITELISTED_TOKENS = {}
for key, default_value in DEFAULT_WHITELIST.items():
    env_key = f'WHITELIST_{key}'
    if os.getenv(env_key):
        WHITELISTED_TOKENS[key] = os.getenv(env_key)
    else:
        WHITELISTED_TOKENS[key] = default_value

# Monitoring Configuration
MONITORING_INTERVAL = int(os.getenv('MONITORING_INTERVAL', '60'))  # seconds
MAX_PAIRS_TO_ANALYZE = int(os.getenv('MAX_PAIRS_TO_ANALYZE', '20'))
MAX_WALLETS_TO_ANALYZE = int(os.getenv('MAX_WALLETS_TO_ANALYZE', '100'))
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE_PATH = os.getenv('LOG_FILE_PATH', 'logs/trading_bot.log')

# Rate Limiting Configuration
REQUESTS_PER_MINUTE = int(os.getenv('REQUESTS_PER_MINUTE', '6'))
REQUEST_INTERVAL = float(os.getenv('REQUEST_INTERVAL', '10.0'))
MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))

# Retry Configuration
INITIAL_RETRY_DELAY = float(os.getenv('INITIAL_RETRY_DELAY', '1.0'))  # Initial delay in seconds
MAX_RETRY_DELAY = float(os.getenv('MAX_RETRY_DELAY', '60.0'))  # Maximum delay in seconds
WALLET_MONITOR_DELAY = float(os.getenv('WALLET_MONITOR_DELAY', '2.0'))  # Delay between monitoring wallets
TRANSACTION_BATCH_SIZE = int(os.getenv('TRANSACTION_BATCH_SIZE', '50'))  # Number of transactions to fetch per request

# Common token program IDs
TOKEN_PROGRAM_ID = 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA'
ASSOCIATED_TOKEN_PROGRAM_ID = 'ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL'

# DEX Program IDs
RAYDIUM_PROGRAM_ID = '9W959DqEETiGZocYWCQPaJ6sBmUzgfxXfqGeTEdp3aQP'
ORCA_PROGRAM_ID = 'whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc'
JUPITER_PROGRAM_ID = 'JUP4Fb2cqiRUcaTHdrPC8h2gNsA2ETXiPDD33WcGuJB'

# Global rate limiter settings
GLOBAL_RATE_LIMIT = True  # Enable global rate limiting
GLOBAL_REQUEST_INTERVAL = float(os.getenv('REQUEST_INTERVAL', '10.0'))  # Minimum seconds between any RPC requests

# API Usage flags
USE_SOLSCAN = False  # Disable Solscan API since we don't have a key
USE_JUPITER_PRICE = True  # Use Jupiter API for price data
