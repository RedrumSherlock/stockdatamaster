
from sdm.candlestick.parameters import *


def is_down_trend(curr, prev_5, prev_10, prev_20, thres_5=DOWN_AFTER_5_DAYS_THRES,
                  thres_10=DOWN_AFTER_10_DAYS_THRES, thres_20=DOWN_AFTER_20_DAYS_THRES):
    # Here we simply compare the current close price against the closing price 10, 20, 40 days ago, i.e. 2 weeks, one
    # month, 2 months ago. If the closing price difference is more than predefined thresholds against any one of these,
    # We call it a down trend
    return curr["close"] < prev_5["close"] * (1 - thres_5) or curr["close"] < prev_10["close"] * \
        (1 - thres_10) or curr["close"] < prev_20["close"] * (1 - thres_20)


def is_up_trend(curr, prev_5, prev_10, prev_20, thres_5=UP_AFTER_5_DAYS_THRES,
                thres_10=UP_AFTER_10_DAYS_THRES, thres_20=UP_AFTER_20_DAYS_THRES):
    # Same idea as above but in the opposite way
    return curr["close"] > prev_5["close"] * (1 + thres_5) or curr["close"] > prev_10["close"] * \
           (1 + thres_10) or curr["close"] > prev_20["close"] * (1 + thres_20)


def is_down_trend_rsi(curr, prev_n_list, bound=RSI_LOWER_BOUND, n=RSI_N, method=RSI_METHODS.simple):
    # We use the most commonly used RSI for 12 days.
    return rsi(curr, prev_n_list, n, method) < bound


def is_up_trend_rsi(curr, prev_n_list, bound=RSI_UPPER_BOUND, n=RSI_N, method=RSI_METHODS.simple):
    # We use the most commonly used RSI for 12 days.
    return rsi(curr, prev_n_list, n, method) > bound


def rsi(curr, prev_n_list, n=RSI_N, method=RSI_METHODS.simple):
    # There are three ways of calculating RSI, but there aren't too much difference. The latter two just smooth the
    # averaging so the number is more stable against sudden changes. here I'll just use the simple one
    if len(prev_n_list) < n:
        raise ValueError("There must be at least {} days data to calculate RSI, but there are only {}".format(
            n, len(prev_n_list)))

    avg_up = 0.0
    avg_down = 0.0
    day = len(prev_n_list) - n
    while day < len(prev_n_list):
        next_closing = curr["close"] if day == len(prev_n_list)-1 else prev_n_list[day+1]["close"]
        prev_closing = prev_n_list[day]["close"]
        if method == RSI_METHODS.simple:
            avg_up += next_closing - prev_closing if next_closing > prev_closing else 0
            avg_down += prev_closing - next_closing if prev_closing > next_closing else 0
        elif method == RSI_METHODS.exponential:
            avg_up = 2/(n+1) * (next_closing - prev_closing) + (1 - 2/(n+1)) * avg_up \
                if next_closing > prev_closing else avg_up
            avg_down = 2/(n+1) * (prev_closing - next_closing) + (1 - 2/(n+1)) * avg_down \
                if prev_closing > next_closing else avg_down
        elif method == RSI_METHODS.wilder:
            avg_up = 1/n * (next_closing - prev_closing) + (1 - 1/n) * avg_up if next_closing > prev_closing else avg_up
            avg_down = 1/n * (prev_closing - next_closing) + (1 - 1/n) * avg_down if prev_closing > next_closing \
                else avg_down
        day += 1
    if avg_up + avg_down > 0:
        return round(100 * avg_up / (avg_up + avg_down), 2)
    else:
        return 50
