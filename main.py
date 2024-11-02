"""
Main entry point for the Solana trading bot
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
import sys
import argparse

# Configure logging
log_dir = Path('logs')
log_dir.mkdir(exist_ok=True)
log_file = log_dir / f'trading_bot_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'

# Configure logging to both file and console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def setup_argument_parser():
    """Setup command line argument parser"""
    parser = argparse.ArgumentParser(description='Solana Trading Bot')
    parser.add_argument(
        '--mode',
        type=str,
        choices=['research', 'execute'],
        required=True,
        help='Operating mode: research (analysis only) or execute (perform trades)'
    )
    return parser

# Import bot modules
from solana_wallet_finder import WalletFinder
from solana_trade_bot import SolanaTradingBot

async def research_mode():
    """Run in research mode - analyze and log findings only"""
    logger.info("Starting in RESEARCH mode...")
    logger.info("This mode will analyze trading patterns and log findings without executing trades")
    
    try:
        # Initialize wallet finder in research mode
        wallet_finder = WalletFinder(research_mode=True)
        
        # Find and analyze profitable wallets
        logger.info("Beginning wallet analysis...")
        profitable_wallets = await wallet_finder.find_profitable_wallets()
        
        logger.info("Research completed successfully")
        logger.info(f"Results have been saved to the logs directory")
        
    except Exception as e:
        logger.exception("Error during research mode execution")
        raise e

async def execute_mode():
    """Run in execute mode - perform actual trading"""
    logger.info("Starting in EXECUTE mode...")
    logger.info("This mode will perform actual trading based on analysis")
    
    try:
        # Initialize wallet finder
        logger.info("Initializing wallet finder...")
        wallet_finder = WalletFinder(research_mode=False)
        
        # Find profitable wallets
        profitable_wallets = await wallet_finder.find_profitable_wallets()
        
        if not profitable_wallets:
            logger.warning("No profitable wallets found to copy. Exiting...")
            return
        
        # Initialize trading bot with discovered wallets
        logger.info("Initializing trading bot...")
        trading_bot = SolanaTradingBot()
        
        # Run the bot
        await trading_bot.run()
        
    except Exception as e:
        logger.exception("Error during execute mode operation")
        raise e

async def main():
    """Main entry point"""
    # Parse command line arguments
    parser = setup_argument_parser()
    args = parser.parse_args()
    
    # Log startup information
    logger.info("=" * 60)
    logger.info("Solana Trading Bot Starting")
    logger.info("=" * 60)
    logger.info(f"Mode: {args.mode.upper()}")
    logger.info(f"Log file: {log_file}")
    logger.info(f"Log level: {logging.getLevelName(logging.getLogger().getEffectiveLevel())}")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Working directory: {Path.cwd()}")
    logger.info("-" * 60)
    
    try:
        if args.mode == 'research':
            await research_mode()
        else:  # execute mode
            await execute_mode()
            
    except KeyboardInterrupt:
        logger.info("Shutting down gracefully...")
    except Exception as e:
        logger.exception("Fatal error occurred")
        raise e
    finally:
        logger.info("Bot shutdown complete")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
