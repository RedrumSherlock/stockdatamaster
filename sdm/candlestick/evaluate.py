"""
This module evaluate the pattern detection in historical data
"""
import logging

from sdm.util.date_utils import date_to_string
from sdm.candlestick.parameters import RSI_N

import plotly.graph_objects as go
from inspect import signature


def make_plot_dict(datetime):
    date_text = date_to_string(datetime)
    return dict(x0=date_text, x1=date_text, y0=0, y1=1, xref='x', yref='paper', line_width=2)


def plot_candlestick(symbol, input_dict, detection_func, pattern_name="Candlestick Pattern", y_range=[0,100]):
    """
    :param input_dict: stock data for only ONE symbol. It should be an OrderedDict with key being a datetime
    object, and value being a dict with at least the following keys: open, close, high, low, volume
    :param detection_func: the function to detect candlestick patterns. It should take either curr, or (curr, prev_1),
    or (curr, prev_1, prev_2) as the input parameters.
    :param pattern_name: the name of the pattern we are detecting
    :param y_range: the upper and lower range for the y axis. Default is to display $0 to $100
    :return: None
    """
    if len(input_dict) < 2:
        raise ValueError("The input data should have at lease 3 days but only has {} days instead".format(
            len(input_dict)))

    result_list = []
    params = signature(detection_func).parameters
    data_list = list(input_dict.values())
    datetime_list = list(input_dict.keys())
    for i in range(len(data_list)):
        if i > 1:
            if "prev_9_list" in params:
                found = detection_func(data_list[i], data_list[i - 10:i - 1]) if i > 9 else False
            elif "prev_2" in params:
                found = detection_func(data_list[i], data_list[i-1], data_list[i-2])
            elif "prev_1" in params:
                found = detection_func(data_list[i], data_list[i-1])
            else:
                found = detection_func(data_list[i])

            if found:
                result_list.append(make_plot_dict(datetime_list[i]))

    logging.info("Found {} {} in stock price history".format(len(result_list), pattern_name, symbol))

    fig = go.Figure(data=[go.Candlestick(x=datetime_list,
                                         open=[entry["open"] for entry in data_list],
                                         high=[entry["high"] for entry in data_list],
                                         low=[entry["low"] for entry in data_list],
                                         close=[entry["close"] for entry in data_list],
                                         increasing_line_color='white', decreasing_line_color='black')])
    fig.update_layout(
        title=f'{pattern_name} Charts',
        plot_bgcolor='grey',
        yaxis_title=f'{symbol} Stock',
        shapes=result_list,
        yaxis1={"range": y_range}
    )
    fig.show()


def eval_gain_loss(input_data, shape_func, trend_func, threshold_tuple=(), trend_tuple=(),
                   days_after=20, gain_loss_threshold=0.15):
    """
    :param input_data: stock data for any number of symbols. It should be a dict with symbol being the key, and value
     is an OrderedDict with datetime as key. The value of the OrderedDict is another dict with at least the following
     keys: open, close, high, low, volume
    :param shape_func: the function we want to use for candlestick function shape. It CAN be None. When it is none we
    simply ignore the candlestick detection result, i.e. we default the shape detection to be always true
    :param trend_func: the function we want to use for trend detection. It CAN be None. When it is none we
    simply ignore the trend detection result, i.e. we default the trend detection to be always true
    :param threshold_tuple: optional if you want to send specific thresholds for the candlestick detection other than
    the default ones we chose
    :param trend_tuple: optional if you want to send specific parameters for trend detection other than the default
    :param days_after: within how many days do we evaluate the performance of gain/loss/raise/drop
    :param gain_loss_threshold: when above/below this threshold within certain days we consider it to be a raise/drop
    :return: A tuple (detected, avg_gain, avg_loss, perc_raised, perc_dropped). detected - the number of pattern/trend
    combo detected. avg_gain: - the average of max gains within certain days. avg_loss - the average of max losses
    within certain days. perc_raised - the percentage of raised within certain days among the detected. perc_dropped -
    the percentage of dropped within certain days among the detected.
    """

    detected = 0
    max_gain = 0
    max_loss = 0
    raised = 0
    dropped = 0

    if shape_func is None and trend_func is None:
        raise ValueError("You must pick at least one function for either candlestick detection or trend detection!")

    shape_params = signature(shape_func).parameters if shape_func is not None else None
    trend_params = signature(trend_func).parameters if trend_func is not None else None

    for symbol in input_data:
        symbol_data = list(input_data[symbol].values())
        # We only evaluate symbols with more than 40 days of data, because we need 20 days to determine the trend
        # and we need 20 days to determine if we got the correct prediction
        if len(symbol_data) > 20 + days_after:
            for i in range(20, len(symbol_data) - days_after):
                curr = symbol_data[i]
                prev_1 = symbol_data[i - 1]
                prev_2 = symbol_data[i - 2]
                prev_5 = symbol_data[i - 5]
                prev_10 = symbol_data[i - 10]
                prev_20 = symbol_data[i - 20]

                if shape_func is None:
                    shape_match = True
                else:
                    if "prev_9_list" in shape_params:
                        shape_match = shape_func(curr, symbol_data[i-10:i-1], *threshold_tuple)
                    elif "prev_2" in shape_params:
                        shape_match = shape_func(curr, prev_1, prev_2, *threshold_tuple)
                    elif "prev_1" in shape_params:
                        shape_match = shape_func(curr, prev_1, *threshold_tuple)
                    else:
                        shape_match = shape_func(curr, *threshold_tuple)

                if trend_func is None:
                    trend_match = True
                else:
                    # We only support simple and RSI approaches here
                    if "prev_5" in trend_params and "prev_10" in trend_params and "prev_20" in trend_params:
                        trend_match = trend_func(curr, prev_5, prev_10, prev_20, *trend_tuple)
                    else:
                        trend_match = trend_func(curr, symbol_data[i - RSI_N:i], *trend_tuple)

                if shape_match and trend_match:
                    detected += 1
                    max_after = max(d["high"] for d in symbol_data[i + 1:i + days_after])
                    min_after = min(d["low"] for d in symbol_data[i + 1:i + days_after])
                    max_gain += max_after / curr["close"] - 1
                    max_loss += min_after / curr["close"] - 1
                    signal = first_signal(symbol_data[i + 1:i + days_after], curr["close"], gain_loss_threshold)
                    if signal == 1:
                        raised += 1
                    if signal == -1:
                        dropped += 1

    if detected == 0:
        return 0, 0, 0, 0, 0
    else:
        return (detected, round(max_gain / detected, 4), round(max_loss / detected, 4), round(raised / detected, 4),
                round(dropped / detected, 4))


def first_signal(stock_data, base_price, gain_loss_threshold):
    """
    This function detects the first market signal after certain days. If the price went above the threshold we set
    return 1. If the price went below we return -1. If the price did not go either way we return 0
    :param stock_data: a list of dicts. each dictionary needs to have the keys: high, low
    :param base_price: a number with regards the base price we are comparing to
    :param gain_loss_threshold: a percentage we set to be the sell/buy point
    :return: 1, 0, or -1
    """
    for d in stock_data:
        if d["high"] > base_price * (1 + gain_loss_threshold):
            return 1
        if d["low"] < base_price * (1 - gain_loss_threshold):
            return -1
    return 0
