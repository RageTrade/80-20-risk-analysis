import numpy as np

####
# lp strategy functions
####


def get_lp_range_bounds(percent_collateral_deployed):
    """ given the percent capital deployed, returns the lower and upper bounds for LP range """
    return (1 - percent_collateral_deployed / 100)**2, 1/(1 - percent_collateral_deployed / 100)**2


def apy_to_apy_multiplier(minutes_per_period, apy):
    """ for minutes per period, what is multiplier from APY """
    minutes_per_year = 365 * 24 * 60
    periods_per_year = minutes_per_year / minutes_per_period
    return np.exp(np.log(1 + apy / 100) / periods_per_year)


def update_pnl(lp_pnl, future_price, lp_eth_position, lp_usd_balance):
    """ returns updated lp_pnl and lp_pnl_change """
    lp_pnl_change = lp_usd_balance + lp_eth_position * future_price - lp_pnl
    return lp_pnl + lp_pnl_change, lp_pnl_change
