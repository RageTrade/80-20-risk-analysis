import pandas as pd
from data_cleaning_utils import import_binance_data, clean_btc_df

INITIAL_USD = 100  # initial value of collateral, does not affect results

####
# collateral functions
####


def import_btc_df(min_time, max_time):
    btc_df = import_binance_data(csv='binance_btc_data.csv.zip')
    return clean_btc_df(btc_df, min_time, max_time)


def get_tricrypto_collateral_df(eth_df, use_eth_price=False):
    """ gets value of Curve tricrypto collateral over time based on balancer IL formula & historical price """
    btc_df = import_btc_df(eth_df['time'].min(), eth_df['time'].max())

    collateral_df = btc_df[['time']]
    initial_eth = INITIAL_USD / eth_df.loc[0, 'price']
    initial_btc = INITIAL_USD / btc_df.loc[0, 'price']
    if use_eth_price:
        collateral_df['value'] = INITIAL_USD ** (1 / 3) * (initial_eth * eth_df['price']) ** (2 / 3)
    else:
        collateral_df['value'] = INITIAL_USD ** (1 / 3) * (initial_eth * eth_df['price']) ** (1 / 3) * (
                initial_btc * btc_df['price']) ** (1 / 3)

    return collateral_df


def get_gmx_collateral_df(eth_df):
    btc_df = import_btc_df(eth_df['time'].min(), eth_df['time'].max())

    collateral_df = btc_df[['time']]
    initial_usd = INITIAL_USD * 0.5
    initial_eth = INITIAL_USD / eth_df.loc[0, 'price'] * 0.5
    # initial_btc = INITIAL_USD / btc_df.loc[0, 'price'] * 0.12

    collateral_df['value'] = initial_usd + initial_eth * eth_df['price']  # + initial_btc * btc_df['price']

    return collateral_df


def get_usd_collateral_df(eth_df):
    """ returns collateral_df for portfolio of only USD """
    return pd.DataFrame(data={
        'time': eth_df['time'].to_list(),
        'value': [100] * eth_df.shape[0]
    })


def update_collateral_value(collateral_value, interest_multiplier, lp_pnl_change, current_value, future_value):
    """ updates collateral value from price change, APY earned, and realized Rage IL """
    return collateral_value * future_value / current_value * interest_multiplier + lp_pnl_change
