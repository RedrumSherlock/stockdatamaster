import logging

from sdm.util.market_utils import CATradingCalendar, shift_open_days
import sdm.constants as c

# E-ratio calculation
DEFAULT_ATR_DAYS = 14


def atr(curr, prev_n_list):
    if len(prev_n_list) == 0:
        return tr(curr)
    sum_tr = 0
    for i in range(len(prev_n_list)):
        sum_tr += tr(prev_n_list[i], prev_n_list[i - 1] if i > 0 else None)
    sum_tr += tr(curr, prev_n_list[-1])
    return sum_tr / (len(prev_n_list) + 1)


def tr(curr, prev=None):
    if prev is None:
        return curr["high"] - curr["low"]
    return max(curr["high"] - curr["low"], abs(curr["high"] - prev["close"]), abs(curr["low"] - prev["close"]))


def mfe(curr, next_n_list):
    return max(price["high"] - curr["close"] if price["high"] > curr["close"] else 0 for price in next_n_list)


def mae(curr, next_n_list):
    return max(curr["close"] - price["low"] if price["low"] < curr["close"] else 0 for price in next_n_list)


def average_e_ratio(market_data, func, E_RATIO_N, ATR_N=DEFAULT_ATR_DAYS):
    # func must be a function that takes the current price and cumulative prices as input, and retunr a boolean to
    # decide whether to buy or not
    mfe_list = []
    mae_list = []
    skipped_count = 0
    holidays = CATradingCalendar().holidays(c.EARLIEST_DATE, c.LATEST_DATE)
    for symbol, symbol_prices in market_data.items():
        daily_price_list = list(symbol_prices.values())
        dates_list = list(symbol_prices.keys())
        date_gap = False
        for i in range(len(dates_list) - 1):
            if shift_open_days(dates_list[i], 1, "tsx", holidays) != dates_list[i + 1]:
                skipped_count += 1
                date_gap = True
                break
        if date_gap:
            continue
        if len(daily_price_list) <= E_RATIO_N + ATR_N + 1:
            continue
        for i in range(ATR_N + 1, len(daily_price_list) - E_RATIO_N):
            curr = daily_price_list[i]
            if func(curr, daily_price_list[:i]):
                curr_atr = atr(curr, daily_price_list[i - ATR_N:i])
                if curr_atr <= 0:
                    continue
                symbol_mfe = mfe(curr, daily_price_list[i + 1: i + E_RATIO_N + 1]) / curr["close"]
                symbol_mae = mae(curr, daily_price_list[i + 1: i + E_RATIO_N + 1]) / curr["close"]
                mfe_list.append(symbol_mfe)
                mae_list.append(symbol_mae)
    logging.info(f"In total skipped {skipped_count} symbols")

    if len(mfe_list) == 0 or sum(mae_list) == 0:
        return 0

    logging.debug(f"Max mfe is {max(mfe_list)} and min mfe is {min(mfe_list)}")
    logging.debug(f"Max mae is {max(mae_list)} and min mae is {min(mae_list)}")

    return sum(mfe_list) / sum(mae_list)
