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

### 3.2 20-day realized volatility

Volatility is estimated as the **20-day rolling standard deviation** of daily log returns:

$$
\text{Vol20}_t = \text{Std}\bigl(r_{t-19}, \dots, r_t\bigr)
$$

In code:

```python
window = 20
df["Vol20"] = df["log_return"].rolling(window).std()
3.3 Volatility threshold (historical median)
The volatility threshold is defined as the historical median of all 20-day volatilities in the sample:

Threshold
=
Median
(
Vol20
𝑡
)
Threshold=Median(Vol20 
t
​
 )
In code:

python
Code kopieren
threshold = df["Vol20"].median()
print("Threshold:", threshold)
# ~ 0.0078  ≈ 0.78% daily volatility
Interpretation:
If the current 20-day volatility is below ~0.78% per day, the regime is considered “low volatility”.

3.4 Trading rule (Long / Cash)
A raw long/cash signal is constructed as:

position_raw
𝑡
=
{
1
,
if 
Vol20
𝑡
≤
Threshold
0
,
if 
Vol20
𝑡
>
Threshold
position_raw 
t
​
 ={ 
1,
0,
​
  
if Vol20 
t
​
 ≤Threshold
if Vol20 
t
​
 >Threshold
​
 
In code:

python
Code kopieren
df["position_raw"] = (df["Vol20"] <= threshold).astype(int)
1 → low volatility → long SPY

0 → high volatility → cash

To avoid look-ahead bias, the position used for day 
𝑡
t is the signal from day 
𝑡
−
1
t−1:

position
𝑡
=
position_raw
𝑡
−
1
position 
t
​
 =position_raw 
t−1
​
 
In code:

python
Code kopieren
df["position"] = df["position_raw"].shift(1)
df["position"] = df["position"].fillna(0)
So:

The decision is made at the close of day 
𝑡
−
1
t−1,

and applied during day 
𝑡
t.

3.5 Strategy and benchmark returns
Buy & Hold: always fully invested in SPY.

Strategy: invested only when position == 1.

Daily log returns:

Buy & Hold:

𝑟
𝑡
BH
=
𝑟
𝑡
r 
t
BH
​
 =r 
t
​
 
Strategy:

𝑟
𝑡
Strat
=
position
𝑡
⋅
𝑟
𝑡
r 
t
Strat
​
 =position 
t
​
 ⋅r 
t
​
 
In code:

python
Code kopieren
df["strategy_log_return"] = df["position"] * df["log_return"]
df["bh_log_return"] = df["log_return"]
Equity curves (starting at 1), using that the sum of log-returns is the log of the total growth factor:

𝐸
𝑡
=
exp
⁡
(
∑
𝑠
≤
𝑡
𝑟
𝑠
)
E 
t
​
 =exp( 
s≤t
∑
​
 r 
s
​
 )
In code:

python
Code kopieren
df["bh_equity"] = np.exp(df["bh_log_return"].cumsum())
df["strategy_equity"] = np.exp(df["strategy_log_return"].cumsum())
4. Performance Metrics
(All numbers below are based on the sample used in this project.)

Let 
𝑟
𝑡
Strat
r 
t
Strat
​
  and 
𝑟
𝑡
BH
r 
t
BH
​
  be the daily log-returns of the strategy and the benchmark, respectively.

4.1 Annualized return
Daily mean log returns:

𝜇
daily
=
𝐸
[
𝑟
𝑡
]
≈
𝑟
‾
μ 
daily
​
 =E[r 
t
​
 ]≈ 
r
 
Annualized (using 252 trading days):

𝜇
annual
≈
252
⋅
𝜇
daily
μ 
annual
​
 ≈252⋅μ 
daily
​
 
In code:

python
Code kopieren
mu_tr_daily = df["strategy_log_return"].mean()
mu_bh_daily = df["bh_log_return"].mean()

mu_tr_annual = mu_tr_daily * 252
mu_bh_annual = mu_bh_daily * 252
Strategy annual return: 4.8%

Buy & Hold annual return: 13.11%

4.2 Annualized volatility
Daily volatility (standard deviation of daily log returns):

𝜎
daily
=
V
a
r
(
𝑟
𝑡
)
σ 
daily
​
 = 
Var(r 
t
​
 )
​
 
Assuming i.i.d. daily returns, annualized volatility is:

𝜎
annual
≈
252
⋅
𝜎
daily
σ 
annual
​
 ≈ 
252
​
 ⋅σ 
daily
​
 
In code:

python
Code kopieren
vol_tr_daily = df["strategy_log_return"].std()
vol_bh_daily = df["bh_log_return"].std()

vol_tr_annual = vol_tr_daily * np.sqrt(252)
vol_bh_annual = vol_bh_daily * np.sqrt(252)
Strategy annual vol: 7.66%

Buy & Hold annual vol: 17.27%

4.3 Sharpe ratio (rf ≈ 0)
With risk-free rate 
𝑟
𝑓
≈
0
r 
f
​
 ≈0, the annual Sharpe ratio is:

Sharpe
=
𝜇
annual
−
𝑟
𝑓
𝜎
annual
≈
𝜇
annual
𝜎
annual
Sharpe= 
σ 
annual
​
 
μ 
annual
​
 −r 
f
​
 
​
 ≈ 
σ 
annual
​
 
μ 
annual
​
 
​
 
In code:

python
Code kopieren
sharpe_tr = mu_tr_annual / vol_tr_annual
sharpe_bh = mu_bh_annual / vol_bh_annual
Strategy Sharpe: 0.63

Buy & Hold Sharpe: 0.76

The strategy trades off some return for lower risk; its Sharpe is slightly lower than Buy & Hold in this basic configuration.

4.4 Maximum Drawdown
Let 
𝐸
𝑡
E 
t
​
  be the equity curve and

𝑀
𝑡
=
max
⁡
𝑠
≤
𝑡
𝐸
𝑠
M 
t
​
 = 
s≤t
max
​
 E 
s
​
 
the running maximum. The drawdown at time 
𝑡
t is:

DD
𝑡
=
𝐸
𝑡
𝑀
𝑡
−
1
DD 
t
​
 = 
M 
t
​
 
E 
t
​
 
​
 −1
The maximum drawdown is:

MaxDD
=
min
⁡
𝑡
DD
𝑡
MaxDD= 
t
min
​
 DD 
t
​
 
In code:

python
Code kopieren
def max_drawdown(equity):
    roll_max = equity.cummax()
    dd = equity / roll_max - 1.0
    return dd.min()

mdd_tr = max_drawdown(df["strategy_equity"])
mdd_bh = max_drawdown(df["bh_equity"])
Strategy Max DD: −16.8%

Buy & Hold Max DD: −33.7%

The strategy roughly halves the maximum drawdown compared to Buy & Hold.

4.5 Time in the market
The fraction of days where the strategy is invested is simply the mean of the position indicator:

TimeInMarket
=
𝐸
[
position
𝑡
]
≈
position
‾
TimeInMarket=E[position 
t
​
 ]≈ 
position
​
 
In code:

python
Code kopieren
time_in_market = df["position"].mean()
Time in market (strategy): fraction of days with position = 1.

Time in market (Buy & Hold): always 100%.

5. Results Summary
The volatility-timing strategy significantly reduces risk:

Lower annual volatility (7.66% vs 17.27%).

Lower maximum drawdown (−16.8% vs −33.7%).

It comes at the cost of lower absolute return:

4.8% p.a. vs 13.11% p.a. for Buy & Hold.

Sharpe ratio is slightly lower than Buy & Hold in this basic configuration:

0.63 vs 0.76.

Interpretation:
This simple rule behaves like a risk-managed overlay on SPY:
it does not aim to beat Buy & Hold on returns, but to offer a smoother ride with smaller drawdowns by avoiding high-volatility regimes.


