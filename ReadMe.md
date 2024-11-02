# Solana Copy Trading Bot

A sophisticated automated trading system that discovers and copies successful Solana traders.

## Project Overview

This Solana Copy Trading Bot:
- Monitors successful traders' wallets
- Analyzes their trading patterns
- Automatically copies their profitable trades
- Manages risk and portfolio

## Features

### 1. Real-time Trade Monitoring
- Monitors specified wallets for trading activity
- Detects trades across multiple DEXs (Jupiter, Raydium, Orca)
- Shows trade amounts and token symbols
- Provides Solscan links for verification

### 2. Wallet Management
- Supports wallet nicknames for easy identification
- Configurable monitoring intervals
- Automatic transaction cleanup
- Detailed trade logging

### 3. Risk Management
- Stop-loss and take-profit orders
- Position size limits
- Daily exposure limits
- Slippage control

### 4. Token Management
Trades whitelisted tokens only:
- SOL (native token)
- USDC (stablecoin)
- RAY (Raydium)
- SRM (Serum)
- ORCA (Orca)

## Configuration

### Wallet Configuration (config/tracked-wallets.json)
```json
{
    "wallets": [
        {
            "address": "wallet_address_here",
            "nickname": "Trader1"
        }
    ],
    "settings": {
        "min_trades": 10,
        "min_success_rate": 0.7,
        "min_profit_per_trade": 0.05,
        "monitoring_interval": 60
    }
}
```

### Token Configuration (config/token-whitelist.json)
```json
{
    "tokens": {
        "SOL": "So11111111111111111111111111111111111111112",
        "USDC": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
        "RAY": "4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R"
    },
    "settings": {
        "min_liquidity_usd": 100000,
        "max_price_impact": 0.02,
        "min_daily_volume": 50000
    }
}
```

## Getting Started

1. Create .env file:
```bash
touch .env
```

2. Configure environment variables:
```bash
# Required API Connections
SOLANA_RPC_URL=your_rpc_url_here
BIRDEYE_API_KEY=your_birdeye_api_key_here

# Optional: Private key for executing trades
# PRIVATE_KEY=your_private_key_here

# Trading Parameters
MAX_SLIPPAGE=1.0
MIN_PROFIT_THRESHOLD=1.5
MAX_POSITION_SIZE=10.0
STOP_LOSS_PERCENTAGE=2.0
TAKE_PROFIT_PERCENTAGE=3.0
MAX_TRADES_PER_DAY=10
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the bot:
```bash
python main.py
```

## Monitoring Output

The bot provides detailed trade information:
```
Trade detected:
  Trader: Trader1 (5ZPBHz...)
  DEX: Jupiter
  Amount: 1.2345 SOL
  Transaction: https://solscan.io/tx/...
```

## Operating Modes

### Monitor Only Mode
- Runs without a private key
- Tracks trades in real-time
- Provides detailed logging
- No actual trading

### Trading Mode (requires private key)
- Automatically copies detected trades
- Applies risk management rules
- Manages positions
- Generates performance reports

## Security Notes

- Never share your .env file
- Keep private keys secure
- Start with small amounts for testing
- Monitor the bot's performance regularly

## Performance Reports

The bot generates monitoring reports in monitoring_report.json:
```json
{
    "monitored_wallets": [
        {
            "address": "wallet_address",
            "nickname": "Trader1"
        }
    ],
    "processed_transactions": 100,
    "trading_enabled": false,
    "monitoring_interval": 60,
    "timestamp": "2024-11-02 07:25:49"
}
```

## Rate Limiting and Error Handling

The bot implements:
- Configurable request rate limiting
- Retry logic with exponential backoff
- Error handling for RPC failures
- Automatic request throttling

## Dependencies

- solana-py: Solana blockchain interaction
- python-dotenv: Environment management
- requests: API communication
- pandas: Data analysis
- logging: Error tracking and reporting

## Recommendations

1. Use a dedicated RPC endpoint for reliability
2. Monitor logs for trade detection
3. Start in monitor-only mode
4. Test with small amounts when trading
5. Regularly check performance reports
