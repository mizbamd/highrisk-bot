"""
Premarket Scanner Module

Scans for trading opportunities during premarket hours (4:00 AM - 9:30 AM ET)
and prepares trades for execution when market opens.
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

import exchange_calendars as xcals
import pandas as pd
from ib_async import Contract, Option, Stock, Ticker
from rich import box
from rich.table import Table

from thetagang import log
from thetagang.config import Config
from thetagang.ibkr import IBKR

logger = logging.getLogger(__name__)


class PremarketScanner:
    """Scans for premarket trading opportunities"""

    # Premarket hours: 4:00 AM - 9:30 AM ET (regular market open)
    PREMARKET_START_HOUR = 4  # 4:00 AM ET
    PREMARKET_START_MINUTE = 0
    PREMARKET_END_HOUR = 9  # 9:30 AM ET
    PREMARKET_END_MINUTE = 30

    def __init__(self, config: Config, ibkr: IBKR):
        self.config = config
        self.ibkr = ibkr
        self.scan_results: Dict[str, Dict] = {}

    def is_premarket_hours(self) -> bool:
        """
        Check if current time is within premarket hours (4:00 AM - 9:30 AM ET)
        """
        try:
            calendar = xcals.get_calendar(self.config.exchange_hours.exchange)
            now_utc = datetime.now(tz=timezone.utc)
            
            # Convert to ET (America/New_York timezone)
            # Premarket: 4:00 AM - 9:30 AM ET
            # Use pandas timezone handling (already a dependency)
            now_et_ts = pd.Timestamp(now_utc).tz_convert("America/New_York")
            if pd.isna(now_et_ts) or now_et_ts is pd.NaT:
                log.warning("Failed to convert time to ET timezone")
                return False
            
            now_et: datetime = now_et_ts.to_pydatetime()
            
            # Check if it's a trading day
            today = now_et.date()
            is_session = calendar.is_session(today)  # type: ignore
            if not bool(is_session):
                return False
            
            # Premarket hours: 4:00 AM - 9:30 AM ET
            premarket_start = now_et.replace(
                hour=self.PREMARKET_START_HOUR,
                minute=self.PREMARKET_START_MINUTE,
                second=0,
                microsecond=0
            )
            
            regular_open = calendar.session_open(today)  # type: ignore
            # Convert to ET for comparison - regular_open is timezone-aware
            regular_open_et_ts = pd.Timestamp(regular_open).tz_convert("America/New_York")
            if pd.isna(regular_open_et_ts) or regular_open_et_ts is pd.NaT:
                log.warning("Failed to convert regular open time to ET timezone")
                return False
            
            regular_open_et: datetime = regular_open_et_ts.to_pydatetime()
            
            # Check if we're between 4:00 AM ET and market open (9:30 AM ET)
            if premarket_start <= now_et < regular_open_et:
                return True
                
            return False
        except Exception as e:
            log.warning(f"Error checking premarket hours: {e}")
            return False

    async def scan_symbol(self, symbol: str, primary_exchange: str = "") -> Optional[Dict]:
        """
        Scan a single symbol for premarket opportunities
        
        Returns dict with:
        - symbol: ticker symbol
        - current_price: current premarket price
        - volume: premarket volume
        - price_change_pct: price change from previous close
        - has_opportunity: bool indicating if opportunity exists
        - recommended_action: 'PUT' or 'CALL' or None
        """
        try:
            # Get stock contract
            stock_contract = Stock(symbol, "SMART", "USD", primaryExchange=primary_exchange)
            qualified = await self.ibkr.qualify_contracts(stock_contract)
            
            if not qualified:
                log.warning(f"Could not qualify contract for {symbol}")
                return None
            
            contract = qualified[0]
            
            # Get ticker for premarket data
            ticker = await self.ibkr.get_ticker_for_contract(contract)
            
            if not ticker:
                log.warning(f"Could not get ticker for {symbol}")
                return None
            
            # Get premarket data
            current_price = ticker.marketPrice() if hasattr(ticker, 'marketPrice') else 0.0
            close_price = ticker.close if hasattr(ticker, 'close') and not pd.isna(ticker.close) else 0.0
            
            # Calculate price change
            price_change_pct = 0.0
            if close_price > 0:
                price_change_pct = ((current_price - close_price) / close_price) * 100
            
            # Get volume (if available in premarket)
            volume = getattr(ticker, 'volume', 0)
            
            # Determine opportunity based on price action
            # If stock is down in premarket, consider selling puts
            # If stock is up significantly, consider selling calls (if we own shares)
            has_opportunity = False
            recommended_action = None
            
            symbol_config = self.config.symbols.get(symbol)
            if symbol_config:
                # Check if stock is "red" (down) - opportunity for puts
                if price_change_pct < -1.0:  # Down more than 1%
                    if (
                        symbol_config.puts is None
                        or symbol_config.puts.write_when is None
                        or symbol_config.puts.write_when.red is True
                    ):
                        has_opportunity = True
                        recommended_action = "PUT"
                
                # Check if stock is "green" (up) - opportunity for calls (if we have shares)
                elif price_change_pct > 1.0:  # Up more than 1%
                    if (
                        symbol_config.calls is None
                        or symbol_config.calls.write_when is None
                        or symbol_config.calls.write_when.green is True
                    ):
                        has_opportunity = True
                        recommended_action = "CALL"
            
            result = {
                "symbol": symbol,
                "current_price": current_price,
                "close_price": close_price,
                "price_change_pct": price_change_pct,
                "volume": volume,
                "has_opportunity": has_opportunity,
                "recommended_action": recommended_action,
                "timestamp": datetime.now(tz=timezone.utc),
            }
            
            self.scan_results[symbol] = result
            return result
            
        except Exception as e:
            logger.exception(f"Error scanning {symbol}: {e}")
            return None

    async def scan_all_symbols(self) -> Dict[str, Dict]:
        """
        Scan all configured symbols for premarket opportunities in parallel
        
        Returns dict of scan results keyed by symbol
        """
        if not self.is_premarket_hours():
            log.info("Not in premarket hours, skipping scan")
            return {}
        
        log.info("Starting premarket scan (parallel processing)...")
        symbols = list(self.config.symbols.keys())
        total_symbols = len(symbols)
        
        if total_symbols == 0:
            log.warning("No symbols configured for premarket scanning")
            return {}
        
        log.info(f"Scanning {total_symbols} symbols in parallel...")
        
        # Create parallel tasks for all symbols
        tasks = []
        symbol_configs = {}
        
        for symbol in symbols:
            symbol_config = self.config.symbols[symbol]
            primary_exchange = getattr(symbol_config, 'primary_exchange', '')
            symbol_configs[symbol] = primary_exchange
            
            # Create async task for each symbol
            tasks.append(self.scan_symbol(symbol, primary_exchange))
        
        # Execute all scans in parallel
        # return_exceptions=True ensures one failure doesn't break the entire scan
        start_time = datetime.now(tz=timezone.utc)
        
        # Safety check: Verify we're still in premarket before starting scan
        # This captures timing in a "single shot" at scan start
        if not self.is_premarket_hours():
            log.warning("Premarket hours expired before scan started, aborting")
            return {}
        
        # Get market open time to calculate time remaining
        # This provides visibility into how much time we have before market open
        try:
            calendar = xcals.get_calendar(self.config.exchange_hours.exchange)
            now_utc = datetime.now(tz=timezone.utc)
            now_et_ts = pd.Timestamp(now_utc).tz_convert("America/New_York")
            if pd.isna(now_et_ts) or now_et_ts is pd.NaT:
                pass  # Could not determine current ET time
            else:
                today = now_et_ts.date()
                regular_open = calendar.session_open(today)  # type: ignore
                regular_open_et_ts = pd.Timestamp(regular_open).tz_convert("America/New_York")
                if not pd.isna(regular_open_et_ts) and regular_open_et_ts is not pd.NaT:
                    market_open_et = regular_open_et_ts.to_pydatetime()
                    now_et = now_et_ts.to_pydatetime()
                    time_until_open = (market_open_et - now_et).total_seconds()
                    if time_until_open > 0:
                        log.info(
                            f"Market opens in {time_until_open/60:.1f} minutes "
                            f"at {market_open_et.strftime('%H:%M')} ET"
                        )
        except Exception:
            pass  # Could not calculate market open time (non-critical)
        
        # Run parallel scan
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = datetime.now(tz=timezone.utc)
        
        # Calculate elapsed time
        elapsed = (end_time - start_time).total_seconds()
        
        # Safety check: Verify we're still in premarket after scan completes
        # This ensures we didn't accidentally run past market open
        if not self.is_premarket_hours():
            log.warning(
                f"Premarket hours expired during scan (took {elapsed:.1f}s). "
                f"Results may be incomplete or inaccurate."
            )
            # Continue processing results anyway - better to have partial data than none
        
        # Process results and filter out errors/None values
        scan_results = {}
        successful_scans = 0
        failed_scans = 0
        
        for i, result in enumerate(results):
            symbol = symbols[i]
            
            if isinstance(result, Exception):
                log.warning(f"Error scanning {symbol}: {result}")
                failed_scans += 1
            elif result is not None:
                scan_results[symbol] = result
                successful_scans += 1
            else:
                log.info(f"No result for {symbol}")
                failed_scans += 1
        
        self.scan_results = scan_results
        
        log.info(
            f"Premarket scan completed in {elapsed:.2f}s: "
            f"{successful_scans}/{total_symbols} successful, "
            f"{failed_scans} failed"
        )
        
        return scan_results

    def get_opportunities_summary(self) -> Table:
        """
        Create a summary table of premarket opportunities
        """
        table = Table(
            title="Premarket Scanner Results",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold magenta",
        )
        
        table.add_column("Symbol", style="cyan", no_wrap=True)
        table.add_column("Current Price", justify="right", style="green")
        table.add_column("Prev Close", justify="right")
        table.add_column("Change %", justify="right")
        table.add_column("Volume", justify="right")
        table.add_column("Action", style="yellow")
        
        opportunities = [
            r for r in self.scan_results.values() if r.get("has_opportunity", False)
        ]
        
        if not opportunities:
            table.add_row("No opportunities found", "", "", "", "", "")
        else:
            for result in sorted(opportunities, key=lambda x: abs(x.get("price_change_pct", 0)), reverse=True):
                change_pct = result.get("price_change_pct", 0)
                change_color = "red" if change_pct < 0 else "green"
                
                table.add_row(
                    result.get("symbol", ""),
                    f"${result.get('current_price', 0):.2f}",
                    f"${result.get('close_price', 0):.2f}",
                    f"[{change_color}]{change_pct:+.2f}%[/{change_color}]",
                    f"{result.get('volume', 0):,}",
                    result.get("recommended_action", ""),
                )
        
        return table

    async def get_top_opportunities(self, limit: int = 10) -> List[Dict]:
        """
        Get top N opportunities sorted by price change magnitude
        
        Args:
            limit: Maximum number of opportunities to return
            
        Returns:
            List of opportunity dicts
        """
        opportunities = [
            r for r in self.scan_results.values() if r.get("has_opportunity", False)
        ]
        
        # Sort by absolute price change (descending)
        opportunities.sort(
            key=lambda x: abs(x.get("price_change_pct", 0)), reverse=True
        )
        
        return opportunities[:limit]

