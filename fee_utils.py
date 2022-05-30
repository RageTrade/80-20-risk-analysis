import numpy as np

from uni_v3_utils import calculate_usd_in_range

#####
# fee estimation functions
#####


def get_arbitrage_prices(prices, arb_threshold, concentrated=False):
    """ given minimum arbitrage threshold for trade, get the prices for arbitrage-only trades """
    arb_prices = [prices[0]]
    prev_price = prices[0]
    for p in prices[1:]:
        if np.abs(p - prev_price) / prev_price * 100 > arb_threshold:
            arb_prices.append(p)
            prev_price = p
        elif concentrated:
            arb_prices.append(prev_price)

    return arb_prices


def estimate_fees_collected(liquidity, arb_threshold, fee_size, prices):
    """ returns USD value of fees collected from arbitrage volume alone """
    arb_prices = get_arbitrage_prices(prices, arb_threshold)
    usd_traded = 0
    for i in range(len(arb_prices) - 1):
        min_price = np.minimum(arb_prices[i], arb_prices[i + 1])
        max_price = np.maximum(arb_prices[i], arb_prices[i + 1])
        usd_traded += calculate_usd_in_range(liquidity, min_price, max_price)

    return usd_traded * fee_size
