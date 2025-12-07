
#%%
import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


df = yf.download("SPY", start = "2010-01-01")
df = df[["Close"]].dropna()
df["log_return"] = np.log(df["Close"] / df["Close"].shift(1))
df = df.dropna()


window = 20
df ["Vol20"] = df["log_return"].rolling(window).std()
threshold = df["Vol20"].median()

print ("Threshold", threshold)
#Threshold 0.007799613671426236

df["position_raw"] = (df["Vol20"] <= threshold).astype(int)

df["position"] = df["position_raw"].shift(1)
df["position"].fillna(0, inplace=True)

# Retornos de la estrategia y de buy & hold
df["strategy_log_return"] = df["position"] * df["log_return"]
df["bh_log_return"] = df["log_return"]

df["bh_equity"] = np.exp(df["bh_log_return"].cumsum())
df["strategy_equity"] = np.exp(df["strategy_log_return"].cumsum())

plt.figure()
plt.plot(df.index, df["bh_equity"], label="Buy & Hold")
plt.plot(df.index, df["strategy_equity"], label="Volatility Strategy")
plt.legend()
plt.title("Equity Curve: Buy & Hold vs Volatility-Timing Strategy")
plt.xlabel("Date")
plt.ylabel("Equity")
plt.show()

df.to_csv("resultados_volatility.csv", index=True)

mu_tr_daily = df["strategy_log_return"].mean()
mu_bh_daily = df["bh_log_return"].mean()

mu_tr_annual = mu_tr_daily * 252
mu_bh_annual = mu_bh_daily * 252

print("Strategy annual return (%):", round(mu_tr_annual * 100, 2))
print("BH annual return (%):", round(mu_bh_annual * 100, 2))

vol_tr_daily = df["strategy_log_return"].std()
vol_bh_daily = df["bh_log_return"].std()

vol_tr_annual = vol_tr_daily * np.sqrt(252)
vol_bh_annual = vol_bh_daily * np.sqrt(252)

print("Strategy annual vol (%):", round(vol_tr_annual * 100, 2))
print("BH annual vol (%):", round(vol_bh_annual * 100, 2))

sharpe_tr = mu_tr_annual / vol_tr_annual
sharpe_bh = mu_bh_annual / vol_bh_annual

print("Sharpe Strategy:", round(sharpe_tr, 2))
print("Sharpe Buy&Hold:", round(sharpe_bh, 2))

def max_drawdown(equity):
    
    roll_max = equity.cummax()         
    dd = equity / roll_max - 1.0   
    
    return dd.min()  

mdd_tr = max_drawdown(df["strategy_equity"])
mdd_bh = max_drawdown(df["bh_equity"])

print("Max DD Strategy:", mdd_tr, "→", round(mdd_tr * 100, 2), "%")
print("Max DD Buy&Hold:", mdd_bh, "→", round(mdd_bh * 100, 2), "%")

metrics = pd.DataFrame({
    "Annual Return (%)": [mu_tr_annual * 100,    mu_bh_annual * 100],
    "Annual Vol (%)":    [vol_tr_annual * 100,   vol_bh_annual * 100],
    "Sharpe":            [sharpe_tr,             sharpe_bh],
    "Max DD (%)":        [mdd_tr * 100,          mdd_bh * 100]
}, index=["Strategy", "Buy&Hold"])

plt.figure()
metrics[["Annual Return (%)", "Annual Vol (%)"]].plot(kind="bar")
plt.title("Strategy vs Buy&Hold: Return & Volatility")
plt.ylabel("%")
plt.xticks(rotation=0)
plt.tight_layout()
plt.show()

plt.figure()
metrics[["Sharpe"]].plot(kind="bar")
plt.title("Strategy vs Buy&Hold: Sharpe Ratio")
plt.xticks(rotation=0)
plt.tight_layout()
plt.show()

#%%
plt.figure()
metrics[["Max DD (%)"]].plot(kind="bar")
plt.title("Strategy vs Buy&Hold: Max Drawdown")
plt.ylabel("%")
plt.xticks(rotation=0)
plt.tight_layout()
plt.show()