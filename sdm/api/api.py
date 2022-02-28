"""
This module is the abstract class for the API calls

"""
import logging

from sdm import constants as c

from abc import ABC, abstractmethod
import requests
import csv


class API(ABC):

    def __init__(self, base_url, token, market, response_format):
        self._base_url = base_url
        self._token = token
        if market.lower() not in c.MARKETS:
            raise ValueError("Market {} is not supported yet! We only support the following markets: {}"
                             .format(market, c.MARKETS))
        self._market = market.lower()
        if response_format not in c.RESPONSE_FORMATS:
            raise ValueError("Response format {} is not supported yet! We only support the following formats: {}"
                             .format(response_format, c.RESPONSE_FORMATS))
        self._format = response_format
        self._symbol_list = None

    def _call_url(self, suffix):
        response = requests.get(self._base_url + suffix)
        if self._format == 'json':
            return response.json()
        elif self._format == 'csv':
            return csv.reader(response.text.splitlines())
        else:
            raise ValueError("Not Recognized Format!")

    def get_url(self, suffix):
        return self._base_url + suffix

    def get_daily_historical_all(self, start_date=c.EARLIEST_DATE, end_date=c.LATEST_DATE):
        """
        Return the daily historical data for all symbols in the current market.
        :param start_date: Datetime object which defines the start date of the data to request.
        :param end_date: Datetime object which defines the end date of the data to request.
        :return: A dict with symbol name as the key. Each item is an OrderedDict object with datetime object as its own
        key. Each item in this OrderedDict is the stock data of this date as another dict.
        """
        symbol_list = self.get_symbol_list()
        result = {}
        for symbol in symbol_list:
            if symbol in result:
                logging.warning("Duplicate found on symbol {}. Skipping this request.".format(symbol))
            else:
                symbol_data = self.get_daily_historical_per_symbol(symbol, start_date, end_date)
                if symbol_data is None:
                    continue
                result = {**result, **symbol_data}
        return result

    @abstractmethod
    def get_daily_historical_per_symbol(self, symbol, start_date=c.EARLIEST_DATE, end_date=c.LATEST_DATE):
        """
        Return the daily historical data for a symbol.
        :param symbol: symbol name for the stock. Case insensitive.
        :param start_date: Datetime object which defines the start date of the data to request.
        :param end_date: Datetime object which defines the end date of the data to request.
        :return: A dict with symbol name as the key. The value is an OrderedDict object with datetime object as its own
        key. Each item in this OrderedDict is the stock data of this date as another dict.
        """
        raise NotImplementedError

    def get_symbol_list(self):
        """
        Get all the symbols available in the current market. The symbols will be distinct.
        :return: A list of symbol name in string format. Each value will only appear once.
        """
        if self._symbol_list is None:
            self._symbol_list = self.get_symbol_list_internal()
        return self._symbol_list

    @abstractmethod
    def get_symbol_list_internal(self):
        """
        Get all the symbols available in the current market. The symbols will be distinct.
        :return: A list of symbol name in string format. Each value will only appear once.
        """
        raise NotImplementedError

    @abstractmethod
    def get_previous_day_closing(self):
        """
        Get the previous closing price for all symbols in the market.
        :return: A dict with keys as the symbol name, and value as the previous closing price.
        """
        raise NotImplementedError

    @abstractmethod
    def get_previous_day_full_price(self):
        """
        Get the full price for previous day on all symbols in the market.
        :return: A dict with keys as the symbol name, and value is another dict with stock data from the previous day
        """
        raise NotImplementedError

    @abstractmethod
    def get_realtime_quote_per_symbol(self, symbol):
        """
        Get the realtime quote for a symbol.
        :param symbol: symbol name. Case insensitive.
        :return: A dict with key as the symbol name, and the item is another dict of price data.
        """
        raise NotImplementedError

    @abstractmethod
    def get_realtime_quote_all(self):
        """
        Get the real time quotes for all symbols in the market
        :return: A dict with key as the symbol name, and the item is another dict of price data
        """
        raise NotImplementedError


    class InvalidSymbolError(Exception):
        """
        Raised when the symbol is not found in FMP
        """
        pass
