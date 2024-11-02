"""
Enhanced trading bot implementation with dynamic wallet discovery
"""

import os
from solana.rpc.api import Client
from solders.pubkey import Pubkey
import time
import logging
from datetime import datetime
import json
from typing import Dict, List, Optional
from dotenv import load_dotenv
from pathlib import Path
import asyncio
import aiohttp
from rate_limiter import GlobalRateLimiter
from solana_config import (
    SOLANA_RPC_URL, JUPITER_API_URL, JUPITER_HEADERS,
    REQUESTS_PER_MINUTE, REQUEST_INTERVAL,
    MAX_RETRIES, INITIAL_RETRY_DELAY, MAX_RETRY_DELAY,
    MONITORING_INTERVAL, WALLET_MONITOR_DELAY, TRANSACTION_BATCH_SIZE,
    USE_JUPITER_PRICE
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class SolanaTradingBot:
    def __init__(self, discovered_wallets=None, trending_pairs=None):
        load_dotenv()
        
        # Initialize Solana client
        self.solana_client = Client(SOLANA_RPC_URL)
        logger.info(f"Connected to Solana RPC: {SOLANA_RPC_URL}")
        
        # Initialize rate limiter
        self.rate_limiter = GlobalRateLimiter()
        
        # Load wallet if private key is available
        private_key = os.getenv('PRIVATE_KEY')
        if private_key:
            logger.info("Private key found. Trading enabled.")
            self.trading_enabled = True
        else:
            logger.warning("No private key found. Running in monitoring mode only.")
            self.trading_enabled = False
        
        # Initialize tracking for discovered wallets
        self.tracked_wallets = self._setup_tracked_wallets(discovered_wallets)
        self.trending_pairs = trending_pairs or {}
        
        # Create wallet nickname mapping
        self.wallet_nicknames = self._create_wallet_nickname_mapping()
        
        # Initialize processed transactions set
        self.processed_transactions = set()
        
        # DEX Program IDs
        self.dex_programs = {
            "Raydium": "9W959DqEETiGZocYWCQPaJ6sBmUzgfxXfqGeTEdp3aQP",
            "Jupiter": "JUP4Fb2cqiRUcaTHdrPC8h2gNsA2ETXiPDD33WcGuJB",
            "Orca": "whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc"
        }
        
        logger.info("-" * 60)
        logger.info("Trading Bot Configuration:")
        logger.info(f"Trading Enabled: {self.trading_enabled}")
        logger.info(f"Tracked Wallets: {len(self.tracked_wallets)}")
        logger.info(f"Trending Pairs: {len(self.trending_pairs)}")
        logger.info(f"RPC Rate Limit: {REQUESTS_PER_MINUTE} requests/minute")
        logger.info(f"Using Jupiter Price API: {USE_JUPITER_PRICE}")
        logger.info(f"Monitoring Interval: {MONITORING_INTERVAL} seconds")
        logger.info("-" * 60)

    def _setup_tracked_wallets(self, discovered_wallets) -> List[Dict]:
        """Setup tracked wallets from discovered wallets"""
        if not discovered_wallets:
            logger.warning("No discovered wallets provided")
            return []
            
        wallets = []
        for wallet in discovered_wallets:
            if isinstance(wallet, dict):
                wallets.append({
                    'address': wallet['address'],
                    'nickname': f"Wallet_{wallet['address'][:6]}",
                    'stats': wallet.get('stats', {}),
                    'involved_in_trending': wallet.get('involved_in_trending', False)
                })
        
        logger.info(f"Setup {len(wallets)} tracked wallets from discoveries")
        return wallets

    def _create_wallet_nickname_mapping(self) -> Dict[str, str]:
        """Create mapping of wallet addresses to nicknames"""
        mapping = {}
        for wallet in self.tracked_wallets:
            mapping[wallet['address']] = wallet.get('nickname', wallet['address'][:8])
        return mapping

    def _get_dex_name(self, program_id: str) -> str:
        """Get DEX name from program ID"""
        for dex_name, dex_program in self.dex_programs.items():
            if program_id == dex_program:
                return dex_name
        return "Unknown DEX"

    def _is_swap_instruction(self, instruction: Dict) -> bool:
        """Check if instruction is a swap/trade"""
        try:
            program_id = instruction.get('programId')
            return program_id in self.dex_programs.values()
        except Exception:
            return False

    def _parse_token_amounts(self, transaction: Dict) -> float:
        """Parse token amounts from transaction"""
        try:
            pre_balances = transaction.get('meta', {}).get('preBalances', [])
            post_balances = transaction.get('meta', {}).get('postBalances', [])
            
            if pre_balances and post_balances:
                balance_change = sum(post - pre for post, pre in zip(post_balances, pre_balances))
                return abs(balance_change) / 1e9  # Convert lamports to SOL
            return 0
        except Exception:
            return 0

    async def get_jupiter_price(self, token_address: str) -> Optional[float]:
        """Get token price from Jupiter API"""
        try:
            url = f"{JUPITER_API_URL}/price?ids={token_address}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=JUPITER_HEADERS) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('data', {}).get(token_address, {}).get('price')
                    else:
                        logger.debug(f"Jupiter API error: {response.status}")
                        return None
        except Exception as e:
            logger.debug(f"Error getting Jupiter price: {str(e)}")
            return None

    def _is_trending_pair(self, token_address: str) -> bool:
        """Check if token is in trending pairs"""
        try:
            return any(
                token_address in [
                    pair.get('baseToken', {}).get('address'),
                    pair.get('quoteToken', {}).get('address')
                ]
                for pair in self.trending_pairs.values()
            )
        except Exception as e:
            logger.debug(f"Error checking trending pair: {str(e)}")
            return False

    async def monitor_wallet(self, wallet_info: Dict):
        """Monitor a wallet for trading activity"""
        try:
            wallet_address = wallet_info['address']
            wallet_nickname = wallet_info.get('nickname', wallet_address[:8])
            
            # Add delay between monitoring attempts
            await self.rate_limiter.wait()
            
            # Get wallet's recent transactions
            try:
                response = self.solana_client.get_signatures_for_address(
                    Pubkey.from_string(wallet_address),
                    limit=TRANSACTION_BATCH_SIZE
                )
                
                if not hasattr(response, 'value') or not response.value:
                    return
                    
                transactions = response.value
                
                # Reset backoff on success
                self.rate_limiter.reset_backoff()
                
                for sig_info in transactions:
                    if sig_info.signature in self.processed_transactions:
                        continue

                    # Add transaction to processed set
                    self.processed_transactions.add(sig_info.signature)
                    
                    try:
                        # Wait for rate limit
                        await self.rate_limiter.wait()
                        
                        # Get transaction details with retries
                        for attempt in range(MAX_RETRIES):
                            try:
                                tx = self.solana_client.get_transaction(
                                    sig_info.signature,
                                    commitment="finalized"
                                )
                                
                                if not hasattr(tx, 'value') or not tx.value:
                                    continue
                                    
                                # Reset backoff on success
                                self.rate_limiter.reset_backoff()
                                break
                                
                            except Exception as e:
                                if "429" in str(e):
                                    await self.rate_limiter.handle_429()
                                    if attempt < MAX_RETRIES - 1:
                                        continue
                                raise e
                        else:
                            logger.debug(f"Max retries reached for transaction {sig_info.signature}")
                            continue
                        
                        # Check if transaction contains swap instructions
                        instructions = tx.value.transaction.message.instructions
                        for ix in instructions:
                            if self._is_swap_instruction(ix):
                                dex_name = self._get_dex_name(ix.get('programId'))
                                amount = self._parse_token_amounts(tx.value)
                                
                                # Get token price if available
                                token_price = None
                                token_address = ix.get('tokenAddress')
                                if USE_JUPITER_PRICE and token_address:
                                    token_price = await self.get_jupiter_price(token_address)
                                
                                # Check if token is trending
                                is_trending = self._is_trending_pair(token_address) if token_address else False
                                
                                # Log the trade with detailed information
                                logger.info("+" + "="*58 + "+")
                                logger.info("|" + " "*20 + "TRADE DETECTED" + " "*24 + "|")
                                logger.info("+" + "="*58 + "+")
                                logger.info(f"| Trader    : {wallet_nickname} ({wallet_address[:8]}...)")
                                logger.info(f"| DEX       : {dex_name}")
                                if amount > 0:
                                    logger.info(f"| Amount    : {amount:.4f} SOL")
                                if token_price:
                                    logger.info(f"| Price     : ${token_price:.4f}")
                                if is_trending:
                                    logger.info(f"| Status    : TRENDING")
                                logger.info(f"| Timestamp : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                                logger.info(f"| TX        : https://solscan.io/tx/{sig_info.signature}")
                                logger.info("+" + "-"*58 + "+")
                            
                    except Exception as tx_error:
                        logger.debug(f"Error getting transaction: {str(tx_error)}")
                        continue

            except Exception as e:
                if "429" in str(e):
                    await self.rate_limiter.handle_429()
                    return
                logger.debug(f"Error getting signatures: {str(e)}")
                return
                
        except Exception as e:
            logger.error(f"Error monitoring wallet {wallet_nickname}: {str(e)}")
            return

    async def run(self):
        """Main bot loop"""
        logger.info("+" + "="*58 + "+")
        logger.info("|" + " "*20 + "BOT STARTED" + " "*27 + "|")
        logger.info("+" + "="*58 + "+")
        
        # Get monitoring interval from config
        monitoring_interval = MONITORING_INTERVAL
        logger.info(f"Monitoring interval: {monitoring_interval} seconds")
        
        while True:
            try:
                if not self.tracked_wallets:
                    logger.warning("No wallets to monitor")
                    await asyncio.sleep(monitoring_interval)
                    continue
                
                for wallet in self.tracked_wallets:
                    try:
                        await self.monitor_wallet(wallet)
                    except Exception as e:
                        nickname = wallet.get('nickname', wallet['address'][:8])
                        logger.error(f"Error monitoring {nickname}: {str(e)}")
                    finally:
                        # Add significant delay between wallets
                        await asyncio.sleep(WALLET_MONITOR_DELAY)
                
                # Clean up old transactions periodically
                self._clean_old_transactions()
                
                # Add delay between monitoring cycles based on config
                logger.debug(f"Completed monitoring cycle, waiting {monitoring_interval}s...")
                await asyncio.sleep(monitoring_interval)
                
            except Exception as e:
                logger.error(f"Error in main loop: {str(e)}")
                await asyncio.sleep(5)
                
            except KeyboardInterrupt:
                logger.info("Received shutdown signal")
                break

    def _clean_old_transactions(self):
        """Clean up old transactions from memory"""
        try:
            if len(self.processed_transactions) > 1000:
                logger.info("Cleaning up old processed transactions")
                self.processed_transactions = set(list(self.processed_transactions)[-500:])
        except Exception as e:
            logger.error(f"Error cleaning transactions: {str(e)}")

    def generate_reports(self):
        """Generate monitoring report"""
        try:
            report = {
                'monitored_wallets': [
                    {
                        'address': w['address'],
                        'nickname': w.get('nickname', w['address'][:8]),
                        'stats': w.get('stats', {}),
                        'involved_in_trending': w.get('involved_in_trending', False)
                    } for w in self.tracked_wallets
                ],
                'processed_transactions': len(self.processed_transactions),
                'trading_enabled': self.trading_enabled,
                'monitoring_interval': MONITORING_INTERVAL,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Create logs directory if it doesn't exist
            Path('logs').mkdir(exist_ok=True)
            
            # Save report with timestamp
            filename = f"logs/monitoring_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2)
                
            logger.info(f"Generated monitoring report: {filename}")
            return report
            
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            return None
