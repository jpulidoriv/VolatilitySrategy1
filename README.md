# Risk Managed Volatility Timing Strategy on SPY

This project implements and backtests a simple **volatility timing long/cash strategy** on the S&P 500 ETF **SPY**, using daily data from 2010 onwards.

The goal is **not** to beat Buy & Hold on raw returns, but to **reduce portfolio risk** (volatility and drawdowns) by staying invested only in “calm” volatility regimes.

## 1. Mission

- Use **realized volatility** of SPY (20-day rolling standard deviation of daily log returns) as a simple **risk indicator**.
- Define a **volatility threshold**: the **historical median** of the 20-day volatility.
- Build a **Long / Cash strategy**:
  - If volatility is **below** the threshold → **invested (long SPY)**.
  - If volatility is **above** the threshold → **out of the market (cash)**.
- Compare this strategy against a **Buy & Hold benchmark**:
  - Equity curve
  - Annualized return
  - Annualized volatility
  - Sharpe ratio
  - Maximum drawdown
---

## 2. Data & Tools

- **Asset:** SPY (S&P 500 ETF)
- **Data source:** [`yfinance`]
- **Frequency:** Daily close prices
- **Language:** Python
- **Main libraries:**
  - `yfinance` 
  - `pandas` 
  - `numpy` 
  - `matplotlib` 
---

## 3. Methodology

### 3.1 Daily log returns

Given daily close prices \( P_t \), the daily **log return** is:

\[
r_t = \ln\left(\frac{P_t}{P_{t-1}}\right)
\]

In code:

```python
df = yf.download("SPY", start="2010-01-01")
df = df[["Close"]].dropna().copy()

df["log_return"] = np.log(df["Close"] / df["Close"].shift(1))
df = df.dropna()

