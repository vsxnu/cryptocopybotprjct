"""
Enhanced wallet finder module for discovering profitable wallets based on real-time analysis
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
    MIN_PROFIT_TRADE, ANALYSIS_PERIOD_DAYS
)

logger = logging.getLogger(__name__)

class WalletFinder:
    def __init__(self, research_mode=False):
        self.solana_client = Client(SOLANA_RPC_URL)
        self.research_mode = research_mode
        self.discovered_wallets = {}
        self.trending_pairs = {}
        
    async def _fetch_dexscreener_trending(self):
        """Fetch trending pairs from DexScreener"""
        try:
            logger.info("\n" + "="*80)
            logger.info("FETCHING TRENDING PAIRS FROM DEXSCREENER")
            logger.info("="*80)
            
            async with aiohttp.ClientSession() as session:
                url = "https://api.dexscreener.com/token-profiles/latest/v1"
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Filter for Solana tokens
                        solana_pairs = [token for token in data if token.get('chainId') == 'solana']
                        
                        if self.research_mode:
                            logger.info(f"\nFound {len(solana_pairs)} Solana tokens:")
                            logger.info("-"*80)
                            
                            for idx, token in enumerate(solana_pairs, 1):
                                logger.info(f"\n{idx}. Token Details:")
                                logger.info(f"   Address: {token.get('tokenAddress')}")
                                logger.info(f"   URL: {token.get('url')}")
                                if token.get('description'):
                                    logger.info(f"   Description: {token.get('description')}")
                                
                                # Log links if available
                                if 'links' in token:
                                    logger.info("   Links:")
                                    for link in token['links']:
                                        link_type = link.get('type', link.get('label', 'link'))
                                        logger.info(f"      {link_type}: {link.get('url')}")
                                
                                # Get detailed pair information
                                pair_url = f"https://api.dexscreener.com/latest/dex/tokens/{token.get('tokenAddress')}"
                                async with session.get(pair_url) as pair_response:
                                    if pair_response.status == 200:
                                        pair_data = await pair_response.json()
                                        if 'pairs' in pair_data:
                                            logger.info("\n   Trading Information:")
                                            for pair in pair_data['pairs'][:3]:  # Show top 3 pairs
                                                logger.info(f"      DEX: {pair.get('dexId')}")
                                                logger.info(f"      Pair: {pair.get('baseToken', {}).get('symbol')}/{pair.get('quoteToken', {}).get('symbol')}")
                                                logger.info(f"      Price: ${pair.get('priceUsd', 'Unknown')}")
                                                logger.info(f"      24h Volume: {pair.get('volume', {}).get('h24', 'Unknown')}")
                                                logger.info(f"      Liquidity: {pair.get('liquidity', {}).get('usd', 'Unknown')}")
                                                
                                                # Get transaction counts
                                                txns = pair.get('txns', {}).get('h24', {})
                                                if txns:
                                                    logger.info(f"      24h Transactions: {txns.get('buys', 0)} buys, {txns.get('sells', 0)} sells")
                                await asyncio.sleep(0.5)  # Rate limiting
                            
                            return solana_pairs
                        
                        return solana_pairs
                    else:
                        logger.error(f"DexScreener API error: {response.status}")
                        logger.error(f"Response: {await response.text()}")
                        return []
        except Exception as e:
            logger.error(f"Error fetching trending pairs: {str(e)}")
            return []

    async def find_profitable_wallets(self):
        """Find profitable wallets based on recent trading activity"""
        logger.info("\n" + "="*80)
        logger.info("STARTING ENHANCED SOLANA WALLET DISCOVERY")
        logger.info("="*80)
        logger.info("\nStep 1: Fetching trending pairs...")
        
        # Get trending pairs
        trending_pairs = await self._fetch_dexscreener_trending()
        self.trending_pairs = {pair.get('tokenAddress'): pair for pair in trending_pairs}
        
        logger.info("\nStep 2: Analyzing trading activity...")
        discovered_wallets = {}
        
        # Save research results
        self._save_research_results(discovered_wallets)
        
        return list(discovered_wallets.values())

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
                    'analysis_period_days': ANALYSIS_PERIOD_DAYS
                }
            }
            
            # Create logs directory if it doesn't exist
            Path('logs').mkdir(exist_ok=True)
            
            # Save to file with timestamp
            filename = f"logs/research_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(research_data, f, indent=2, default=str)
            
            logger.info(f"\nDetailed research results saved to: {filename}")
            
        except Exception as e:
            logger.error(f"Error saving research results: {str(e)}")
