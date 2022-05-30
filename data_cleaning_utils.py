import pandas as pd
import numpy as np
from os import listdir
from os.path import isfile, join

####
# cleaning code for binance kline & spot data (used to generate included binanace data CSVs)
####


def clean_binance_spot_data(df):
    """ convert aggregated trade data to minute data """
    df.columns = ['trade_id', 'price', 'q', 'first_tid', 'last_tid', 'time', 'buyer_maker', 'best_price']
    df['time'] = pd.to_datetime(df['time'], unit='ms')
    df['n_trades'] = df['last_tid'] - df['first_tid']
    df = df[['time', 'price', 'q', 'n_trades']].set_index('time').groupby(pd.Grouper(freq='1min')).apply(
        lambda x: [np.sum(x['price'] * x['q']) / x['q'].sum(), x['q'].sum(), x['n_trades'].sum()]).reset_index()
    df['price'] = df[0].apply(lambda x: x[0])
    df['q'] = df[0].apply(lambda x: x[1])
    df['n_trades'] = df[0].apply(lambda x: x[2])

    return df.drop(columns=[0])


def clean_binance_kline_data(df):
    cols = ['time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'qvolume', 'ntrades', 'tvolume', 'tqvolume',
            'ignore']
    # columns are a minute of data... want to save it for continuity
    first_row = pd.DataFrame(list(df.columns)).T
    df.columns = cols
    first_row.columns = cols
    df = df[['time', 'open']]
    first_row = first_row[['time', 'open']]
    try:
        first_row = first_row.astype(df.dtypes.to_dict())
        df = pd.concat([first_row, df]).reset_index(drop=True)
    except:
        print('oops')
        pass
    df['time'] = pd.to_datetime(df['time'], unit='ms')
    df = df.rename(columns={'open': 'price'})

    return df


def make_binance_data_csv(dir='./one_minute_eth_data/', file_name='binance_eth_data.csv'):
    onlyfiles = [dir + f for f in listdir(dir) if isfile(join(dir, f))]
    dfs = []
    for f in onlyfiles:
        dfs.append(clean_binance_kline_data(pd.read_csv(f)))
    df = pd.concat(dfs)

    df.sort_values(by='time').reset_index(drop=True).to_csv(file_name)


####
# functions for importing and cleaning provided binance data CSVs
####


def import_binance_data(csv='binance_eth_data.csv.zip'):
    df = pd.read_csv(csv)
    df = df[['time', 'price']]
    df['time'] = pd.to_datetime(df['time'])

    return df


def interpolate_missing_values(df, start_date=None, end_date=None):
    """ linearly interpolates missing 1 minute data points """
    df = df.set_index('time')
    start_date = start_date if start_date is not None else df.index.min()
    end_date = end_date if end_date is not None else df.index.max()
    df = df.reindex(pd.date_range(start=start_date, end=end_date, freq='1min'))
    df = df.interpolate()
    return df.reset_index().rename(columns={'index': 'time'})


def get_eth_df(start_date=None, end_date=None):
    eth_df = import_binance_data()
    if start_date is not None:
        eth_df = eth_df.loc[eth_df['time'] >= start_date].reset_index(drop=True)
    if end_date is not None:
        eth_df = eth_df.loc[eth_df['time'] <= end_date].reset_index(drop=True)

    return interpolate_missing_values(eth_df)


def clean_btc_df(btc_df, start_date, end_date):
    btc_df = btc_df.loc[(btc_df['time'] >= start_date) & (btc_df['time'] <= end_date)].reset_index(drop=True)
    return interpolate_missing_values(btc_df, start_date=start_date, end_date=end_date)

