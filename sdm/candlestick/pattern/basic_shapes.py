"""
This module defines the detection of the basic stick shapes
For all the methods in this module, the input is a dictionary of the daily stock price with usually 5 keys: high,
low, open, close, and volume. For CandleStick detection the first 4 keys are mandatory.
Some of the methods would require data from previous's day, or even the days before. In these cases they will be
provided in prev_n (n=1,2,3..) input parameter.
"""

from sdm.candlestick.parameters import *


"""
Following are the utility functions for shape detection
"""


def body_length(curr):
    return abs(curr["close"] - curr["open"])


def day_length(curr):
    return curr["high"] - curr["low"]


def is_white(curr):
    return curr["close"] > curr["open"]


def is_black(curr):
    return curr["close"] < curr["open"]


def is_long_body(curr, prev_1, threshold=LONG_BODY_THRESHOLD, multiplier=LONG_BODY_MULTIPLIER):
    # a long body stick would have a high/low very close to the close, and the low/high very close to the open.
    # Another important thing is that the length of body must be longer than the previous day.
    return day_length(curr) > 0 and body_length(curr) / day_length(curr) > threshold and body_length(curr) \
           > multiplier * body_length(prev_1)


def is_long_shadow(curr, threshold=LONG_SHADOW_THRESHOLD):
    # a long shadow should be the opposite of long body, i.e. the shadow part shuold be the majority of the day length,
    # but there is not a limit on the shadow length over the previous day
    return day_length(curr) > 0 and (day_length(curr) - body_length(curr)) / day_length(curr) > threshold


def is_long_upper_shadow(curr, long_thres=LONG_SHADOW_THRESHOLD, short_thres=SHORT_SHADOW_THRESHOLD):
    # the long shadow is on the top, so the lower of the open/close price should be very close to the low price
    # This indicates a bearish market after price is going up
    return is_long_shadow(curr, long_thres) and (min(curr["open"], curr["close"]) - curr["low"]) / day_length(curr) < \
           short_thres


def is_long_lower_shadow(curr, long_thres=LONG_SHADOW_THRESHOLD, short_thres=SHORT_SHADOW_THRESHOLD):
    # the long shadow is at the bottom, so the higher of the open/close price should be extremly close to the high
    # This indicates a bullish market after price is going down
    return is_long_shadow(curr, long_thres) and (curr["high"] - max(curr["open"], curr["close"])) / day_length(curr) < \
           short_thres


"""
Following are the basic candlestick patterns definition
"""


def is_long_white(curr, prev_1, threshold=LONG_BODY_THRESHOLD, multiplier=LONG_BODY_MULTIPLIER):
    # This is a strong buy signal if it happens while price is going down
    return is_white(curr) and is_long_body(curr, prev_1, threshold, multiplier)


def is_long_black(curr, prev_1, threshold=LONG_BODY_THRESHOLD, multiplier=LONG_BODY_MULTIPLIER):
    # This is a strong sell signal if it happens while price is going up
    return is_black(curr) and is_long_body(curr, prev_1, threshold, multiplier)


def is_doji(curr, threshold = DOJI_THRESHOLD):
    # Doji(Cross) is very similar to long shadow, but the body must be almost zero.
    # Doji by itself is not a signal for buy or sell. It tells the market is struggling. However if a doji happens after
    # a sudden rise or drop, then it is a signal of reverse.
    return day_length(curr) > 0 and body_length(curr) / day_length(curr) < threshold


def is_gravestone(curr, doji_thres=DOJI_THRESHOLD, long_thres=LONG_SHADOW_THRESHOLD,
                  short_thres=SHORT_SHADOW_THRESHOLD):
    # Gravestone is a specialcase of doji. It is basically a doji without lower shadow at all.
    # When this happens when price is going up, this is a very strong signal for sell, or do NOT buy
    return is_doji(curr, doji_thres) and is_long_upper_shadow(curr, long_thres, short_thres)


def is_hammer(curr, prev_1, long_thres=LONG_SHADOW_THRESHOLD, short_thre=SHORT_SHADOW_THRESHOLD,
              multiplier=HAMMER_MULTIPLIER):
    # Hammer is a long lower shadow, but must be after significant dropping in price (over at least one week).
    # Also we would like the shadow part of the hammer to be long, and preferably longer than previous day.
    # It is a strong signal for buy in.
    return is_long_lower_shadow(curr, long_thres, short_thre) and day_length(curr) > day_length(prev_1) \
           * multiplier


def is_hanging_man(curr, prev_1, long_thres=LONG_SHADOW_THRESHOLD, short_thres=SHORT_SHADOW_THRESHOLD):
    # Hanging is exactly the same shape as hammer. The only difference is that it must be appearing after the price
    # has been increasing. It is a signal for selling, but not as strong as the hammer. So people suggest confirming it
    # by the next day. If the next day's close price is lower than the min(open, close) of the previous day,
    # then it is a hanging man signal.
    return is_long_lower_shadow(prev_1, long_thres, short_thres) and curr["close"] < min(
        prev_1["open"], prev_1["close"])
