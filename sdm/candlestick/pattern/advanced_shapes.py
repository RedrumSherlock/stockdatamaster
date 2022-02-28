"""
This module defines the detection of the advanced stick shapes
For all the methods in this module, the input is a dictionary of the daily stock price with usually 5 keys: high,
low, open, close, and volume. For CandleStick detection the first 4 keys are mandatory.
Some of the methods would require data from previous's day, or even the days before. In these cases they will be
provided in prev_n (n=1,2,3..) input parameter.
"""

from sdm.candlestick.pattern.basic_shapes import *
from sdm.candlestick.parameters import *


def is_dark_cloud(curr, prev_1):
    return is_white(prev_1) and day_length(prev_1) > 0 and body_length(prev_1)/day_length(prev_1) > \
        DARK_CLOUD_PIERCING_BODY_THRES and curr["open"] > prev_1["close"] and is_black(curr) and curr["close"]\
        < (prev_1["open"] + prev_1["close"])/2


def is_piercing(curr, prev_1):
    return is_black(prev_1) and day_length(prev_1) > 0 and body_length(prev_1)/day_length(prev_1) > \
        DARK_CLOUD_PIERCING_BODY_THRES and curr["open"] < prev_1["close"] and is_white(curr) and curr["close"]\
        > (prev_1["open"] + prev_1["close"])/2


def is_engulf(curr, prev_1):
    return body_length(curr) >= body_length(prev_1) * ENGULF_REAL_BODY_RATIO \
        and body_length(curr) > day_length(prev_1) > 0 \
        and body_length(curr)/day_length(curr) > ENGULF_SECOND_BODY_THRES \
        and max(curr["open"], curr["close"]) > max(prev_1["open"], prev_1["close"]) \
        and min(curr["open"], curr["close"]) < min(prev_1["open"], prev_1["close"])


def is_bullish_engulf(curr, prev_1):
    return is_white(curr) and is_black(prev_1) and is_engulf(curr, prev_1)


def is_bearish_engulf(curr, prev_1):
    return is_black(curr) and is_white(prev_1) and is_engulf(curr, prev_1)


def is_harami(curr, prev_1):
    return body_length(prev_1) > 0 and max(prev_1["open"], prev_1["close"]) > curr["high"] \
        and min(prev_1["open"], prev_1["close"]) < curr["low"]


def is_bearish_harami(curr, prev_1):
    return is_harami(curr, prev_1) and is_black(prev_1)


def is_bullish_harami(curr, prev_1):
    return is_harami(curr, prev_1) and is_white(prev_1)


def is_bearish_doji_harami(curr, prev_1):
    return is_bearish_harami(curr, prev_1) and is_doji(curr)


def is_bullish_doji_harami(curr, prev_1):
    return is_bullish_harami(curr, prev_1) and is_doji(curr)


def is_up_window(curr, prev_1):
    return curr["low"] >= prev_1["high"]


def is_down_window(curr, prev_1):
    return curr["high"] <= prev_1["low"]


def is_three_window(curr, prev_9_list, window_func):
    count = 0
    for i in range(1, len(prev_9_list)):
        if window_func(prev_9_list[i], prev_9_list[i - 1]):
            count += 1
        if count == 3:
            return True
    if count == 2 and window_func(curr, prev_9_list[-1]):
        return True
    else:
        return False


def is_three_down_window(curr, prev_9_list):
    return is_three_window(curr, prev_9_list, is_down_window)


def is_three_up_window(curr, prev_9_list):
    return is_three_window(curr, prev_9_list, is_up_window)


def is_two_black_gapping(curr, prev_1, prev_2):
    return is_down_window(prev_1, prev_2) and is_black(prev_1) and is_black(curr)


def is_bearish_gapping_doji(curr, prev_1, prev_2, doji_threshold=DOJI_THRESHOLD):
    return is_black(curr) and is_doji(prev_1, doji_threshold) and is_down_window(prev_1, prev_2)


def is_bullish_gapping_doji(curr, prev_1, prev_2, doji_threshold=DOJI_THRESHOLD):
    return is_white(curr) and is_doji(prev_1, doji_threshold) and is_up_window(prev_1, prev_2)


def is_evening_star(curr, prev_1, prev_2):
    return is_long_white(prev_2, prev_1) and min(prev_1["close"], prev_1["open"]) > prev_2["close"] and is_black(curr) \
           and min(prev_1["close"], prev_1["open"]) > curr["open"]


def is_evening_doji_star(curr, prev_1, prev_2, doji_thres=DOJI_THRESHOLD):
    return is_evening_star(curr, prev_1, prev_2) and is_doji(prev_1, doji_thres)


def is_morning_star(curr, prev_1, prev_2):
    return is_long_black(prev_2, prev_1) and max(prev_1["close"], prev_1["open"]) < prev_2["close"] and is_white(curr) \
           and max(prev_1["close"], prev_1["open"]) < curr["open"]


def is_morning_doji_star(curr, prev_1, prev_2, doji_thres=DOJI_THRESHOLD):
    return is_morning_star(curr, prev_1, prev_2) and is_doji(prev_1, doji_thres)
