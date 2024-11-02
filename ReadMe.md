# Solana Copy Trading Bot (Version 3)

A sophisticated automated trading system that discovers and copies successful Solana traders.

## Version 3 Updates

### Enhanced Configuration System
- Flexible environment variables for all criteria
- Token whitelist with configurable settings
- Improved wallet discovery parameters
- Rate limiting and monitoring controls

### New Features
- Trending pair detection
- Advanced wallet analysis
- Performance metrics tracking
- Detailed research reports

## Project Overview

This Solana Copy Trading Bot:
- Discovers profitable traders automatically
- Monitors their trading activity
- Analyzes trading patterns
- Copies successful trades (optional)
- Manages risk and portfolio

## Configuration Guide

### 1. Trading Pair Criteria (.env)
```bash
# Minimum requirements for trading pairs
MIN_LIQUIDITY_USD=1000        # Minimum liquidity in USD
MIN_DAILY_VOLUME=100000       # Minimum 24h trading volume
MIN_PRICE_CHANGE=10           # Minimum 24h price change percentage
MAX_PRICE_IMPACT=10000        # Maximum price impact percentage
```

### 2. Wallet Finding Criteria (.env)
```bash
# Requirements for profitable traders
MIN_SOL_BALANCE=1.0           # Minimum SOL balance required
MIN_TRADES_DAY=2              # Minimum trades per day
MIN_SUCCESS_RATE=0.5          # Minimum success rate (0.5 = 50%)
MIN_PROFIT_TRADE=0.01         # Minimum profit per trade (0.01 = 1%)
ANALYSIS_PERIOD_DAYS=7        # Number of days to analyze
```

### 3. Token Whitelist (config/token-whitelist.json)
```json
{
    "tokens": {
        "SOL": "So11111111111111111111111111111111111111112",
        "USDC": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
        "RAY": "4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R",
        "SRM": "SRMuApVNdxXokk5GT7XD5cUUgXMBCoAz2LHeuAoKWRt",
        "ORCA": "orcaEKTdK7LKz57vaAYr9QeNsVEPfiu6QeMU1kektZE"
    },
    "settings": {
        "min_liquidity_usd": 1000,
        "max_price_impact": 10000,
        "min_daily_volume": 100000,
        "min_price_change": 10
    }
}
```

### 4. Monitoring Settings (.env)
```bash
# Performance and rate limiting
MONITORING_INTERVAL=60        # Seconds between monitoring cycles
MAX_PAIRS_TO_ANALYZE=20      # Maximum number of pairs to analyze
MAX_WALLETS_TO_ANALYZE=100   # Maximum number of wallets to analyze
REQUESTS_PER_MINUTE=6        # Maximum RPC requests per minute
REQUEST_INTERVAL=10          # Seconds between requests
```

## Operating Modes

### 1. Research Mode
```bash
python main.py --mode research
```
- Discovers profitable traders
- Analyzes trading patterns
- Generates research reports
- No trading execution

### 2. Monitor Mode
```bash
python main.py --mode monitor
```
- Tracks discovered traders
- Real-time trade detection
- Performance tracking
- No trade execution

### 3. Trading Mode
```bash
python main.py --mode trade
```
- Requires private key
- Copies detected trades
- Applies risk management
- Generates reports

## Customizing Criteria

### 1. Adjusting Trading Pair Criteria
- Higher `MIN_LIQUIDITY_USD`: More stable trading
- Higher `MIN_DAILY_VOLUME`: More active pairs
- Higher `MIN_PRICE_CHANGE`: More volatile pairs
- Lower `MAX_PRICE_IMPACT`: More stable prices

### 2. Tuning Wallet Discovery
- Higher `MIN_SOL_BALANCE`: More established traders
- Higher `MIN_TRADES_DAY`: More active traders
- Higher `MIN_SUCCESS_RATE`: More successful traders
- Higher `MIN_PROFIT_TRADE`: More profitable traders

### 3. Optimizing Performance
- Lower `MONITORING_INTERVAL`: More frequent updates
- Lower `MAX_PAIRS_TO_ANALYZE`: Faster analysis
- Lower `MAX_WALLETS_TO_ANALYZE`: Faster processing
- Higher `REQUESTS_PER_MINUTE`: Faster updates (careful with RPC limits)

## Research Reports

The bot generates detailed research reports in JSON format:
```json
{
    "timestamp": "2024-11-02T20:00:00",
    "trending_pairs": {
        "pair_address": {
            "baseToken": {"symbol": "TOKEN"},
            "volume": {"h24": 1000000},
            "liquidity": {"usd": 500000},
            "priceChange": {"h24": 15.5}
        }
    },
    "profitable_wallets": {
        "wallet_address": {
            "sol_balance": 10.5,
            "trades_per_day": 5.2,
            "success_rate": 0.75,
            "profit_rate": 0.12,
            "total_trades": 100
        }
    }
}
```

## Getting Started

1. Copy example configuration:
```bash
cp .env.example .env
```

2. Configure environment variables in .env:
```bash
# Required
SOLANA_RPC_URL=your_rpc_url_here

# Optional
PRIVATE_KEY=your_private_key_here  # For trading mode only
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Start in research mode:
```bash
python main.py --mode research
```

## Security Notes

- Never share your .env file
- Keep private keys secure
- Start with research mode
- Test with small amounts
- Monitor performance regularly

## Dependencies

- solana-py: Solana blockchain interaction
- python-dotenv: Environment management
- aiohttp: Async HTTP requests
- logging: Error tracking

## Best Practices

1. Start with research mode to discover traders
2. Adjust criteria based on market conditions
3. Monitor logs for trade detection
4. Review research reports regularly
5. Test strategies with small amounts
6. Keep configuration files backed up
7. Monitor system resources and RPC usage
