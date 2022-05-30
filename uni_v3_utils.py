import numpy as np

####
# uniswap v3 math functions
####


def calculate_univ3_liquidity(price, q_eth, q_usd, lower_tick_price, upper_tick_price):
    """ return minimum of asset liquidity """
    liquidity_eth = q_eth * np.sqrt(price) * np.sqrt(upper_tick_price) / (np.sqrt(upper_tick_price) - np.sqrt(price))
    liquidity_usd = q_usd / (np.sqrt(price) - np.sqrt(lower_tick_price))

    return np.minimum(liquidity_eth, liquidity_usd)


def reset_liquidity(price, lower_bound, upper_bound, collateral_value, percent_collateral_deployed):
    """ returns new uni v3 liquidity value after reset """
    q_eth = collateral_value / 2 / price * percent_collateral_deployed / 100
    q_usd = collateral_value / 2 * percent_collateral_deployed / 100
    return calculate_univ3_liquidity(price, q_eth, q_usd, price * lower_bound, price * upper_bound)


def calculate_eth_in_range(liquidity, upper_tick_price, price):
    """ returns eth in a uni v3 range with provided liquidity """
    return liquidity * (np.sqrt(upper_tick_price) - np.sqrt(price)) / (
            np.sqrt(price) * np.sqrt(upper_tick_price))


def calculate_usd_in_range(liquidity, lower_tick_price, price):
    """ returns usd in a uni v3 range with provided liquidity """
    return liquidity * (np.sqrt(price) - np.sqrt(lower_tick_price))


def calculate_eth_change(liquidity, upper_bound, current_price, future_price):
    """ calculates the change in eth balance after price movement in uni v3 range """
    initial_eth = calculate_eth_in_range(liquidity, current_price * upper_bound, current_price)
    future_eth = calculate_eth_in_range(liquidity, current_price * upper_bound, future_price)
    return future_eth - initial_eth


def calculate_usd_change(liquidity, lower_bound, current_price, future_price):
    """ calculates the change in usd balance after price movement in uni v3 range """
    initial_usd = calculate_usd_in_range(liquidity, current_price * lower_bound, current_price)
    future_usd = calculate_usd_in_range(liquidity, current_price * lower_bound, future_price)
    return future_usd - initial_usd


def get_eth_usd_deployed(liquidity, lower_bound, upper_bound, price):
    """ returns eth and usd in range given liquidity """
    eth_deployed = calculate_eth_in_range(liquidity, price * upper_bound, price)
    usd_deployed = calculate_usd_in_range(liquidity, price * lower_bound, price)
    return eth_deployed, usd_deployed

