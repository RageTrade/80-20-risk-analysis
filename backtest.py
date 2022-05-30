import pandas as pd

from uni_v3_utils import reset_liquidity, calculate_eth_change, calculate_usd_change, get_eth_usd_deployed
from fee_utils import estimate_fees_collected
from collateral_utils import update_collateral_value
from strategy_utils import get_lp_range_bounds, apy_to_apy_multiplier, update_pnl

####
# parameter constants
####

VAULT_RESET_SLIPPAGE = 0.03  # assumed slippage cost from unwinding vault trading position
FEE_SIZE = .001  # Rage LPs collect 0.1% fees (though charge takers 0.15%)
INITIAL_COLLATERAL_VALUE = 1000000  # amount of money starting in the vault during backtest

####
# entrypoint
####


def backtest(eth_df, collateral_df, collateral_apy=0, arb_threshold=0.2, percent_collateral_deployed=20,
             liquidity_concentration=1, reset_threshold=0.2, window_size=60*24):
    """ backtests the Rage Trade vault strategy w/ arbitrary collateral w/ arbitrary APY
    @param eth_df: df with eth price history
    @param collateral_df: df with collateral price history
    @param collateral_apy: expected APY on collateral
    @param arb_threshold: the minimum price deviation for arbitrage to occur
    @param percent_collateral_deployed: "80-20" vault, so deploys 20% of collateral in Rage
    @param liquidity_concentration: 1 is equivalent to UNI v2, 2 is equivalent to 2x leveraged UNI v2
    @param reset_threshold: calls reset after trading notional reaches 20% of collateral value
    @param window_size: number of minutes between rebalances
    """
    apy_multiplier = apy_to_apy_multiplier(window_size, collateral_apy)
    collateral_value = INITIAL_COLLATERAL_VALUE
    lower_bound, upper_bound = get_lp_range_bounds(percent_collateral_deployed / liquidity_concentration)
    v3_liquidity = reset_liquidity(eth_df.loc[0, 'price'], lower_bound, upper_bound, collateral_value,
                                   percent_collateral_deployed)  # initial uniswap v3 liquidity
    # lp variables
    lp_eth_position = 0  # tracks total eth position held in trader state
    lp_usd_balance = 0  # tracks the net amount of usd gained from Rage LP positions
    lp_pnl = 0  # tracks the total profit & loss from Rage LP position

    df_rows = []
    for i in range(eth_df.shape[0] // window_size - 1):  # for every price change
        current_price, future_price = eth_df.loc[i * window_size, 'price'], eth_df.loc[(i + 1) * window_size, 'price']
        eth_deployed, usd_deployed = get_eth_usd_deployed(v3_liquidity, lower_bound, upper_bound, current_price)
        initial_values = {  # store initial values
            'time': eth_df.loc[i * window_size, 'time'],
            'current_price': current_price,
            'future_price': future_price,
            'collateral_value': collateral_value,
            'liquidity': v3_liquidity,
            'lower_tick': current_price * lower_bound,
            'upper_tick': current_price * upper_bound,
            'eth_deployed': eth_deployed,
            'usd_deployed': usd_deployed,
            'lp_eth_position': lp_eth_position,
            'lp_usd_balance': lp_usd_balance,
        }
        fees_collected = estimate_fees_collected(v3_liquidity, arb_threshold, FEE_SIZE,
                                                 eth_df.loc[i*window_size: (i+1)*window_size, 'price'].to_list())
        lp_eth_position += calculate_eth_change(v3_liquidity, upper_bound, current_price, future_price)
        lp_usd_balance += calculate_usd_change(v3_liquidity, lower_bound, current_price, future_price) + fees_collected
        lp_pnl, lp_pnl_change = update_pnl(lp_pnl, future_price, lp_eth_position, lp_usd_balance)
        collateral_value = update_collateral_value(collateral_value, apy_multiplier, lp_pnl_change,
                                                   collateral_df.loc[i * window_size, 'value'],
                                                   collateral_df.loc[(i + 1) * window_size, 'value'])
        reset_triggered = abs(lp_eth_position) * future_price > reset_threshold * collateral_value
        if reset_triggered:  # reset if trading position is above reset_threshold
            collateral_value -= abs(lp_eth_position) * future_price * VAULT_RESET_SLIPPAGE  # subtract slippage
            v3_liquidity = reset_liquidity(future_price, lower_bound, upper_bound, collateral_value,
                                           percent_collateral_deployed)  # recalculate uni v3 liquidity
            lp_eth_position, lp_usd_balance, lp_pnl = [0]*3  # reset lp variables

        final_values = {
                'fees_collected': fees_collected,
                'reset_triggered': reset_triggered,
                'lp_pnl': lp_pnl,
                'lp_pnl_change': lp_pnl_change,
        }
        df_rows.append({**initial_values, **final_values})

    return pd.DataFrame(df_rows)

