# ThetaGang Setup Summary

## Completed Tasks

### 1. ✅ Repository Setup
- Cloned repository from https://github.com/mizbamd/trade-strategies.git
- Repository is ready for paper trading

### 2. ✅ Configuration Updates

#### Paper Trading
- `ibc-config.ini`: Set `TradingMode=paper`
- `thetagang.toml`: Already configured for paper trading (`tradingMode = 'paper'`)

#### Parameters Modified
- **DTE (Days to Expiration)**: Set to 45 days (already configured in `target.dte = 45`)
- **Delta**: Set to 0.30 (already configured in `target.delta = 0.3`)
- **Profit Target**: Changed from 90% to 50% (`roll_when.pnl = 0.5`)

### 3. ✅ 200 Tickers Added
- Generated list of 200 popular tickers including:
  - Major ETFs (SPY, QQQ, IWM, DIA, TLT, GLD, etc.)
  - Large cap tech stocks (AAPL, MSFT, GOOGL, AMZN, META, NVDA, TSLA, etc.)
  - Financials, Healthcare, Consumer, Industrial, Energy, Materials, REITs
  - All tickers configured with equal weights (0.005 each, total = 1.0)
  - Primary exchanges specified where needed (NYSE/NASDAQ)

### 4. ✅ Scanner Scaling
- Updated `option_chains` configuration:
  - `expirations`: Increased from 4 to 6
  - `strikes`: Increased from 15 to 20
- Better coverage for 200 tickers

### 5. ✅ Automated Profit-Taking
- Already implemented via `roll_when.pnl = 0.5`
- Options will automatically roll/close when P&L reaches 50%
- System uses `position_pnl()` to calculate profit percentage

### 6. ✅ Market Regime Detection
- Created new module: `thetagang/market_regime.py`
- Detects market regimes:
  - **Bull**: Positive trend, low VIX (< 20)
  - **Bear**: Negative trend, elevated VIX (> 20)
  - **Sideways**: Low trend, moderate VIX (15-25)
  - **High Volatility**: VIX > 30
- Features:
  - VIX level monitoring
  - SPY trend analysis (20-day MA)
  - Realized volatility calculation
  - Position size adjustment based on regime
  - Delta adjustment based on regime
  - Trading pause in extreme volatility (VIX > 40)
- Integrated into `PortfolioManager.manage()`

## Configuration Files

### thetagang.toml
- **Account**: Configure with your IBKR paper account number
- **Target**: 45 DTE, 30 delta
- **Roll When**: 50% profit target
- **Symbols**: 200 tickers with equal weights
- **Option Chains**: Scaled for 200 tickers (6 expirations, 20 strikes)

### ibc-config.ini
- **TradingMode**: paper
- **IbLoginId**: edemo (paper trading default)
- **IbPassword**: demouser (paper trading default)

## Running the Bot

### Prerequisites
1. Install Python 3.10-3.13
2. Install `uv` package manager
3. Install dependencies: `uv run pip install -e .`
4. Set up IBC (Interactive Brokers Controller)

### Run Command
```bash
uv run thetagang --config thetagang.toml
```

Or with Docker:
```bash
docker run --rm -i --net host \
    -v ~/thetagang:/etc/thetagang \
    brndnmtthws/thetagang:main \
    --config /etc/thetagang/thetagang.toml
```

## Key Features

1. **200 Ticker Portfolio**: Diversified across sectors and asset classes
2. **45 DTE Strategy**: Targets options with 45+ days to expiration
3. **30 Delta**: Writes options at approximately 30 delta (OTM)
4. **50% Profit Taking**: Automatically closes/rolls positions at 50% profit
5. **Market Regime Detection**: Adjusts behavior based on market conditions
6. **Scaled Scanner**: Optimized for scanning 200 tickers

## Next Steps

1. **Update Account Number**: Change `account.number` in `thetagang.toml` to your IBKR paper account
2. **Test in Paper Trading**: Run the bot in paper trading mode first
3. **Monitor Performance**: Check logs and adjust parameters as needed
4. **Gradual Rollout**: Start with fewer tickers if needed, then scale up

## Notes

- The bot will automatically detect market regimes and adjust trading behavior
- In extreme volatility (VIX > 40), trading will pause automatically
- Position sizes and deltas are adjusted based on detected regime
- All 200 tickers are equally weighted (0.5% each)

