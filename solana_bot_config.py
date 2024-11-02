"""
Trading bot configuration and settings management
"""

import os
from typing import Dict, Any
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class TradingBotConfig:
    def __init__(self):
        self.config_dir = Path('config')
        self.load_all_configs()

    def load_all_configs(self):
        """Load all configuration files"""
        self.trading_config = self._load_trading_config()
        self.tracked_wallets = self._load_tracked_wallets()
        self.token_whitelist = self._load_token_whitelist()

    def _load_trading_config(self) -> Dict[str, Any]:
        """Load main trading configuration"""
        return {
            'max_slippage': float(os.getenv('MAX_SLIPPAGE', '1.0')),
            'min_profit_threshold': float(os.getenv('MIN_PROFIT_THRESHOLD', '1.5')),
            'max_position_size': float(os.getenv('MAX_POSITION_SIZE', '10.0')),
            'stop_loss_percentage': float(os.getenv('STOP_LOSS_PERCENTAGE', '2.0')),
            'take_profit_percentage': float(os.getenv('TAKE_PROFIT_PERCENTAGE', '3.0')),
            'max_trades_per_day': int(os.getenv('MAX_TRADES_PER_DAY', '10')),
            'gas_buffer_sol': float(os.getenv('GAS_BUFFER_SOL', '0.05')),
            'max_daily_exposure': float(os.getenv('MAX_DAILY_EXPOSURE', '20.0')),
            'trailing_stop_activation': float(os.getenv('TRAILING_STOP_ACTIVATION', '2.0')),
            'trailing_stop_distance': float(os.getenv('TRAILING_STOP_DISTANCE', '1.0'))
        }

    def _load_tracked_wallets(self) -> Dict[str, Any]:
        """Load tracked wallets configuration"""
        try:
            with open(self.config_dir / 'tracked-wallets.json', 'r') as f:  # Updated filename
                return json.load(f)
        except FileNotFoundError:
            logger.warning("No tracked wallets config found. Creating default.")
            return {'wallets': [], 'settings': {}}

    def _load_token_whitelist(self) -> Dict[str, Any]:
        """Load token whitelist configuration"""
        try:
            with open(self.config_dir / 'token-whitelist.json', 'r') as f:  # Updated filename
                return json.load(f)
        except FileNotFoundError:
            logger.warning("No token whitelist found. Creating default.")
            return {'tokens': {}, 'settings': {}}

    def update_tracked_wallets(self, wallets: Dict[str, Any]):
        """Update tracked wallets configuration"""
        with open(self.config_dir / 'tracked-wallets.json', 'w') as f:  # Updated filename
            json.dump(wallets, f, indent=4)
        self.tracked_wallets = wallets

    def update_token_whitelist(self, whitelist: Dict[str, Any]):
        """Update token whitelist configuration"""
        with open(self.config_dir / 'token-whitelist.json', 'w') as f:  # Updated filename
            json.dump(whitelist, f, indent=4)
        self.token_whitelist = whitelist

    def get_trading_params(self) -> Dict[str, Any]:
        """Get trading parameters"""
        return self.trading_config

    def get_tracked_wallets(self) -> list:
        """Get list of tracked wallet addresses"""
        return self.tracked_wallets.get('wallets', [])

    def get_whitelisted_tokens(self) -> Dict[str, str]:
        """Get whitelisted token addresses"""
        return self.token_whitelist.get('tokens', {})

    def is_token_whitelisted(self, token_address: str) -> bool:
        """Check if a token is whitelisted"""
        return token_address in self.token_whitelist.get('tokens', {}).values()