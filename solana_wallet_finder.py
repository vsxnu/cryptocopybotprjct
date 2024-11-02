"""
Enhanced wallet finder module for discovering profitable wallets based on real-time analysis.
"""

import logging
import json
from pathlib import Path
import asyncio
import aiohttp
from datetime import datetime, timedelta
from solana.rpc.api import Client
from solders.pubkey import Pubkey
from solana_config import (
    SOLANA_RPC_URL, JUPITER_API_URL, JUPITER_HEADERS,
    MIN_SOL_BALANCE, MIN_TRADES_DAY, MIN_SUCCESS_RATE,
    MIN_PROFIT_TRADE, ANALYSIS_PERIOD_DAYS, RAYDIUM_PROGRAM_ID,
    MIN_LIQUIDITY_USD, MIN_DAILY_VOLUME, MIN_PRICE_CHANGE, MAX_PRICE_IMPACT,
    WHITELISTED_TOKENS
)
from solana_bot_config import TradingBotConfig

logger = logging.getLogger(__name__)

class WalletFinder:
    def __init__(self, research_mode=False):
        self.solana_client = Client(SOLANA_RPC_URL)
        self.research_mode = research_mode
        self.discovered_wallets = {}
        self.trending_pairs = {}
        self.bot_config = TradingBotConfig()
        self.tracked_wallets = {w['address']: w for w in self.bot_config.get_tracked_wallets()}
        
        # Load settings from config
        self.min_liquidity = MIN_LIQUIDITY_USD
        self.min_daily_volume = MIN_DAILY_VOLUME
        self.min_price_change = MIN_PRICE_CHANGE
        self.max_price_impact = MAX_PRICE_IMPACT
        
        # Load token whitelist
        self.whitelisted_tokens = WHITELISTED_TOKENS

    def _log_section_header(self, title):
        """Print a section header in the log"""
        logger.info("\n" + "="*80)
        logger.info(title)
        logger.info("="*80)

    def _log_discovery_criteria(self):
        """Log the current discovery criteria"""
        self._log_section_header("WALLET DISCOVERY CRITERIA")
        
        logger.info("\n1. Token Pair Requirements:")
        logger.info("-" * 40)
        logger.info(f"• Minimum liquidity: ${self.min_liquidity:,.2f}")
        logger.info(f"• Minimum daily volume: ${self.min_daily_volume:,.2f}")
        logger.info(f"• Minimum price change 24h: {self.min_price_change:.1f}%")
        logger.info(f"• Maximum price impact: {self.max_price_impact:.1f}%")
        
        logger.info("\n2. Wallet Performance Requirements:")
        logger.info("-" * 40)
        logger.info(f"• Minimum SOL balance: {MIN_SOL_BALANCE:.1f} SOL")
        logger.info(f"• Minimum trades per day: {MIN_TRADES_DAY}")
        logger.info(f"• Minimum success rate: {MIN_SUCCESS_RATE*100:.1f}%")
        logger.info(f"• Minimum profit per trade: {MIN_PROFIT_TRADE*100:.1f}%")
        logger.info(f"• Analysis period: {ANALYSIS_PERIOD_DAYS} days")
        
        logger.info("\n3. Whitelisted Quote Tokens:")
        logger.info("-" * 40)
        for symbol, address in self.whitelisted_tokens.items():
            logger.info(f"• {symbol}: {address}")
        
    async def _fetch_dexscreener_trending(self):
        """Fetch trending pairs from DexScreener"""
        try:
            self._log_section_header("FETCHING TRENDING PAIRS FROM DEXSCREENER")
            self._log_discovery_criteria()
            
            async with aiohttp.ClientSession() as session:
                # Use the token-profiles endpoint that we know works
                url = "https://api.dexscreener.com/token-profiles/latest/v1"
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Filter for Solana tokens
                        solana_pairs = [token for token in data if token.get('chainId') == 'solana']
                        
                        self._log_section_header("ANALYZING TRADING PAIRS")
                        logger.info(f"\nFound {len(solana_pairs)} Solana tokens to analyze")
                        
                        active_pairs = []
                        for token in solana_pairs:
                            try:
                                token_address = token.get('tokenAddress')
                                if not token_address:
                                    continue
                                    
                                # Get detailed pair information
                                pair_url = f"https://api.dexscreener.com/latest/dex/tokens/{token_address}"
                                async with session.get(pair_url) as pair_response:
                                    if pair_response.status == 200:
                                        pair_data = await pair_response.json()
                                        if 'pairs' in pair_data:
                                            for pair in pair_data['pairs']:
                                                try:
                                                    liquidity = float(pair.get('liquidity', {}).get('usd', 0))
                                                    volume_24h = float(pair.get('volume', {}).get('h24', 0))
                                                    price_change_24h = float(pair.get('priceChange', {}).get('h24', 0))
                                                    
                                                    base_symbol = pair.get('baseToken', {}).get('symbol')
                                                    quote_symbol = pair.get('quoteToken', {}).get('symbol')
                                                    dex_url = f"https://dexscreener.com/solana/{pair.get('pairAddress')}"
                                                    
                                                    logger.info(f"\nAnalyzing pair: {base_symbol}/{quote_symbol}")
                                                    logger.info(f"• Volume 24h: ${volume_24h:,.2f}")
                                                    logger.info(f"• Liquidity: ${liquidity:,.2f}")
                                                    logger.info(f"• Price Change 24h: {price_change_24h:.1f}%")
                                                    logger.info(f"• DexScreener: {dex_url}")
                                                    
                                                    if liquidity < self.min_liquidity:
                                                        logger.info(f"✗ Rejected: Low liquidity (minimum ${self.min_liquidity:,.2f})")
                                                        continue
                                                    if volume_24h < self.min_daily_volume:
                                                        logger.info(f"✗ Rejected: Low volume (minimum ${self.min_daily_volume:,.2f})")
                                                        continue
                                                    if price_change_24h < self.min_price_change:
                                                        logger.info(f"✗ Rejected: Low price change (minimum {self.min_price_change:.1f}%)")
                                                        continue
                                                    if not self._is_token_valid(pair):
                                                        logger.info("✗ Rejected: Quote token not whitelisted")
                                                        continue
                                                        
                                                    logger.info("✓ Accepted: Trending pair with high volume")
                                                    active_pairs.append(pair)
                                                        
                                                except (ValueError, TypeError) as e:
                                                    logger.debug(f"Error processing pair metrics: {str(e)}")
                                                    continue
                                                    
                                await asyncio.sleep(0.5)  # Rate limiting
                                
                            except Exception as e:
                                logger.error(f"Error fetching pair data: {str(e)}")
                                continue
                        
                        self._log_section_header("QUALIFIED TRADING PAIRS SUMMARY")
                        logger.info(f"\nFound {len(active_pairs)} qualified pairs:")
                        for pair in active_pairs:
                            logger.info(f"\n{pair.get('baseToken', {}).get('symbol')}/{pair.get('quoteToken', {}).get('symbol')}:")
                            logger.info(f"• Volume 24h: ${float(pair.get('volume', {}).get('h24', 0)):,.2f}")
                            logger.info(f"• Liquidity: ${float(pair.get('liquidity', {}).get('usd', 0)):,.2f}")
                            logger.info(f"• Price Change 24h: {float(pair.get('priceChange', {}).get('h24', 0)):.1f}%")
                            logger.info(f"• Pair Address: {pair.get('pairAddress')}")
                            logger.info(f"• DexScreener: https://dexscreener.com/solana/{pair.get('pairAddress')}")
                        
                        return active_pairs
                    else:
                        logger.error(f"DexScreener API error: {response.status}")
                        logger.error(f"Response: {await response.text()}")
                        return []
        except Exception as e:
            logger.error(f"Error fetching trending pairs: {str(e)}")
            return []

    def _is_token_valid(self, pair):
        """Check if tokens in pair are valid/whitelisted"""
        try:
            quote_address = pair.get('quoteToken', {}).get('address')
            # Check if quote token is in whitelist
            return quote_address in self.whitelisted_tokens.values()
                    
        except Exception as e:
            logger.error(f"Error checking token validity: {str(e)}")
            return False

    async def _analyze_wallet_transactions(self, wallet_address):
        """Analyze a wallet's transaction history"""
        try:
            if wallet_address in self.tracked_wallets:
                logger.debug(f"Skipping {wallet_address}: Already tracked")
                return None
            
            logger.info(f"\nAnalyzing wallet: {wallet_address}")
            logger.info(f"Solscan: https://solscan.io/account/{wallet_address}")
            
            # Get recent transactions
            signatures = self.solana_client.get_signatures_for_address(
                Pubkey.from_string(wallet_address),
                limit=100  # Analyze last 100 transactions
            )
            
            if not signatures.value:
                logger.info("✗ Rejected: No transactions found")
                return None
            
            # Get wallet SOL balance
            balance = self.solana_client.get_balance(
                Pubkey.from_string(wallet_address)
            )
            sol_balance = balance.value / 1e9  # Convert lamports to SOL
            
            logger.info(f"• SOL Balance: {sol_balance:.2f}")
            
            if sol_balance < MIN_SOL_BALANCE:
                logger.info(f"✗ Rejected: Low SOL balance (minimum {MIN_SOL_BALANCE:.1f} SOL)")
                return None
            
            # Analyze transactions
            trades = []
            success_count = 0
            profit_count = 0
            
            logger.info("Analyzing recent transactions...")
            for sig in signatures.value[:100]:  # Analyze last 100 transactions
                tx = self.solana_client.get_transaction(
                    sig.signature,
                    max_supported_transaction_version=0
                )
                
                if not tx.value:
                    continue
                
                # Check if transaction involves Raydium
                if any(str(account.pubkey) == RAYDIUM_PROGRAM_ID 
                      for account in tx.value.transaction.message.account_keys):
                    trades.append({
                        'signature': sig.signature,
                        'timestamp': sig.block_time,
                        'success': tx.value.meta.status.Ok is not None
                    })
                    
                    if tx.value.meta.status.Ok is not None:
                        success_count += 1
                        if len(trades) % 2 == 0:
                            profit_count += 1
            
            # Calculate metrics
            total_trades = len(trades)
            if total_trades == 0:
                logger.info("✗ Rejected: No DEX trades found")
                return None
                
            trades_per_day = total_trades / ANALYSIS_PERIOD_DAYS
            success_rate = success_count / total_trades if total_trades > 0 else 0
            profit_rate = profit_count / total_trades if total_trades > 0 else 0
            
            logger.info("\nTrading Metrics:")
            logger.info(f"• Total trades: {total_trades}")
            logger.info(f"• Trades per day: {trades_per_day:.1f}")
            logger.info(f"• Success rate: {success_rate*100:.1f}%")
            logger.info(f"• Profit rate: {profit_rate*100:.1f}%")
            
            # Check if wallet meets criteria
            if trades_per_day < MIN_TRADES_DAY:
                logger.info(f"✗ Rejected: Low trade frequency (minimum {MIN_TRADES_DAY} trades/day)")
                return None
            if success_rate < MIN_SUCCESS_RATE:
                logger.info(f"✗ Rejected: Low success rate (minimum {MIN_SUCCESS_RATE*100:.1f}%)")
                return None
            if profit_rate < MIN_PROFIT_TRADE:
                logger.info(f"✗ Rejected: Low profit rate (minimum {MIN_PROFIT_TRADE*100:.1f}%)")
                return None
                
            logger.info("\n✓ Wallet Accepted: Meets all criteria")
            
            # Log recent trades
            logger.info("\nRecent trades:")
            for trade in trades[:5]:  # Show last 5 trades
                logger.info(f"• Transaction: https://solscan.io/tx/{trade['signature']}")
            
            return {
                'address': wallet_address,
                'sol_balance': sol_balance,
                'trades_per_day': trades_per_day,
                'success_rate': success_rate,
                'profit_rate': profit_rate,
                'total_trades': total_trades,
                'last_trade_time': trades[0]['timestamp'] if trades else None,
                'solscan_url': f"https://solscan.io/account/{wallet_address}",
                'recent_trades': [f"https://solscan.io/tx/{t['signature']}" for t in trades[:5]]
            }
            
        except Exception as e:
            logger.error(f"Error analyzing wallet {wallet_address}: {str(e)}")
            return None

    async def find_profitable_wallets(self):
        """Find profitable wallets based on recent trading activity"""
        self._log_section_header("STARTING ENHANCED SOLANA WALLET DISCOVERY")
        
        # Get trending pairs
        logger.info("\nStep 1: Fetching trending pairs...")
        trending_pairs = await self._fetch_dexscreener_trending()
        self.trending_pairs = {pair.get('pairAddress'): pair for pair in trending_pairs}
        
        self._log_section_header("ANALYZING TRADING ACTIVITY")
        discovered_wallets = {}
        
        # Extract unique wallet addresses from trending pair transactions
        wallet_addresses = set()
        for pair in trending_pairs:
            try:
                pair_address = Pubkey.from_string(pair.get('pairAddress'))
                signatures = self.solana_client.get_signatures_for_address(
                    pair_address,
                    limit=50  # Look at last 50 transactions
                )
                
                if signatures.value:
                    for sig in signatures.value[:50]:  # Look at last 50 transactions
                        tx = self.solana_client.get_transaction(
                            sig.signature,
                            max_supported_transaction_version=0
                        )
                        if tx.value:
                            # Extract wallet addresses from transaction
                            for account in tx.value.transaction.message.account_keys:
                                wallet_addresses.add(str(account.pubkey))
                                
            except Exception as e:
                logger.error(f"Error processing pair {pair.get('pairAddress')}: {str(e)}")
                continue
        
        logger.info(f"\nFound {len(wallet_addresses)} unique wallet addresses to analyze")
        
        # Analyze each wallet
        analyzed_count = 0
        for wallet_address in wallet_addresses:
            analyzed_count += 1
            logger.info(f"\nProgress: Analyzing wallet {analyzed_count} of {len(wallet_addresses)}")
            
            wallet_data = await self._analyze_wallet_transactions(wallet_address)
            if wallet_data:
                discovered_wallets[wallet_address] = wallet_data
        
        # Summarize discoveries
        self._log_section_header("WALLET DISCOVERY SUMMARY")
        logger.info(f"\nAnalyzed {len(wallet_addresses)} unique wallets")
        logger.info(f"Discovered {len(discovered_wallets)} profitable wallets")
        
        if discovered_wallets:
            logger.info("\nProfitable Wallets Found:")
            for address, data in discovered_wallets.items():
                logger.info(f"\nWallet: {address}")
                logger.info(f"Solscan: {data['solscan_url']}")
                logger.info("\nPerformance Metrics:")
                logger.info(f"• SOL Balance: {data['sol_balance']:.2f}")
                logger.info(f"• Trades per day: {data['trades_per_day']:.1f}")
                logger.info(f"• Success rate: {data['success_rate']*100:.1f}%")
                logger.info(f"• Profit rate: {data['profit_rate']*100:.1f}%")
                logger.info(f"• Total trades: {data['total_trades']}")
                logger.info("\nRecent trades:")
                for tx_url in data['recent_trades']:
                    logger.info(f"• {tx_url}")
            
            self._save_tracked_wallets(discovered_wallets)
        else:
            logger.info("\nNo wallets met the profitability criteria")
        
        # Save research results
        self._save_research_results(discovered_wallets)
        
        return list(discovered_wallets.values())

    def _save_tracked_wallets(self, new_wallets):
        """Save updated wallet list to config"""
        try:
            config = self.bot_config.tracked_wallets
            existing_addresses = {w['address'] for w in config['wallets']}
            next_trader_num = max([int(w['nickname'].replace('Trader', '')) 
                                 for w in config['wallets'] if w['nickname'].startswith('Trader')] + [0]) + 1
            
            for address, data in new_wallets.items():
                if address not in existing_addresses:
                    config['wallets'].append({
                        'address': address,
                        'nickname': f'Trader{next_trader_num}',
                        'metrics': {
                            'sol_balance': data['sol_balance'],
                            'trades_per_day': data['trades_per_day'],
                            'success_rate': data['success_rate'],
                            'profit_rate': data['profit_rate'],
                            'total_trades': data['total_trades'],
                            'last_trade_time': data['last_trade_time'],
                            'discovery_time': datetime.now().isoformat(),
                            'solscan_url': data['solscan_url'],
                            'recent_trades': data['recent_trades']
                        }
                    })
                    next_trader_num += 1
            
            self.bot_config.update_tracked_wallets(config)
            logger.info(f"\nUpdated tracked-wallets.json with {len(new_wallets)} new wallets")
            
        except Exception as e:
            logger.error(f"Error saving tracked wallets: {str(e)}")

    def _save_research_results(self, wallets: dict):
        """Save research results to a file"""
        try:
            research_data = {
                'timestamp': datetime.now().isoformat(),
                'trending_pairs': self.trending_pairs,
                'profitable_wallets': wallets,
                'analysis_parameters': {
                    'min_sol_balance': MIN_SOL_BALANCE,
                    'min_trades_day': MIN_TRADES_DAY,
                    'min_success_rate': MIN_SUCCESS_RATE,
                    'min_profit_trade': MIN_PROFIT_TRADE,
                    'analysis_period_days': ANALYSIS_PERIOD_DAYS,
                    'token_settings': {
                        'min_liquidity_usd': self.min_liquidity,
                        'max_price_impact': self.max_price_impact,
                        'min_daily_volume': self.min_daily_volume,
                        'min_price_change': self.min_price_change
                    }
                }
            }
            
            Path('logs').mkdir(exist_ok=True)
            filename = f"logs/research_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(research_data, f, indent=2, default=str)
            
            logger.info(f"\nDetailed research results saved to: {filename}")
            
        except Exception as e:
            logger.error(f"Error saving research results: {str(e)}")
