# High-Risk Naked Options Trading Bot

A high-risk trading bot for Interactive Brokers (IBKR) that trades **naked calls and naked puts** around earnings reports using automated option selection and earnings-based expiry strategies.

⚠️ **EXTREME RISK WARNING**: Naked options have **unlimited risk**. This bot is designed for experienced traders with significant capital and risk tolerance.

## 🎯 Strategy Overview

This bot implements an **aggressive naked options strategy** focused on earnings plays:

- **Naked Calls & Naked Puts**: Pure directional plays (no underlying positions)
- **45 DTE Target**: Options with 45 days to expiration
- **Same-Week Expiry**: Selects Friday expiry in the week of earnings reports
- **Small Portfolio**: 5-10 high-volatility symbols for focused exposure
- **Aggressive Profit Targets**: 30% profit target (capture IV crush after earnings)
- **Earnings-Based Expiry**: Automatically selects earnings week expiry when available

### How It Works

1. **Earnings Detection**: Scans for upcoming earnings reports for configured symbols
2. **Same-Week Expiry**: Selects Friday expiry in the earnings week (instead of standard 45 DTE)
3. **IV Expansion Play**: Opens positions 1-2 weeks before earnings to capture IV expansion
4. **Quick Profit Taking**: Takes profit at 30% (more aggressive than wheel strategy)
5. **Naked Options Only**: No stock positions, pure premium collection on direction

## ⚠️ Risk Disclaimer

**EXTREME RISK: Naked options have UNLIMITED RISK and can result in TOTAL LOSS OF CAPITAL.**

### Naked Calls Risk
- **Unlimited upside risk**: If stock moves against you, losses can exceed your entire account
- **No protection**: Unlike covered calls, there's no underlying stock to limit losses
- **Margin calls**: Rapid price moves can trigger margin calls and forced liquidation

### Naked Puts Risk  
- **Maximum loss**: Strike price × 100 shares per contract (if stock goes to $0)
- **Assignment risk**: If put goes ITM, you may be assigned and forced to buy stock
- **Margin requirements**: High margin requirements can tie up significant capital

**Before using this bot:**
- Understand that you can lose **ALL** of your capital
- Ensure you have **excessive capital** to handle worst-case scenarios
- Be prepared for **margin calls** and **forced liquidation**
- **Paper trade first** for at least 6 months before live trading
- Consult with a financial advisor - this is NOT for beginners
- Only trade with money you can **afford to lose completely**

**This strategy is extremely dangerous and can wipe out your account in a single trade.**

## 🚀 Key Features

### Earnings-Based Expiry Selection
- Automatically detects upcoming earnings reports
- Selects same-week Friday expiry for earnings plays
- Falls back to standard 45 DTE if no earnings found

### Market Regime Detection
- Adjusts strategy based on VIX and SPY trends
- Reduces exposure in high volatility (VIX > 40)
- Pauses trading in extreme market conditions

### Premarket Scanner (Optional)
- Scans opportunities during premarket hours (4:00 AM - 9:30 AM ET)
- Parallel processing for fast scanning (5-10 seconds)
- Identifies PUT/CALL opportunities based on premarket price action

### Automated Profit Taking
- 30% profit target (aggressive for earnings plays)
- Automatic position closing at profit target
- Quick exits to avoid IV crush after earnings

### Risk Management
- Position sizing limits (max 15% per symbol)
- Margin usage control (3.0x default for naked options)
- Delta targeting (30 delta for balanced risk/reward)
- Minimum open interest requirements (50+ for liquidity)

## 📋 Requirements

- **Interactive Brokers (IBKR) Account**: Paper trading account for testing
- **Python 3.10-3.13**: Required Python version
- **`uv` Package Manager**: Fast Python package manager ([install](https://docs.astral.sh/uv/))
- **IBC (IBKR Gateway)**: For automated IB Gateway management
- **Significant Capital**: Naked options require substantial margin

### Capital Requirements

**Naked options require MUCH less capital than covered positions**, but still need substantial margin:

- **Naked Put Example**: TSLA $400 Put requires ~$20,000-40,000 in margin (depending on broker)
- **Naked Call Example**: TSLA $400 Call requires ~$15,000-30,000 in margin
- **Account Minimum**: Recommend $50,000+ for small portfolio (5-6 symbols)

**You need MUCH LESS capital than wheel strategy, but still need significant margin capacity.**

## 🔧 Installation

### 1. Clone Repository

```bash
git clone https://github.com/mizbamd/highrisk-bot.git
cd highrisk-bot
```

### 2. Install Dependencies

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv run pip install -e .
```

### 3. Configure Bot

Edit `high-risk-bot.toml`:

```toml
[account]
number = "YOUR_ACCOUNT_NUMBER"  # Your IBKR account number

[high_risk]
enable_earnings_expiry = true  # Enable earnings-based expiry
days_before_earnings = 10      # Open positions 10 days before ER
max_position_per_symbol = 0.15 # Max 15% per symbol

[symbols]
  # Configure your 5-10 symbols
  [symbols.TSLA]
  weight = 0.20
  primary_exchange = "NASDAQ"
  
  [symbols.NVDA]
  weight = 0.20
  primary_exchange = "NASDAQ"
  
  # ... add more symbols
```

### 4. Configure IB Gateway

Edit `ibc-config.ini`:

```ini
TradingMode=paper  # Start with paper trading!
IbLoginId=your_username
IbPassword=your_password
```

## 📖 Usage

### Dry Run (Test Configuration)

```bash
uv run thetagang --config high-risk-bot.toml --dry-run
```

This validates your configuration without executing trades.

### Paper Trading

```bash
# Start IB Gateway first, then:
uv run thetagang --config high-risk-bot.toml
```

### Without IBC (Manual Gateway)

If you're running IB Gateway manually:

```bash
uv run thetagang --config high-risk-bot.toml --without-ibc
```

## ⚙️ Configuration

### High-Risk Bot Settings

```toml
[high_risk]
enable_earnings_expiry = true      # Use earnings-based expiry
days_before_earnings = 10          # Open positions 10 days before ER
close_before_earnings = false      # Close positions 1 day before ER
max_position_per_symbol = 0.15     # Max 15% buying power per symbol

[target]
dte = 45                           # Target 45 DTE (or earnings week)
delta = 0.3                        # 30 delta for naked options
maximum_new_contracts_percent = 0.10  # Max 10% buying power per trade
minimum_open_interest = 50         # Higher OI for earnings plays

[roll_when]
pnl = 0.3                          # Take profit at 30%
dte = 5                            # Roll at 5 DTE (closer to earnings)
```

### Account Settings

```toml
[account]
number = "YOUR_ACCOUNT_NUMBER"
margin_usage = 3.0  # Use 3x margin for naked options (HIGH RISK!)
```

### Symbol Configuration

```toml
[symbols]
  [symbols.TSLA]
  weight = 0.20              # 20% of portfolio
  primary_exchange = "NASDAQ"
  
  [symbols.NVDA]
  weight = 0.20              # 20% of portfolio
  primary_exchange = "NASDAQ"
```

**Total weights must sum to 1.0 (100%)**

## 📊 Earnings Detection

The bot includes an earnings detector module that:

- Detects upcoming earnings reports for configured symbols
- Calculates same-week Friday expiry dates
- Integrates with option chain selection

**⚠️ Note**: Earnings data source integration is required. Currently, `get_earnings_date()` returns `None` and needs implementation with an earnings API:

- **Alpha Vantage**: Free tier available
- **Polygon.io**: Real-time earnings data
- **Yahoo Finance**: Scraping (less reliable)
- **IBKR Fundamentals**: May require additional data subscriptions

To implement earnings detection, modify `thetagang/earnings_detector.py`:

```python
def get_earnings_date(self, symbol: str) -> Optional[datetime]:
    # TODO: Integrate with earnings API
    # Example: Alpha Vantage, Polygon.io, etc.
    return None
```

## 🎯 Strategy Examples

### High Volatility Tech Stocks

```toml
[symbols]
  [symbols.TSLA]   # Tesla - high volatility
  weight = 0.25
  primary_exchange = "NASDAQ"
  
  [symbols.NVDA]   # NVIDIA - AI momentum
  weight = 0.25
  primary_exchange = "NASDAQ"
  
  [symbols.AMD]    # AMD - semi momentum
  weight = 0.20
  primary_exchange = "NASDAQ"
  
  [symbols.AAPL]   # Apple - stable with ER plays
  weight = 0.15
  primary_exchange = "NASDAQ"
  
  [symbols.MSFT]   # Microsoft - enterprise focus
  weight = 0.15
  primary_exchange = "NASDAQ"
```

### Earnings Play Configuration

```toml
[high_risk]
enable_earnings_expiry = true
days_before_earnings = 10      # Open 10 days before ER
close_before_earnings = false  # Hold through earnings (HIGH RISK!)

[roll_when]
pnl = 0.3                      # Take profit quickly (IV crush after ER)
dte = 5                        # Close at 5 DTE to avoid ER
```

## ⚡ Performance Considerations

### Premarket Scanner Performance
- **Parallel Processing**: Scans all symbols concurrently
- **Speed**: 5-10 seconds for 20 symbols (vs 80-200 seconds sequential)
- **Single-Shot Timing**: Checks premarket hours once before scanning
- **Safety Checks**: Validates timing before and after scan

### Market Regime Detection
- Adjusts delta and position sizing based on VIX/SPY trends
- Pauses trading in extreme volatility (VIX > 40)
- Reduces exposure in bear markets

## 🛡️ Risk Management Features

### Position Sizing
- **Max per Symbol**: 15% of buying power (configurable)
- **Max per Trade**: 10% of buying power
- **Portfolio Limits**: Total allocation capped at configured weights

### Margin Management
- **Margin Usage**: 3.0x default (adjust based on risk tolerance)
- **Buffer Cushion**: IB will start closing positions if margin drops too low
- **Monitor Closely**: Naked options can require margin adjustments quickly

### Delta Targeting
- **30 Delta**: Balance of premium vs risk
- **OTM Strikes**: Out-of-the-money for directional plays
- **Regime Adjustment**: Delta adjusts based on market conditions

### Profit Targets
- **30% Profit Target**: More aggressive than wheel strategy
- **Quick Exits**: Capture IV crush after earnings
- **Risk Reduction**: Close positions before major earnings events (optional)

## 📝 Example Trade Flow

### Earnings Play Example: TSLA

```
Week 1 (10 days before earnings):
- Earnings detector finds TSLA ER in 10 days
- Bot selects Friday expiry of ER week (e.g., Jan 31, 2025)
- Stock is down 5% (RED) → Sell naked PUT
- Strike: $380 (0.30 delta, 45 DTE)
- Premium: $1,500 per contract

Week 2 (3 days before earnings):
- Put now worth $1,050 (down 30%)
- Profit: $450 (30% of premium)
- Action: BUY TO CLOSE at 30% profit target
- Result: Profit realized, avoid ER volatility

OR (if still holding):

Earnings Week:
- TSLA beats earnings, stock up 10%
- Put expires worthless
- Result: Keep full $1,500 premium (100% profit)
```

## 🔍 Monitoring

### Log Files

```bash
# Check bot execution logs
tail -f ib_async.log

# Check IBC gateway logs
tail -f ibc.log
```

### Key Metrics to Monitor

- **Total Margin Used**: Watch for margin calls
- **Profit Targets Hit**: Track win rate
- **Earnings Dates**: Verify earnings detection working
- **Position Sizes**: Ensure within limits
- **Market Regime**: Check VIX/SPY trends

## 🐛 Troubleshooting

### No Earnings Dates Found

**Problem**: Bot doesn't find earnings dates

**Solution**: 
1. Implement earnings data source (Alpha Vantage, Polygon, etc.)
2. Check earnings detector logs
3. Bot will fall back to standard 45 DTE if no earnings found

### Margin Calls

**Problem**: IBKR sending margin call warnings

**Solution**:
1. Reduce `margin_usage` (e.g., 2.0 instead of 3.0)
2. Reduce position sizes (`max_position_per_symbol`)
3. Close some positions manually
4. Add more capital to account

### No Contracts Found

**Problem**: Bot can't find suitable contracts

**Solution**:
1. Check `minimum_open_interest` (increase if too high)
2. Verify symbols have liquid options
3. Adjust `target.delta` (try 0.35 or 0.25)
4. Check market hours (options may be unavailable)

## 📚 Additional Resources

- **IBKR API Documentation**: https://interactivebrokers.github.io/tws-api/
- **Options Education**: https://www.optionseducation.org/
- **ThetaGang Strategy**: https://www.reddit.com/r/thetagang/
- **Earnings Calendars**: 
  - https://www.earningswhispers.com/
  - https://www.zacks.com/stock/research/earnings-calendar

## ⚖️ License

This project is licensed under the AGPL-3.0 license. See [LICENSE](LICENSE) for details.

## 🚨 Final Warning

**This bot trades NAKED OPTIONS with UNLIMITED RISK.**

- You can lose **ALL** of your capital in a single trade
- Margin calls can force liquidation
- Market gaps can cause massive losses overnight
- **Only trade with money you can afford to lose completely**
- **Paper trade extensively before live trading**
- **This is NOT for beginners or casual traders**

**Use at your own risk. The authors are not responsible for any losses.**

---

**Repository**: [https://github.com/mizbamd/highrisk-bot](https://github.com/mizbamd/highrisk-bot)

**Status**: Active development - Earnings detection integration in progress
