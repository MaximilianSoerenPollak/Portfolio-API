#%%
import yahooquery as yq
import pandas as pd
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt.expected_returns import mean_historical_return
from pypfopt.risk_models import CovarianceShrinkage

# %%
ticker = yq.Ticker(["GME", "AADI", "IBM", "BTI"])
df = ticker.history(interval="1d", period="ytd", adj_ohlc=True)
df = df.reset_index()
df.shape
# %%
df = df.drop(["high", "volume", "low", "open", "dividends"], axis=1)
df
# %%
df_test = df.copy()
# %%

df_test = df_test.pivot_table(values="close", index="date", columns="symbol", aggfunc="first")
# %%
mu = mean_historical_return(df_test)
s = CovarianceShrinkage(df_test).ledoit_wolf()
# %%
ef = EfficientFrontier(mu, s)
weights = ef.max_sharpe()
cleaned_weights = ef.clean_weights()
print(dict(cleaned_weights))
# %%
ef.portfolio_performance(verbose=True)
# %%
from pypfopt.discrete_allocation import DiscreteAllocation, get_latest_prices

# %%
latest_prices = get_latest_prices(df_test)
# print(latest_prices)
da = DiscreteAllocation(weights, latest_prices, total_portfolio_value=100000)
allocation, leftover = da.greedy_portfolio()
print("Discrete allocation:", allocation)
print("Funds remaining: ${:.2f}".format(leftover))
# %%

# %%
from pypfopt import HRPOpt

# %%
returns = df_test.pct_change().dropna()
# %%
hrp = HRPOpt(returns)
hrp_weights = hrp.optimize()
hrp.portfolio_performance(verbose=True)
print(dict(hrp_weights))
# %%
da_hrp = DiscreteAllocation(hrp_weights, latest_prices, total_portfolio_value=100000)
allocation, leftover = da_hrp.greedy_portfolio()
print("Discrete allocation (HRP):", allocation)
print("Funds remaining (HRP): ${:.2f}".format(leftover))
# %%
from pypfopt.efficient_frontier import EfficientCVaR

# %%
S = df_test.cov()
ef_cvar = EfficientCVaR(mu, S)
cvar_weights = ef_cvar.min_cvar()
cleaned_weights = ef_cvar.clean_weights()
print(dict(cleaned_weights))
# %%

# %%
da_cvar = DiscreteAllocation(cvar_weights, latest_prices, total_portfolio_value=10000)
allocation, leftover = da_cvar.greedy_portfolio()
print("Discrete allocation (CVAR):", allocation)
print("Funds remaining (CVAR): ${:.2f}".format(leftover))
# %%
returns = df_test.pct_change().dropna()
hrp = HRPOpt(returns)
hrp_weights = hrp.optimize()
# hrp.portfolio_performance(verbose=True)
# %%
hrp.porfolio_performanc
# %%
