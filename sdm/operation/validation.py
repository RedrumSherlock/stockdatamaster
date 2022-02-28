import sdm.constants as c
from sdm.util.date_utils import date_to_string
from sdm.util.market_utils import USTradingCalendar, shift_open_days, CATradingCalendar
from sdm.util.misc_utils import is_float
import logging


def validate_realtime_data(data, validation_level=c.DEFAULT_DATA_VALIDATION_LEVEL):
    """
    Validate the realtime data. Since there is only one datetime for each record, we will not perform any level 3
    validation even if specified
    :param data: realtime data as a dict with symbol as the key, and the value being a dict for the data of the symbol
    :param validation_level: the data validation level from 0 to 2, with 0 being no validation and 2 as the most
    intrusive validation.
    :return: True if there is not any error, else False.
    """
    result = True
    for symbol in data:
        if c.DATETIME_KEY not in data[symbol]:
            result = False
            logging.error("Datetime key {} not found for symbol".format(c.DATETIME_KEY, symbol))
        datetime = data[symbol][c.DATETIME_KEY]
        result = _validate_single_record(data[symbol], symbol, datetime, validation_level) and result

    if result:
        logging.info("Passed validation level {}".format(validation_level))
    return result


def validate_historical_data(data, market, validation_level=c.DEFAULT_DATA_VALIDATION_LEVEL):
    """

    :param data: the historical data used in sdm. Should be a dict with symbol as the key, and the value is an
    OrderedDict with datetime object as ordered key, with its own value being the stock data as another dict.
    :param validation_level: the data validation level from 0 to 3, with 0 being no validation and 3 as the most
    intrusive validation.
    :return: True if there is not any error, else False.
    """
    if market not in c.MARKETS:
        raise ValueError("Market must be provided for historical data validation and must be one of the following: {}"
                         .format(c.MARKETS))

    result = True

    if validation_level >= 3:
        if market in ["nasdaq", "nyse"]:
            holidays = USTradingCalendar().holidays(c.EARLIEST_DATE, c.LATEST_DATE)
        if market == "tsx":
            holidays = CATradingCalendar().holidays(c.EARLIEST_DATE, c.LATEST_DATE)

    for symbol in data:
        symbol_data = data[symbol]
        previous_datetime = None
        for datetime in symbol_data:
            # First validate level 1 & 2
            result = _validate_single_record(symbol_data[datetime], symbol, datetime, validation_level) and result

            if validation_level >= 3:
                # for validation level >= 3, we check for gap or closed day in dates
                if previous_datetime is not None:
                    next_open_date = shift_open_days(previous_datetime, 1, market, holidays)
                    if next_open_date.date() != datetime.date():
                        logging.warning("Gap or closed date found! The next open date after {} should be {}, "
                                        "but is {} instead for symbol {}".format(date_to_string(previous_datetime),
                                                                                 date_to_string(next_open_date),
                                                                                 date_to_string(datetime), symbol))
                        result = False
            previous_datetime = datetime
    if result:
        logging.info("Passed validation level {}".format(validation_level))
    return result


def _validate_single_record(record, symbol, datetime, validation_level):
    result = True
    for column in c.BASE_COLUMNS:
        if validation_level >= 1:
            # for validation level >= 1, we verify that the base columns (open, close, high, low, volume) are
            # not None and are actually valid numbers
            if column not in record:
                logging.warning("Column {} for symbol {} on {} is not existing".format(
                    column, symbol, date_to_string(datetime)))
                result = False
                break
            if record[column] is None or not is_float(record[column]) or float(record[column]) < 0:
                logging.warning("Column %s for symbol %s on %s has invalid value: {}".format(
                    column, symbol, date_to_string(datetime), record[column]))
                result = False
                break

        if validation_level >= 2:
            # for validation level >= 2, we also verify that the number of high/low are actually the highest/lowest
            if record["low"] > min(record["open"], record["close"]) or record["high"] < max(record["open"],
                                                                                            record["close"]):
                logging.warning("Incorrect low/high value in the data for symbol {} on date {}: {}".format(
                    symbol, date_to_string(datetime), record))
                result = False
    return result
