"""
This module has all the hard coded global parameters for the default value in candlestick pattern detection
"""
from enum import Enum

# ----------------------------------------------------------------------------------------------------------------
# Parameters for basic shapes

# If the body length is over this percentage of the day length while meeting other criteria, it can be detected as a
# long body shape
LONG_BODY_THRESHOLD = 0.9

# If the body length is over the percentage of the previous day's body length while meeting other criteria, it can be
# detected as a long body shape
LONG_BODY_MULTIPLIER = 2.6

# If the shadow length is over this percentage of the day length while meeting other criteria, it can be detected as a
# long shadow shape
LONG_SHADOW_THRESHOLD = 0.9

# If the body length is less than this percentage of the day length while meeting other criteria, it can be detected
# as a doji
DOJI_THRESHOLD = 0.05

# If the shadow length is less than this percentage of the day length while meeting other criteria, it can be detected
# as a short shadow shape
SHORT_SHADOW_THRESHOLD = 0.1

# The hammer shape needs to have the current day length longer than the previous day, ideally by this multiplier.
# This is not clearly stated but needs to be taken into consideration
HAMMER_MULTIPLIER = 1.5


# ----------------------------------------------------------------------------------------------------------------
# Parameters for advanced shapes

# the first stick of dark cloud/piercing must be a long body, and this is the threshold for that long body
DARK_CLOUD_PIERCING_BODY_THRES = 0.8

# the second stick of engulf must be a long body, and this is the threshold for that long body
ENGULF_SECOND_BODY_THRES = 0.8

# the second engulf stick's body must be longer than the body of the first stick by a percentage
ENGULF_REAL_BODY_RATIO = 3

# ----------------------------------------------------------------------------------------------------------------
# Parameters for trend detection

# By how much percent has the price gone down from two weeks/one month/two months (10/20/40 open days) ago, it can be
# identified as a down trend
DOWN_AFTER_5_DAYS_THRES = 0.05
DOWN_AFTER_10_DAYS_THRES = 0.1
DOWN_AFTER_20_DAYS_THRES = 0.15


# By how much percent has the price gone up from two weeks/one month/two months (10/20/40 open days) ago, it can be
# # identified as an up trend
UP_AFTER_5_DAYS_THRES = 0.05
UP_AFTER_10_DAYS_THRES = 0.1
UP_AFTER_20_DAYS_THRES = 0.15


# Parameters for RSI calculation

# There are three approaches to calculate RSI
RSI_METHODS = Enum('Methods', ['simple', 'exponential', 'wilder'])

# This one is usually 12
RSI_N = 12

# the upper bound for RSI to determine a uptrend
RSI_UPPER_BOUND = 80

# the lower bound for RSI to determine a downtrend
RSI_LOWER_BOUND = 20
