### The 80-20 Strategy Summary
The 80-20 strategy keeps at least 80% of collateral in an external yield-generating
protocol, such as Curve or GMX and uses ~20% of collateral to provide liquidity on
Rage Trade's ETH-USD perp. This approach allows users to essentially
**recycle liquidity**, providing Rage liquidity with LP tokens from other protocols.
For more details, see the [Rage Trade docs](https://docs.rage.trade/).

### 80-20 Vault Backtest Results

This repo provides simulation code to backtest the Rage Trade 80-20 vault over 
the past 3 years of market data. We can see from the below graph that the 80-20 TriCrypto 
strategy performed slightly better than Uniswap V2, particularly during bull runs.

![backtest results](./graphs/three_year_backtest.png?raw=true "Backtest Results")

Note that these results do not include fee collection, though we expect that Rage will
collect more trading fees than Uniswap V2 as it supports buying on margin.

### 80-20 LP Out-Of-Range Risk

In Uniswap V3, LPs want to keep the price within their active liquidity, so they 
maximize their fee collection. The 80-20 vault rebalances Rage liquidity daily to 
keep the liquidity around the current price. The graphs below shows that over the past
3 years, the price never left the LP range.

![out of range graph](./graphs/lp_bounds_backtest.png?raw=True "Out of Range Graph")

The price even stayed within range during March 2020.

![out of range graph](./graphs/lp_bounds_march_2020.png?raw=True "Out of Range Graph")

### Run The Backtests Yourself

To run the code, first make sure pipenv is installed. Then create the environment:
```
pipenv shell
pipenv install
```

Open jupyter lab
```
jupyter lab
```

Open `run_simulations.ipynb`

Run the notebook from the top to generate the graphs.

To change the backtest settings, modify the constants in `backtest.py`.

To change the collateral settings, or test with your own collateral, check out `collateral_utils.py`

### Output Details

The `backtest()` function returns a DataFrame with the following columns:
* `time`: starting time of the current time interval
* `current_price`: ETH price at current row's `time`
* `future_price`: ETH price at next row's `time`
* `collateral_value`: total collateral value at `time`
* `liquidity`: Uniswap V3 "liquidity" provided at `time`
* `lower_tick`: lower tick for the Rage LP range
* `upper_tick`: upper tick for the Rage LP range
* `eth_deployed`: amount of ETH deployed in Rage LP position
* `usd_deployed`: amount of USD deployed in Rage LP position
* `lp_eth_position`: the total ETH position the LP has accumulated since the previous reset
* `lp_usd_position`: the total amount of USD the LP has received from the position since the previous reset
* `fees_collected`: estimate of USD fees collected over current time interval
* `reset_triggered`: True or False indicates whether a reset was triggered that row (takes effect next row)
* `lp_pnl`: The total LP P&L since the previous reset
* `lp_pnl_change`: The change in LP P&L since the previous rebalance
