from .api import API
from sdm import constants as c
from sdm.util.date_utils import string_to_date, date_to_string, trunc_today, timestamp_to_datetime

from collections import OrderedDict
import datetime as dt
import logging


class FMPAPI(API):

    def __init__(self, token, market, response_format="json"):
        super().__init__(c.FMP_BASE_URL, token, market, response_format)
        self._date_key = "date"
        self._symbol_key = "symbol"
        self._exchange_key = "exchange"
        self._timestamp_key = "timestamp"
        self._previous_close_key = "previousClose"

    def get_daily_historical_per_symbol(self, symbol, start_date=c.EARLIEST_DATE, end_date=c.LATEST_DATE):

        # Can only get up to today
        if end_date >= trunc_today():
            end_date = trunc_today() - dt.timedelta(days=1)

        suffix = "historical-price-full/"
        suffix = suffix + symbol.upper() + "?"
        suffix = suffix + "from=" + date_to_string(start_date) + "&"
        suffix = suffix + "to=" + date_to_string(end_date) + "&"
        suffix = suffix + "apikey=" + self._token
        raw_response = super()._call_url(suffix)

        logging.info("Successfully loaded all the daily data for symbol {}".format(symbol))

        try:
            if "historical" not in raw_response:
                return None
            response = self.convert_historical_response(raw_response["historical"], start_date, end_date)
            logging.info("Symbol {} has {} entries loaded".format(symbol, len(response)))
        except self.InvalidSymbolError:
            logging.error("    FAILED to load URL: " + self.get_url(suffix))
            return None

        return {symbol: response}

    def get_symbol_list_internal(self):
        if self._market == "tsx":
            suffix = "symbol/available-tsx?"
        else:
            suffix = "stock/list?"
        suffix = suffix + "apikey=" + self._token
        raw_response = super()._call_url(suffix)
        result = []
        for symbol_item in raw_response:
            if self._symbol_key in symbol_item and \
                    (self._market == "tsx" or (self._exchange_key in symbol_item
                                               and symbol_item[self._exchange_key].lower().startswith(self._market))):
                result.append(symbol_item[self._symbol_key])
        return list(set(result))

    def get_previous_day_closing(self):
        quote_data = self.get_realtime_quote_all()
        result = {}
        for symbol in quote_data:
            if self._previous_close_key in quote_data[symbol]:
                result[symbol] = quote_data[symbol][self._previous_close_key]
        return result

    def get_previous_day_full_price(self):
        raise NotImplementedError("Getting full price for the previous day is not supported by FMP!")

    def get_realtime_quote_per_symbol(self, symbol):
        suffix = "quote/" + symbol.upper() + "?apikey=" + self._token
        raw_response = super()._call_url(suffix)
        result = {}
        if raw_response is None or len(raw_response) == 0:
            logging.error("Error! Not able to pull any realtime quote data for symbol {}".format(symbol))
        else:
            result = raw_response[0]
        if self._symbol_key in result:
            del result[self._symbol_key]
        if self._timestamp_key in result:
            result[c.DATETIME_KEY] = timestamp_to_datetime(result[self._timestamp_key])
            del result[self._timestamp_key]
        return {symbol: result}

    def get_realtime_quote_all(self):
        suffix = "quotes/" + self._market + "?apikey=" + self._token
        raw_response = super()._call_url(suffix)
        logging.info("Successfully loaded all {} realtime quotes for market {}".format(len(raw_response), self._market))
        result = {}
        for quote in raw_response:
            if self._symbol_key in quote:
                symbol_quote = dict(quote)
                if self._timestamp_key in symbol_quote:
                    symbol_quote[c.DATETIME_KEY] = timestamp_to_datetime(symbol_quote[self._timestamp_key])
                    del symbol_quote[self._timestamp_key]
                del symbol_quote[self._symbol_key]
                result[quote[self._symbol_key]] = symbol_quote
        return result

    def convert_historical_response(self, data, start_date=c.EARLIEST_DATE, end_date=c.LATEST_DATE):
        result = {}
        for record in data:
            if self._date_key in record:
                date = string_to_date(record[self._date_key], c.FMP_DATE_FORMAT)
                # For historical data we can only do it for one symbol each call, so there cannot be two entries with
                # the same date
                if date in result:
                    logging.warning("Duplicate date {} found in the FMP Historical Data for symbol {}. "
                                    "Skipping this record.".format(record[self._date_key], record["symbol"]))
                elif start_date <= date <= end_date:
                    date_values = dict(record)
                    del date_values[self._date_key]
                    result[date] = date_values
        return OrderedDict(sorted(result.items()))
