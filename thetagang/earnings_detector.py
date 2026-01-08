"""
Earnings Report Detector Module

Detects upcoming earnings reports and selects same-week expiry options
for high-risk naked calls/puts trading around earnings events.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple

import pandas as pd
from ib_async import Contract

from thetagang import log
from thetagang.config import Config
from thetagang.ibkr import IBKR

logger = logging.getLogger(__name__)


class EarningsDetector:
    """Detects upcoming earnings reports and calculates same-week expiry dates"""

    def __init__(self, config: Config, ibkr: IBKR):
        self.config = config
        self.ibkr = ibkr
        self.earnings_cache: Dict[str, Dict] = {}

    def get_earnings_date(self, symbol: str) -> Optional[datetime]:
        """
        Get the next earnings report date for a symbol.
        
        This is a placeholder - in production, you would:
        1. Use an earnings API (Alpha Vantage, Polygon, etc.)
        2. Scrape earnings calendars
        3. Use IBKR fundamental data
        
        Returns:
            datetime of next earnings report, or None if not found
        """
        # TODO: Implement actual earnings data fetching
        # For now, return None (will need external data source)
        return None

    def get_same_week_expiry(self, earnings_date: datetime, target_dte: int = 45) -> Optional[str]:
        """
        Calculate the same-week expiry date for options around earnings.
        
        Strategy: Find the Friday expiry in the same week as earnings.
        If earnings is on Friday, use that week's expiry.
        If earnings is earlier in the week, use that week's Friday expiry.
        
        Args:
            earnings_date: Date of earnings report
            target_dte: Target days to expiration (default 45)
            
        Returns:
            Expiry date string in format 'YYYYMMDD', or None
        """
        try:
            # Get the Friday of the earnings week
            # Monday = 0, Friday = 4
            days_until_friday = (4 - earnings_date.weekday()) % 7
            if days_until_friday == 0 and earnings_date.weekday() == 4:
                # Earnings is on Friday, use that Friday
                expiry_date = earnings_date
            else:
                # Get the Friday of the earnings week
                expiry_date = earnings_date + timedelta(days=days_until_friday)
            
            # Format as YYYYMMDD for IBKR
            expiry_str = expiry_date.strftime("%Y%m%d")
            
            # Verify it's approximately target_dte days out
            days_diff = (expiry_date - datetime.now(timezone.utc).date()).days
            if abs(days_diff - target_dte) > 7:  # Allow 7 day variance
                log.warning(
                    f"Expiry {expiry_str} is {days_diff} days out, "
                    f"target was {target_dte} days"
                )
            
            return expiry_str
            
        except Exception as e:
            logger.exception(f"Error calculating same-week expiry: {e}")
            return None

    async def get_earnings_expiry_for_symbol(self, symbol: str) -> Optional[str]:
        """
        Get the same-week expiry date for a symbol's upcoming earnings.
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            Expiry date string (YYYYMMDD) or None
        """
        # Check cache first
        if symbol in self.earnings_cache:
            cache_entry = self.earnings_cache[symbol]
            if cache_entry.get("expiry_date"):
                return cache_entry["expiry_date"]
        
        # Get earnings date
        earnings_date = self.get_earnings_date(symbol)
        if not earnings_date:
            log.debug(f"No earnings date found for {symbol}")
            return None
        
        # Calculate same-week expiry
        expiry_str = self.get_same_week_expiry(earnings_date, target_dte=45)
        
        # Cache result
        if expiry_str:
            self.earnings_cache[symbol] = {
                "earnings_date": earnings_date,
                "expiry_date": expiry_str,
                "cached_at": datetime.now(timezone.utc),
            }
        
        return expiry_str

    def is_earnings_week(self, symbol: str) -> bool:
        """
        Check if we're currently in the earnings week for a symbol.
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            True if we're in the earnings week, False otherwise
        """
        if symbol not in self.earnings_cache:
            return False
        
        cache_entry = self.earnings_cache[symbol]
        earnings_date = cache_entry.get("earnings_date")
        
        if not earnings_date:
            return False
        
        # Check if earnings is within the next 7 days
        now = datetime.now(timezone.utc).date()
        earnings_date_only = earnings_date.date() if isinstance(earnings_date, datetime) else earnings_date
        
        days_until_earnings = (earnings_date_only - now).days
        return 0 <= days_until_earnings <= 7

    async def get_all_earnings_expiries(self, symbols: List[str]) -> Dict[str, str]:
        """
        Get same-week expiry dates for all symbols with upcoming earnings.
        
        Args:
            symbols: List of stock ticker symbols
            
        Returns:
            Dict mapping symbol to expiry date string (YYYYMMDD)
        """
        expiries = {}
        
        for symbol in symbols:
            expiry = await self.get_earnings_expiry_for_symbol(symbol)
            if expiry:
                expiries[symbol] = expiry
                log.info(f"{symbol}: Earnings expiry = {expiry}")
        
        return expiries

