"""
Global rate limiter for RPC requests
"""

import time
import asyncio
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class GlobalRateLimiter:
    _instance: Optional['GlobalRateLimiter'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GlobalRateLimiter, cls).__new__(cls)
            cls._instance.last_request = 0
            cls._instance.min_interval = 5.0  # 5 seconds between requests
            cls._instance.backoff_time = 5  # Initial backoff time
        return cls._instance

    async def wait(self):
        """Wait for global rate limit"""
        current_time = time.time()
        elapsed = current_time - self.last_request
        if elapsed < self.min_interval:
            delay = self.min_interval - elapsed
            logger.debug(f"Rate limiting: waiting {delay:.2f}s")
            await asyncio.sleep(delay)
        self.last_request = time.time()

    async def handle_429(self):
        """Handle rate limit error with exponential backoff"""
        await asyncio.sleep(self.backoff_time)
        self.backoff_time = min(self.backoff_time * 2, 60)  # Max 60 seconds
        logger.info(f"Rate limit hit, backing off for {self.backoff_time}s")

    def reset_backoff(self):
        """Reset backoff time after successful request"""
        self.backoff_time = 5
