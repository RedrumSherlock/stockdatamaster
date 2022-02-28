import logging

from sdm.util.date_utils import date_to_string

import matplotlib.pyplot as plt
import numpy as np

DEFAULT_COMMISSION_FLAT_FEE = 0
REALTIME_PRICE_KEY = "price"


def default_commission(transaction):
    if transaction.action < 0 and transaction.price * transaction.amount < DEFAULT_COMMISSION_FLAT_FEE:
        return 0
    return DEFAULT_COMMISSION_FLAT_FEE


class Trader:

    def __init__(self, strategy_function, init_fund, start_date, end_date, commission_calc_func=default_commission,
                 name="Default Trader"):
        """
        The trader is an individual trader that performs its own tradings in the market object.
        :param strategy_function: a function to decide whether to make a trade, on which symbol, to buy or sell for
        what volume. This should be a generator function that yields Transaction objects representing the transactions
        to be made, based on the current day's market data (or real time price if available), the cumulative market
        data up to today, current position, total cash, and its trading history.
        :param init_fund: the total cash this trader initially has
        :param start_date: a datetime object for the start date of trading
        :param end_date: a datetime object for the end date of trading
        :param commission_calc_func: A function that takes price and volume to calculate the commission fee. Default
        is $7 per transaction
        :param name:
        """

        if not callable(strategy_function):
            raise ValueError("Variable strategy_function must be a function, but passed in as {} instead".format(
                type(strategy_function)))
        self._func = strategy_function
        self._start_date = start_date
        self._end_date = end_date
        self._current_day = start_date
        self._init_fund = init_fund
        self.cash = init_fund
        self._name = name
        self._position = {}
        self._latest_close_price = {}
        self.commission_calc_func = commission_calc_func
        self._transaction_history = []

    def reset(self):
        self._current_day = self._start_date
        self.cash = self._init_fund
        self._position = {}
        self._latest_close_price = {}
        self._transaction_history = []

    def set_func(self, func):
        self._func = func

    @property
    def cash(self):
        return self._cash

    @cash.setter
    def cash(self, cash):
        if cash < 0:
            raise ValueError("Cash must be a positive number but given {}".format(cash))
        self._cash = cash

    def is_valid_transaction(self, transaction, current_price):
        if transaction.action > 0 and transaction.price < current_price:
            logging.error("Error: you try to buy {} at price {} but the market lowest price is {}. Skipping.".format(
                transaction.symbol, transaction.price, current_price))
            return False
        if transaction.action < 0 and transaction.price > current_price:
            logging.error("Error: you try to sell {} at price {} but the market highest price is {}. Skipping.".format(
                transaction.symbol, transaction.price, current_price))
            return False

        if transaction.action > 0 and self.cash < transaction.amount * transaction.price + self.commission_calc_func(
                transaction):
            logging.error("Error: you only have cash of {}, which is not enough to buy {} stocks of {} at price {} "
                          "with commission {}".format(self.cash, transaction.amount, transaction.symbol,
                                                      transaction.price, self.commission_calc_func(transaction)))
            return False
        if transaction.action < 0 and self._position[transaction.symbol] < transaction.amount:
            logging.error("Error: you only have {} stock of {}, which is not enough to sell for {}".format(
                self._position[transaction.symbol], transaction.symbol, transaction.amount))
            return False
        return True

    def make_trades(self, market_data_cumulative, current_day, real_time_price=None):
        if current_day < self._current_day:
            raise ValueError("CAN NOT go backwards: Current day for the trader is {} but the date to make trade is {}"
                             .format(date_to_string(self._current_day), date_to_string(current_day)))

        self._current_day = current_day
        transactions = self._func(market_data_cumulative=market_data_cumulative, current_day=current_day,
                                  position=self._position, cash=self.cash,
                                  transaction_history=self._transaction_history,
                                  real_time_price=real_time_price)
        valid_transactions = []
        for transaction in transactions:
            if real_time_price is not None:
                # If we are checking against real market data
                if transaction.symbol in real_time_price:
                    current_price = real_time_price[transaction.symbol][REALTIME_PRICE_KEY]
                else:
                    logging.error("Trying to make a transaction on symbol {} on {} but cannot find it in realtime "
                                  "price data. Skipping this transaction".format(transaction.symbol, current_day))
                    continue
            else:
                # If we are only simulating a trade, then use the previous close price as realtime price
                if transaction.symbol in market_data_cumulative[current_day]:
                    current_price = market_data_cumulative[current_day][transaction.symbol]["close"]
                    self._latest_close_price[transaction.symbol] = current_price
                elif transaction.symbol in self._latest_close_price:
                    # In case we have gap in data, we will use the previous closing price for buy/sell
                    current_price = self._latest_close_price[transaction.symbol]
                else:
                    logging.error("Trying to make a transaction on symbol {} on {} without any price data. Skipping "
                                  "this transaction".format(transaction.symbol, current_day))
                    continue

            if self.is_valid_transaction(transaction, current_price):
                logging.debug("{}ing amount {} on {} with price {}. Cash: {}".format(
                    transaction.get_action_name(), transaction.amount, transaction.symbol, transaction.price,
                    self._cash))
                self.cash -= transaction.action * (transaction.amount * current_price + transaction.action *
                                                   self.commission_calc_func(transaction))
                if transaction.symbol not in self._position:
                    self._position[transaction.symbol] = transaction.action * transaction.amount
                else:
                    self._position[transaction.symbol] += transaction.action * transaction.amount
                self._transaction_history.append(transaction)
                valid_transactions.append(transaction)
            else:
                logging.error("Invalid transaction with reason shown above. Skipping this transaction.")
        return valid_transactions

    def log_assets(self):
        logging.info("Total value of the trader {}: {} on day {}".format(self._name, self.get_total_value(),
                                                                         date_to_string(self._current_day)))

    def get_trading_history(self):
        return self._transaction_history

    def set_trading_history(self, trading_history):
        self._transaction_history = trading_history

    def get_start_date(self):
        return self._start_date

    def get_end_date(self):
        return self._end_date

    def get_name(self):
        return self._name

    def get_init_fund(self):
        return self._init_fund

    def get_position(self):
        return self._position

    def get_total_value(self):
        total_value = self.cash
        for (symbol, holds) in self._position.items():
            total_value += self._latest_close_price[symbol] * holds
        return total_value

    def plot_performance(self):
        value_history = {}
        transaction_list = []
        for transaction in self._transaction_history:
            if transaction.action > 0:
                if transaction.symbol not in value_history:
                    value_history[transaction.symbol] = (transaction.amount, transaction.amount * transaction.price)
                else:
                    (last_vol, last_value) = value_history[transaction.symbol]
                    value_history[transaction.symbol] = (transaction.amount + last_vol,
                                                         last_value + transaction.amount * transaction.price)
            else:
                (last_vol, last_value) = value_history[transaction.symbol]
                assert (transaction.amount == last_vol)
                transaction_list.append(transaction.amount * transaction.price - last_value)
                value_history[transaction.symbol] = (0, 0)

        plt.hist(np.array(transaction_list), bins=100, range=(-1000, 1000), label=self._name)
        logging.info("Trader {}: {} profitable transactions, {} non-profitable transactions".format(
            self._name, sum(x > 0 for x in transaction_list), sum(x < 0 for x in transaction_list)))
        logging.info("Trader {}: Profit from transactions is {}, Loss from transactions is {}: ".format(
            self._name, sum(x for x in transaction_list if x > 0), sum(x for x in transaction_list if x < 0)))
        logging.info("Trader {}: The mean of the transactions is {} and the standard deviation is {}".format(
            self._name, np.mean(transaction_list), np.std(transaction_list)))
        logging.info("Trader {}: Between -500 and 500 the mean is {} and the standard deviation is {}".format(
            self._name, np.mean(list(x for x in transaction_list if abs(x) < 500)),
            np.std(list(x for x in transaction_list if abs(x) < 500))))
        plt.legend(loc='upper right')
        plt.show()
