import logging
from collections import OrderedDict

from sdm.util.date_utils import date_to_string
from sdm.util.market_utils import is_open_day, USTradingCalendar, CATradingCalendar
from sdm.util.misc_utils import transpose_dict

import datetime as dt


class Market:

    def __init__(self, market_historical_data, market_type, start_date, end_date):
        """
        Initializer
        :param market_historical_data: The common data format used in all SDM modules. A dict with symbol as the key,
        and the value is an OrderedDict with datetime as the key. The value of datetime key is another dict with stock
        data.
        :param start_date: a datetime.datetime object for the start date to simulate
        :param end_date: a datetime.datetime object for the end date to simulate
        :param market_type: 'nyse', 'nasdaq', or 'tsx'
        """
        self._start_date = start_date
        self._end_date = end_date
        if self._start_date >= self._end_date:
            raise ValueError("Start date {} must be less than end date {}".format(
                date_to_string(start_date), date_to_string(end_date)))
        self._current_day = start_date

        self._market_type = market_type
        if market_type == "tsx":
            inst = CATradingCalendar()
        else:
            inst = USTradingCalendar()
        self._holidays = inst.holidays(self._start_date, self._end_date)

        # In case the start date is not an open date, we forward it to the next open day
        while not is_open_day(self._current_day, self._market_type, self._holidays):
            self._current_day += dt.timedelta(days=1)

        self._market_data_cumulative = OrderedDict()
        if market_historical_data is not None and len(market_historical_data) > 0:
            logging.info("Transposing historical data dict, this might take a while...")
            self._historical_market_data_by_date = transpose_dict(market_historical_data)
            logging.info("Historical data dict has been transposed.")

        self._traders = []

    def reset(self):
        self._market_data_cumulative = {}
        self._current_day = self._start_date

    def is_the_end(self):
        return self._end_date <= self._current_day

    def has_data_for_date(self, date):
        return date in self._market_data_cumulative

    def append_data_for_date(self, data, date):
        if date not in self._market_data_cumulative or self._market_data_cumulative[date] is None or \
                len(self._market_data_cumulative[date]) == {}:
            self._market_data_cumulative[date] = data

    def get_today_data(self):
        if self.has_data_for_date(self._current_day):
            return self._market_data_cumulative[self._current_day]
        else:
            raise ValueError("Market does not have data for today {} yet! Please append it first.".format(
                self._current_day))

    def get_current_day(self):
        return self._current_day

    def refresh_indicators(self):
        # TODO: this is supposed to refresh any indicator of the market, like index, moving avg line, etc.
        pass

    def add_trader(self, trader):
        self._traders.append(trader)

    def clear_all_traders(self):
        self._traders.clear()

    def get_traders(self):
        return self._traders

    def make_trades(self, real_time_price=None):
        if real_time_price is None:
            self.append_data_for_today()
        all_transactions = []
        for trader in self._traders:
            transactions = trader.make_trades(self._market_data_cumulative, self._current_day, real_time_price)
            all_transactions.append(transactions)
        return all_transactions

    def forward_one_day(self, today_close_quote=None):
        self.append_data_for_today(today_close_quote)
        self._current_day += dt.timedelta(days=1)
        while not is_open_day(self._current_day, self._market_type, self._holidays):
            self._current_day += dt.timedelta(days=1)
        self.refresh_indicators()

    def append_data_for_today(self, today_close_quote=None):
        if self._current_day in self._market_data_cumulative:
            return

        # We don't have today's data. We need to append it if we have today's close quote as input
        if today_close_quote is not None:
            self.append_data_for_date(today_close_quote, self._current_day)
            return

        # If we don't have today's realtime quote, we can try to append from historical data
        if self._historical_market_data_by_date is not None and self._current_day in \
                self._historical_market_data_by_date:
            self.append_data_for_date(self._historical_market_data_by_date[self._current_day],
                                      self._current_day)
        else:
            raise ValueError("No data for today {} can be found from historical data provided!".format(
                self._current_day))

    def trade_and_forward(self, today_close_quote=None):
        self.make_trades()
        self.forward_one_day(today_close_quote)
