# ThetaGang Trading Bot - Complete Strategy Guide

## 📋 Overview

**Strategy**: The Wheel Strategy with Cash-Secured Puts and Covered Calls
**Objective**: Generate income through options premium while potentially acquiring stocks at a discount

---

## 🎯 Your Configuration Summary

### Account Settings
- **Account**: DUO840569 (Paper Trading)
- **Margin Usage**: 50% of Net Liquidation Value
- **Trading Hours**: 9:30 AM - 4:00 PM ET (no delays)
- **Market Behavior**: Wait for market open (up to 1 hour)

### Target Parameters
- **Days to Expiration (DTE)**: 45-180 days
- **Delta**: 0.30 (30 delta)
- **Profit Target**: 50% of premium received
- **Maximum New Contracts**: 5% of buying power per trade

### Portfolio
- **20 Tickers** at 5% weight each:
  - **Tech/Growth**: TSLA, AMZN, NFLX, SHOP, COIN, UPST
  - **Quantum Computing**: QBTS, QUBT, RGTI
  - **Materials/Mining**: MP, ALB, EGO, NAK, TMC, CRML
  - **Real Estate/Auto**: OPEN, CVNA
  - **Retail**: WMT
  - **Biotech**: VOYG
  - **EV/Battery**: QS

---

## 📥 ENTRY STRATEGIES

### 1. **Selling Cash-Secured Puts (CSP)**

**When**: When you DON'T own the stock and want to either:
- Generate income from premium
- Acquire the stock at a lower price

**Conditions to Write Puts**:
```toml
[write_when.puts]
red = true      # Write puts when stock is DOWN (below recent average)
green = false   # Don't write puts when stock is UP
```

**Entry Criteria**:
- Stock must be trading BELOW its 30-day moving average ("red")
- Find put option with:
  - **DTE**: 45-180 days
  - **Delta**: ≤ 0.30 (30% probability of being ITM)
  - **Minimum Credit**: $0.05 per contract
  - **Open Interest**: ≥ 10 contracts

**Example Entry - TSLA Put**:
```
Current TSLA Price: $400
30-Day Average: $420 (stock is "red" - down trend)
Account NLV: $100,000
Buying Power: $50,000 (50% margin usage)
TSLA Allocation: 5% = $2,500

Action: Sell 1 TSLA Put
Strike: $360 (0.30 delta, ~10% below current price)
Expiration: 45 days out
Premium Received: $800 ($8.00 per share × 100)

Capital Required: $36,000 (cash-secured)
Immediate Income: $800 (2.2% return in 45 days if expires worthless)
Annualized Return: ~18% on capital
```

### 2. **Selling Covered Calls**

**When**: When you OWN 100+ shares of the stock

**Conditions to Write Calls**:
```toml
[write_when.calls]
green = true    # Write calls when stock is UP (above recent average)
red = false     # Don't write calls when stock is DOWN
```

**Entry Criteria**:
- Stock must be trading ABOVE its 30-day moving average ("green")
- Find call option with:
  - **DTE**: 45-180 days
  - **Delta**: ≤ 0.30
  - **Strike**: Above your cost basis (ideally)

**Example Entry - AMZN Call**:
```
Own: 100 shares AMZN @ $200 cost basis
Current AMZN Price: $220
30-Day Average: $210 (stock is "green" - up trend)

Action: Sell 1 AMZN Call
Strike: $240 (0.30 delta, ~9% above current price)
Expiration: 45 days out
Premium Received: $600 ($6.00 per share × 100)

Immediate Income: $600 (3% return in 45 days)
Max Profit if Called Away: $4,000 (stock gain) + $600 (premium) = $4,600
```

---

## 📤 EXIT STRATEGIES

### 1. **Take Profit at 50%**

**Primary Exit**: Close position when profit reaches 50% of premium

```toml
[roll_when]
pnl = 0.5  # 50% profit target
```

**Example - TSLA Put Exit**:
```
Opened: Sold TSLA $360 Put for $800 premium
Target: Close when profit = $400 (50% of $800)

Day 15: Put now worth $400 (down from $800)
Profit: $400 ($800 received - $400 to buy back)
Action: BUY TO CLOSE the put for $400
Result: Keep $400 profit, free up $36,000 capital

Time in Trade: 15 days (instead of 45)
Actual Return: 1.1% in 15 days = ~27% annualized
```

### 2. **Roll at 15 DTE (if not profitable)**

**Secondary Exit**: If position isn't profitable by 15 days to expiration, roll it forward

```toml
[roll_when]
dte = 15        # Roll when 15 days left
min_pnl = 0.0   # Only roll if at least break-even
```

**Example - SHOP Put Roll**:
```
Opened: Sold SHOP $100 Put for $500 premium (45 DTE)
Day 30: 15 days left, put now worth $600 (losing $100)
Stock dropped to $95

Action: ROLL the position
1. Buy back the $100 Put (45 DTE → 15 DTE) for $600
2. Sell new $95 Put (45 DTE) for $700

Net Credit on Roll: $100 ($700 - $600)
Total Premium: $600 ($500 original + $100 roll)
New Expiration: 45 days from now
```

### 3. **Close at 100% Profit**

**Maximum Exit**: Close position if it reaches 100% profit (rare but possible)

```toml
[close_when]
pnl = 1.0  # 100% profit
```

**Example - COIN Call Exit**:
```
Opened: Sold COIN $300 Call for $1,000 premium
Week 1: COIN drops to $250, call now worth $100

Profit: $900 ($1,000 - $100 = 90% profit)
Wait for 100%...

Week 2: Call now worth $50
Profit: $950 (95% profit)

Week 3: Call expires worthless
Action: AUTO-CLOSE at expiration
Result: Keep full $1,000 premium (100% profit)
```

### 4. **Assignment Handling**

**If Put is Assigned** (stock goes below strike):
```
Scenario: TSLA $360 Put assigned
Result: You now own 100 TSLA shares @ $360/share
Cost: $36,000
Effective Cost: $352/share ($360 - $8 premium received)

Next Step: The Wheel continues
→ Sell covered calls on TSLA at higher strike
→ Generate more premium while waiting for stock to recover
```

**If Call is Assigned** (stock goes above strike):
```
Scenario: AMZN $240 Call assigned
Result: Your 100 AMZN shares sold @ $240/share
Revenue: $24,000
Profit: $4,000 (stock) + $600 (premium) = $4,600

Next Step: Back to selling puts
→ Sell new AMZN puts to potentially re-acquire shares
→ Or move to different ticker
```

---

## 🔄 THE WHEEL STRATEGY FLOW

```
START
  ↓
┌─────────────────────────────────────┐
│ 1. SELL CASH-SECURED PUT            │
│    - Stock is "red" (down)          │
│    - Collect premium                │
│    - 30 delta, 45 DTE               │
└─────────────────────────────────────┘
  ↓
  ├─→ [50% Profit] → CLOSE → Back to START
  ├─→ [15 DTE, no profit] → ROLL → Continue monitoring
  ├─→ [Expires worthless] → Keep premium → Back to START
  ↓
┌─────────────────────────────────────┐
│ 2. PUT ASSIGNED (ITM at expiration) │
│    - Now own 100 shares             │
│    - Cost basis = strike - premium  │
└─────────────────────────────────────┘
  ↓
┌─────────────────────────────────────┐
│ 3. SELL COVERED CALL                │
│    - Stock is "green" (up)          │
│    - Collect premium                │
│    - 30 delta, 45 DTE               │
│    - Strike above cost basis        │
└─────────────────────────────────────┘
  ↓
  ├─→ [50% Profit] → CLOSE → Continue holding stock
  ├─→ [15 DTE, no profit] → ROLL → Continue monitoring
  ├─→ [Expires worthless] → Keep premium → Sell another call
  ↓
┌─────────────────────────────────────┐
│ 4. CALL ASSIGNED (ITM at expiration)│
│    - Shares sold at strike          │
│    - Profit = (strike - cost) + premiums │
└─────────────────────────────────────┘
  ↓
Back to START (sell puts again)
```

---

## 💰 COMPLETE EXAMPLE: Full Wheel Cycle

### Ticker: **UPST** (Upstart)
### Starting Capital: $100,000 NLV → $50,000 Buying Power
### UPST Allocation: 5% = $2,500

---

### **Month 1: Sell Put**

```
Date: Jan 7, 2026
UPST Price: $60
30-Day Average: $65 (stock is RED - down 7.7%)

Action: SELL TO OPEN 1 UPST $55 Put
Expiration: Feb 21, 2026 (45 DTE)
Delta: 0.30
Premium: $300 ($3.00 × 100)
Capital Reserved: $5,500

Status: Waiting...
```

---

### **Month 1, Week 3: Take Profit**

```
Date: Jan 28, 2026 (21 days later)
UPST Price: $63 (recovered)
Put Value: $150 (down from $300)

Profit: $150 (50% of premium)
Action: BUY TO CLOSE 1 UPST $55 Put for $150

Results:
✅ Profit: $150
✅ Return: 2.7% in 21 days
✅ Annualized: ~47%
✅ Capital freed: $5,500

Next: Wait for UPST to be "red" again to sell another put
```

---

### **Month 2: Sell Put Again**

```
Date: Feb 15, 2026
UPST Price: $58
30-Day Average: $62 (stock is RED - down 6.5%)

Action: SELL TO OPEN 1 UPST $52 Put
Expiration: Apr 1, 2026 (45 DTE)
Delta: 0.30
Premium: $280 ($2.80 × 100)
Capital Reserved: $5,200

Status: Waiting...
```

---

### **Month 3: Assignment**

```
Date: Apr 1, 2026 (Expiration)
UPST Price: $48 (dropped below strike)

Result: PUT ASSIGNED
→ Now own 100 UPST @ $52/share
→ Cost: $5,200
→ Effective cost basis: $49.20/share ($52 - $2.80 premium)
→ Current value: $4,800 (unrealized loss: $400)

Total Premium Collected So Far: $430 ($150 + $280)

Next: Sell covered calls to generate income while waiting for recovery
```

---

### **Month 3: Sell Covered Call**

```
Date: Apr 8, 2026
UPST Price: $50 (recovering)
30-Day Average: $48 (stock is GREEN - up 4.2%)
Cost Basis: $49.20

Action: SELL TO OPEN 1 UPST $55 Call
Expiration: May 23, 2026 (45 DTE)
Delta: 0.30
Premium: $250 ($2.50 × 100)

Status: Waiting...
```

---

### **Month 4: Take Profit on Call**

```
Date: May 1, 2026 (23 days later)
UPST Price: $49 (dropped back down)
Call Value: $125 (down from $250)

Profit: $125 (50% of premium)
Action: BUY TO CLOSE 1 UPST $55 Call for $125

Results:
✅ Profit: $125
✅ Still own 100 UPST shares
✅ Total premium collected: $555 ($430 + $125)

Current Position:
- Own 100 UPST @ $49.20 cost basis
- Current price: $49
- Unrealized loss: $20
- Total premium: $555
- Net profit: $535 ($555 - $20)
```

---

### **Month 5: Sell Another Call**

```
Date: May 15, 2026
UPST Price: $54 (recovering again)
30-Day Average: $51 (stock is GREEN - up 5.9%)

Action: SELL TO OPEN 1 UPST $58 Call
Expiration: Jun 29, 2026 (45 DTE)
Delta: 0.30
Premium: $280 ($2.80 × 100)

Status: Waiting...
```

---

### **Month 6: Call Assignment**

```
Date: Jun 29, 2026 (Expiration)
UPST Price: $61 (above strike)

Result: CALL ASSIGNED
→ 100 UPST shares sold @ $58/share
→ Revenue: $5,800
→ Cost basis: $4,920 (100 × $49.20)
→ Stock profit: $880 ($5,800 - $4,920)

Total Premium Collected: $835 ($555 + $280)
Total Profit: $1,715 ($880 stock + $835 premium)

Return on Capital: 34.9% ($1,715 / $4,920)
Time in Trade: ~6 months
Annualized Return: ~70%

Status: Back to selling puts (full wheel completed)
```

---

## 📊 Summary of Full Wheel Cycle

| Trade | Action | Premium | Days | Outcome |
|-------|--------|---------|------|---------|
| 1 | Sell $55 Put | +$300 | 21 | Closed at 50% profit (+$150) |
| 2 | Sell $52 Put | +$280 | 45 | Assigned (acquired stock) |
| 3 | Sell $55 Call | +$250 | 23 | Closed at 50% profit (+$125) |
| 4 | Sell $58 Call | +$280 | 45 | Assigned (sold stock) |

**Total Results**:
- **Total Premium**: $835
- **Stock Profit**: $880
- **Total Profit**: $1,715
- **Return**: 34.9% in 6 months (~70% annualized)
- **Trades**: 4 options trades
- **Capital**: $5,200 max

---

## 🎯 Key Success Factors

### 1. **Delta Selection (0.30)**
- ~30% probability of being ITM at expiration
- ~70% probability of profit
- Good balance of premium vs. risk

### 2. **DTE Range (45-180 days)**
- Longer DTE = more premium
- More time for theta decay
- More opportunities to take profit at 50%

### 3. **50% Profit Target**
- Takes profit quickly (often in 20-30 days)
- Frees up capital for new trades
- Reduces risk exposure
- Increases win rate

### 4. **Rolling Strategy**
- Extends duration if needed
- Collects additional premium
- Avoids taking losses
- Maintains positions through volatility

### 5. **Market Regime Detection** (Your Custom Feature)
- Adjusts delta based on VIX and SPY trend
- Reduces exposure in high volatility
- More aggressive in bull markets
- More conservative in bear markets

---

## 🛡️ Risk Management

### Position Sizing
- **5% per ticker** = diversification across 20 stocks
- **50% margin usage** = keeps 50% cash buffer
- **5% max new contracts** = limits single trade size

### Diversification
- 20 different tickers across sectors
- Mix of high/low volatility stocks
- Penny stocks to mega-caps
- Tech, materials, retail, biotech, etc.

### Downside Protection
- Cash-secured puts = can't lose more than stock value
- 30 delta = OTM strikes provide cushion
- Rolling capability = extend and collect more premium
- Market regime detection = reduce exposure in crashes

---

## 📈 Expected Performance

### Conservative Estimate
- **Win Rate**: 70-80% (due to 30 delta and 50% profit target)
- **Average Return per Trade**: 1-3% in 20-40 days
- **Annualized Return**: 15-30% on deployed capital
- **Drawdowns**: 10-20% during market corrections

### Aggressive Estimate (Bull Market)
- **Win Rate**: 80-90%
- **Average Return per Trade**: 2-4% in 20-40 days
- **Annualized Return**: 30-50% on deployed capital
- **Drawdowns**: 5-15%

### Risk Scenarios
- **Bear Market**: Returns may be 5-15%, higher drawdowns (20-30%)
- **High Volatility**: May pause trading or reduce delta significantly
- **Assignment Risk**: May hold stocks through downturns

---

## 🚀 Next Steps

1. **Paper Trade First** (3-6 months minimum)
   - Test the strategy with virtual money
   - Learn the mechanics
   - Build confidence
   - Refine parameters

2. **Set Up IB Gateway**
   - Download and install
   - Configure IBC for automation
   - Test connection

3. **Monitor Daily**
   - Check positions each morning
   - Review P&L
   - Adjust if needed

4. **Track Performance**
   - Log all trades
   - Calculate returns
   - Identify patterns
   - Optimize over time

5. **Scale Gradually**
   - Start with small capital
   - Add more as you gain experience
   - Don't rush into live trading

---

## ⚠️ Important Disclaimers

- **Not Financial Advice**: This is educational only
- **Past Performance**: Does not guarantee future results
- **Risk of Loss**: Options trading involves substantial risk
- **Paper Trade First**: Always test before using real money
- **Understand Mechanics**: Know how options work before trading
- **Capital at Risk**: Never trade with money you can't afford to lose

---

## 📚 Additional Resources

- **ThetaGang Docs**: https://github.com/brndnmtthws/thetagang
- **Options Education**: https://www.optionseducation.org/
- **IBKR API**: https://interactivebrokers.github.io/tws-api/
- **The Wheel Strategy**: Search "options wheel strategy" for more examples

---

**Generated**: January 7, 2026
**Configuration**: thetagang.toml
**Account**: DUO840569 (Paper Trading)

