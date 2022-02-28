"""
This module is responsible for implementing the Alpha Vantage API calls

"""
import logging
from collections import OrderedDict

from sdm.util.date_utils import date_difference, get_current_datetime, string_to_date
from sdm.api.api import API
from sdm import constants as c


class IEXCloudAPI(API):

    def __init__(self, token, market, response_format="json"):
        if market == 'tsx':
            raise ValueError("TSX is not supported by IEX cloud API!")
        super().__init__(c.IEX_CLOUD_BASE_URL, token, market, response_format)
        self._date_key = "date"
        self._symbol_key = "symbol"
        self._exchange_key = "exchange"
        self._timestamp_key = "iexLastUpdated"
        self._previous_close_key = "close"
        self._quote_key = "quote"

    def get_daily_historical_per_symbol(self, symbol, start_date=c.EARLIEST_DATE, end_date=c.LATEST_DATE):
        days_diff = date_difference(start_date, get_current_datetime())
        if days_diff < 5:
            date_range = "5d"
        elif days_diff < 29:
            date_range = "1m"
        elif days_diff < 89:
            date_range = "3m"
        elif days_diff < 6 * 30:
            date_range = "6m"
        elif days_diff < 365:
            date_range = "1y"
        elif days_diff < 2 * 365:
            date_range = "2y"
        elif days_diff < 5 * 365:
            date_range = "5y"
        else:
            date_range = "max"
        print(date_range)
        suffix = "stock/{}/chart/{}?".format(symbol, date_range)
        suffix = suffix + "token=" + self._token
        raw_response = super()._call_url(suffix)

        logging.info("Successfully loaded all the daily data for symbol {}".format(symbol))

        try:
            response = self.convert_historical_response(raw_response, start_date, end_date)
            logging.info("Symbol {} has {} entries loaded".format(symbol, len(response)))
        except self.InvalidSymbolError:
            logging.error("    FAILED to load URL: " + self.get_url(suffix))
            return None

        return {symbol: response}

    def get_previous_day_full_price(self):
        """
        Get the full price for previous day on all symbols in the market.
        :return: A dict with keys as the symbol name, and value is another dict with stock data from the previous day
        """
        suffix = "stock/market/previous?"
        suffix = suffix + "token=" + self._token
        raw_response = super()._call_url(suffix)
        result = {}
        if raw_response is None or len(raw_response) == 0:
            raise ValueError("Got empty result from IEX cloud for market previous price on url {}".format(
                self.get_url(suffix)))
        market_symbol_list = self.get_symbol_list()
        date_list = [item[self._date_key] if self._date_key in item else None for item in raw_response]
        # Get the most common date because some symbols do not have data for previous day
        date = max(set(date_list), key=date_list.count)
        for symbol_data in raw_response:
            if self._symbol_key not in symbol_data or self._date_key not in symbol_data \
                    or symbol_data[self._date_key] != date:
                continue
            symbol = symbol_data[self._symbol_key]
            if symbol in market_symbol_list:
                self._remove_kv_pairs_from_dict(symbol_data,
                                                [self._symbol_key, self._date_key, "id", "key", "subkey", "label"])
                result[symbol] = symbol_data
        logging.info("Successfully loaded full prices from previous day {}".format(date))
        return result

    def get_symbol_list_internal(self):
        if self._market == "tsx":
            raise NotImplementedError("TSX is not supported by IEX cloud")
        else:
            suffix = "ref-data/symbols?"
        suffix = suffix + "token=" + self._token
        raw_response = super()._call_url(suffix)
        result = []
        for symbol_item in raw_response:
            if self._symbol_key in symbol_item and self._exchange_key in symbol_item \
                    and symbol_item[self._exchange_key].lower().startswith(self._market[0:3]):
                result.append(symbol_item[self._symbol_key])
        return list(set(result))

    def get_previous_day_closing(self):
        quote_data = self.get_previous_day_full_price()
        result = {}
        for symbol in quote_data:
            if self._previous_close_key in quote_data[symbol]:
                result[symbol] = quote_data[symbol][self._previous_close_key]
        return result

    def get_realtime_quote_per_symbol(self, symbol):
        suffix = "stock/{}/quote?token={}".format(symbol.upper(), self._token)
        raw_response = super()._call_url(suffix)
        if raw_response is None or len(raw_response) == 0:
            logging.error("Error! Not able to pull any realtime quote data for symbol {}".format(symbol))
        if self._symbol_key in raw_response:
            del raw_response[self._symbol_key]
        raw_response[c.DATETIME_KEY] = get_current_datetime()
        self._remove_kv_pairs_from_dict(raw_response,
                                        ["companyName", "primaryExchange", "isUSMarketOpen", self._timestamp_key])
        return {symbol: raw_response}

    def get_realtime_quote_all(self):
        market_symbol_list = self.get_symbol_list()
        all_raw_responses = {}
        batch_num = 0
        batch_symbols = ""
        for symbol in market_symbol_list:
            batch_symbols += symbol + ","
            batch_num += 1
            if batch_num == c.IEX_CLOUD_BATCH_LIMIT:
                suffix = "stock/market/batch?symbols={}&types=quote&token={}".format(batch_symbols[:-1], self._token)
                raw_response = super()._call_url(suffix)
                all_raw_responses.update(raw_response)
                batch_num = 0
                batch_symbols = ""
        return self.convert_realtime_quote_response(all_raw_responses)

    def convert_realtime_quote_response(self, data):
        realtime_response = {}
        for (symbol, symbol_data) in data.items():
            if self._quote_key not in symbol_data:
                continue
            self._remove_kv_pairs_from_dict(symbol_data[self._quote_key], [self._symbol_key])
            realtime_response[symbol] = symbol_data[self._quote_key]
        return realtime_response

    def convert_historical_response(self, data, start_date=c.EARLIEST_DATE, end_date=c.LATEST_DATE):
        result = {}
        for record in data:
            if self._date_key in record:
                date = string_to_date(record[self._date_key], c.IEX_CLOUD_DATE_FORMAT)
                # For historical data we can only do it for one symbol each call, so there cannot be two entries with
                # the same date
                if date in result:
                    logging.warning("Duplicate date {} found in the IEX Cloud Historical Data for symbol {}. "
                                    "Skipping this record.".format(record[self._date_key], record["symbol"]))
                elif start_date <= date <= end_date:
                    date_values = dict(record)
                    del date_values[self._date_key]
                    self._remove_kv_pairs_from_dict(date_values, ["id", "key", "subkey", "label", self._symbol_key])
                    result[date] = date_values
        return OrderedDict(sorted(result.items()))

    @staticmethod
    def _remove_kv_pairs_from_dict(dict_obj, key_list):
        for key in key_list:
            if key in dict_obj:
                del dict_obj[key]
