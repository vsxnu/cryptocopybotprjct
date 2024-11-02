"""
Solana Copy Trading Bot Package
"""

from .solana_wallet_finder import SolanaWalletFinder
from .solana_trade_bot import SolanaTradingBot
from .solana_bot_config import TradingBotConfig

__version__ = '0.1.0'
__all__ = ['SolanaWalletFinder', 'SolanaTradingBot', 'TradingBotConfig']
