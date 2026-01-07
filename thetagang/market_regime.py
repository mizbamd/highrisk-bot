"""
Market Regime Detection Module

This module detects different market regimes (bull, bear, sideways, high volatility)
and adjusts trading behavior accordingly.
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from ib_async import IB, Ticker, util

from thetagang.ibkr import IBKR

log = logging.getLogger(__name__)


class MarketRegime(Enum):
    """Market regime types"""

    BULL = "bull"
    BEAR = "bear"
    SIDEWAYS = "sideways"
    HIGH_VOLATILITY = "high_volatility"
    UNKNOWN = "unknown"


@dataclass
class RegimeMetrics:
    """Market regime metrics"""

    regime: MarketRegime
    vix_level: float
    spy_trend: float  # 20-day moving average trend
    volatility: float  # 30-day realized volatility
    confidence: float  # 0.0 to 1.0


class MarketRegimeDetector:
    """Detects current market regime based on multiple indicators"""

    def __init__(self, ibkr: IBKR, ib: IB):
        self.ibkr = ibkr
        self.ib = ib
        self.current_regime: Optional[RegimeMetrics] = None

    async def detect_regime(self) -> RegimeMetrics:
        """
        Detect current market regime using:
        - VIX level
        - SPY trend (20-day MA)
        - Realized volatility
        - Market momentum
        """
        try:
            # Get VIX
            vix_ticker = await self.ibkr.get_ticker_for_stock("VIX", "")
            vix_level = vix_ticker.marketPrice() if vix_ticker else 20.0

            # Get SPY for trend analysis
            spy_ticker = await self.ibkr.get_ticker_for_stock("SPY", "")
            spy_price = spy_ticker.marketPrice() if spy_ticker else 0.0

            # Get historical data for SPY to calculate trend
            # Using 20-day moving average trend
            try:
                bars = await self.ib.reqHistoricalDataAsync(
                    self.ib.stock("SPY", "SMART", "USD"),
                    "",
                    20,
                    "1 day",
                    "TRADES",
                    0,
                    1,
                    False,
                )
                if bars:
                    recent_prices = [bar.close for bar in bars[-20:]]
                    if len(recent_prices) >= 10:
                        ma_20 = sum(recent_prices[-20:]) / min(20, len(recent_prices))
                        ma_10 = sum(recent_prices[-10:]) / min(10, len(recent_prices))
                        spy_trend = (ma_10 - ma_20) / ma_20 if ma_20 > 0 else 0.0
                    else:
                        spy_trend = 0.0
                else:
                    spy_trend = 0.0
            except Exception as e:
                log.warning(f"Could not calculate SPY trend: {e}")
                spy_trend = 0.0

            # Calculate realized volatility (simplified)
            # In production, you'd want to calculate actual 30-day realized vol
            volatility = abs(spy_trend) * 100  # Simplified proxy

            # Determine regime
            regime = self._classify_regime(vix_level, spy_trend, volatility)
            confidence = self._calculate_confidence(vix_level, spy_trend, volatility)

            metrics = RegimeMetrics(
                regime=regime,
                vix_level=vix_level,
                spy_trend=spy_trend,
                volatility=volatility,
                confidence=confidence,
            )

            self.current_regime = metrics
            log.info(
                f"Market regime detected: {regime.value} "
                f"(VIX={vix_level:.2f}, trend={spy_trend:.2%}, vol={volatility:.2f}, "
                f"confidence={confidence:.2%})"
            )

            return metrics

        except Exception as e:
            log.error(f"Error detecting market regime: {e}")
            # Return default regime
            return RegimeMetrics(
                regime=MarketRegime.UNKNOWN,
                vix_level=20.0,
                spy_trend=0.0,
                volatility=15.0,
                confidence=0.0,
            )

    def _classify_regime(
        self, vix_level: float, spy_trend: float, volatility: float
    ) -> MarketRegime:
        """Classify market regime based on indicators"""

        # High volatility regime
        if vix_level > 30:
            return MarketRegime.HIGH_VOLATILITY

        # Bull market: positive trend, low VIX
        if spy_trend > 0.01 and vix_level < 20:
            return MarketRegime.BULL

        # Bear market: negative trend, elevated VIX
        if spy_trend < -0.01 and vix_level > 20:
            return MarketRegime.BEAR

        # Sideways: low trend, moderate VIX
        if abs(spy_trend) < 0.005 and 15 < vix_level < 25:
            return MarketRegime.SIDEWAYS

        # Default to sideways
        return MarketRegime.SIDEWAYS

    def _calculate_confidence(
        self, vix_level: float, spy_trend: float, volatility: float
    ) -> float:
        """Calculate confidence in regime classification (0.0 to 1.0)"""

        # Higher confidence when indicators are more extreme
        vix_confidence = min(abs(vix_level - 20) / 20, 1.0)
        trend_confidence = min(abs(spy_trend) / 0.02, 1.0)

        # Average the confidences
        confidence = (vix_confidence + trend_confidence) / 2.0
        return min(confidence, 1.0)

    def should_trade(self) -> bool:
        """
        Determine if trading should proceed based on current regime.
        Returns False for extreme conditions.
        """
        if not self.current_regime:
            return True  # Default to trading if regime unknown

        # Don't trade in extreme high volatility
        if (
            self.current_regime.regime == MarketRegime.HIGH_VOLATILITY
            and self.current_regime.vix_level > 40
        ):
            log.warning(
                f"Trading paused: Extreme volatility (VIX={self.current_regime.vix_level:.2f})"
            )
            return False

        return True

    def get_position_size_multiplier(self) -> float:
        """
        Get position size multiplier based on regime.
        Returns a value between 0.0 and 1.0 to scale position sizes.
        """
        if not self.current_regime:
            return 1.0  # Default full size

        regime = self.current_regime.regime

        # Reduce size in high volatility
        if regime == MarketRegime.HIGH_VOLATILITY:
            if self.current_regime.vix_level > 35:
                return 0.5  # 50% size
            elif self.current_regime.vix_level > 30:
                return 0.75  # 75% size

        # Increase size slightly in favorable conditions
        if regime == MarketRegime.BULL and self.current_regime.vix_level < 18:
            return 1.1  # 110% size (with margin)

        # Default full size
        return 1.0

    def get_delta_adjustment(self) -> float:
        """
        Get delta adjustment based on regime.
        Returns adjustment to add/subtract from target delta.
        """
        if not self.current_regime:
            return 0.0

        regime = self.current_regime.regime

        # Use lower delta (more OTM) in high volatility
        if regime == MarketRegime.HIGH_VOLATILITY:
            return -0.05  # Reduce delta by 0.05

        # Use slightly higher delta in bull markets
        if regime == MarketRegime.BULL:
            return 0.02  # Increase delta by 0.02

        return 0.0

