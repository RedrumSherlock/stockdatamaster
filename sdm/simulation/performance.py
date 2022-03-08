import logging
import numpy as np
from sdm.util.date_utils import date_to_string


def get_trader_performance_metrics(trader):
    if trader is None or len(trader.get_trading_history()) == 0:
        raise ValueError("No data found to produce metrics!")

    final_balance = trader.get_total_value()
    sell_buy_ratio_list = []
    profit_list = []
    hold_days_list = []
    max_loss = 0
    max_loss_transaction = None
    max_loss_bought = 0
    max_gain = 0
    max_gain_transaction = None
    max_gain_bought = 0
    last_buy_transaction = {}
    assets = trader.get_init_fund()
    lowest_assets = assets
    lowest_assets_date = trader.get_start_date()
    previous_year = trader.get_start_date().year
    previous_month = trader.get_start_date().month
    annually_asset_list = []
    monthly_asset_list = []
    monthly_transaction_times_list = []
    monthly_transaction_times = 0

    for transaction in trader.get_trading_history():

        if transaction.is_buy():
            last_buy_transaction[transaction.symbol] = transaction
            assets -= trader.commission_calc_func(transaction)
        if transaction.is_sell():
            bought_price = last_buy_transaction[transaction.symbol].price
            bought_date = last_buy_transaction[transaction.symbol].datetime
            sell_buy_ratio = transaction.price / bought_price
            sell_buy_ratio_list.append(sell_buy_ratio)
            profit_list.append(1 if sell_buy_ratio > 1 else 0)
            if max_loss < transaction.amount * (bought_price - transaction.price):
                max_loss = transaction.amount * (bought_price - transaction.price)
                max_loss_transaction = transaction
                max_loss_bought = bought_price
            if max_gain < transaction.amount * (transaction.price - bought_price):
                max_gain = transaction.amount * (transaction.price - bought_price)
                max_gain_transaction = transaction
                max_gain_bought = bought_price
            hold_days_list.append(np.busday_count(date_to_string(bought_date), date_to_string(transaction.datetime)))
            assets = assets + transaction.amount * (transaction.price - bought_price) - trader.commission_calc_func(
                transaction)
            if assets < lowest_assets:
                lowest_assets = assets
                lowest_assets_date = transaction.datetime

        while transaction.datetime.month != previous_month:
            monthly_asset_list.append(assets)
            monthly_transaction_times_list.append(monthly_transaction_times)
            monthly_transaction_times = 0
            previous_month = previous_month + 1 if previous_month < 12 else 1
        monthly_transaction_times += 1

        if transaction.datetime.year > previous_year:
            # A new year is detected. Save the asset of the previous year(s) and forward to current year.
            while transaction.datetime.year != previous_year:
                annually_asset_list.append(assets)
                previous_year += 1

    sell_buy_ratio_array = np.array(sell_buy_ratio_list)
    sell_buy_ratio_avg = np.mean(sell_buy_ratio_array, axis=0)
    sell_buy_ratio_std = np.std(sell_buy_ratio_array, axis=0)
    profit_probability = sum(profit_list) / len(profit_list)
    hold_days_array = np.array(hold_days_list)
    hold_days_avg = np.mean(hold_days_array, axis=0)
    hold_days_std = np.std(hold_days_array, axis=0)
    monthly_return_rate_array = np.array(
        [(monthly_asset_list[i] / monthly_asset_list[i - 1] - 1) * 100 for i in range(2, len(monthly_asset_list))])
    monthly_return_rate_avg = np.mean(monthly_return_rate_array, axis=0)
    monthly_return_rate_std = np.std(monthly_return_rate_array, axis=0)
    annually_return_rate_array = np.array(
        [(annually_asset_list[i] / annually_asset_list[i - 1] - 1) * 100 for i in range(2, len(annually_asset_list))])
    annually_return_rate_avg = np.mean(annually_return_rate_array, axis=0)
    annually_return_rate_std = np.std(annually_return_rate_array, axis=0)
    monthly_transaction_times_array = np.array(monthly_transaction_times_list)
    monthly_transaction_times_avg = np.mean(monthly_transaction_times_array, axis=0)

    logging.info("From {} to {}, trader {} has the performance metrics as following: ".format(
        trader.get_start_date(), trader.get_end_date(), trader.get_name()))
    logging.info("Expected return metrics:")
    logging.info("Final balance: {:.2f}".format(final_balance))
    logging.info("Final assets: {:.2f}".format(assets))
    logging.info("Average Monthly Return Rate: {:.2f}".format(monthly_return_rate_avg))
    logging.info("Average Annually Return Rate: {:.2f}".format(annually_return_rate_avg))
    logging.info("Average Sell Buy Ratio: {:.4f}".format(sell_buy_ratio_avg))
    logging.info("Risk related metrics:")
    logging.info("Profit probability of all transactions: {:.4f}".format(profit_probability))
    logging.info("Standard Deviation of Sell Buy Ratio: {:.4f}".format(sell_buy_ratio_std))
    logging.info("Standard Deviation of Monthly Return Rate: {:.2f}".format(monthly_return_rate_std))
    logging.info("Standard Deviation of Annually Return Rate: {:.2f}".format(annually_return_rate_std))
    logging.info("Max Loss over single transaction: {:.2f} of symbol {}, bought for {} and sold for {} on {}".format(
        max_loss, max_loss_transaction.symbol, max_loss_bought, max_loss_transaction.price,
        max_loss_transaction.datetime))
    logging.info("Lowest Total Asset was {} at Date {}".format(lowest_assets, lowest_assets_date))
    logging.info("Other metrics:")
    logging.info("Average Monthly Transaction Times: {:.2f}".format(monthly_transaction_times_avg))
    logging.info("Average Hold Days: {:.2f}".format(hold_days_avg))
    logging.info("Standard Deviation of Hold Days: {:.2f}".format(hold_days_std))
    logging.info("Max Gain over single transaction: {:.2f} of symbol {}, bought for {} and sold for {} on {}".format(
        max_gain, max_gain_transaction.symbol, max_gain_bought, max_gain_transaction.price,
        max_gain_transaction.datetime))
    logging.info("Minimal and Maximum Monthly Return Rate: {:.2f}, {:.2f}".format(np.min(monthly_return_rate_array),
                                                                                  np.max(monthly_return_rate_array)))

    alpha_score = 0.8 * monthly_return_rate_avg + 0.2 * (sell_buy_ratio_avg - 1) * 100
    beta_score = 0.7 * sell_buy_ratio_std / sell_buy_ratio_avg * 100 + 0.3 * (
            monthly_return_rate_std / monthly_return_rate_avg) * 100
    logging.info("Final Score: Alpha {:.2f} (Higher the better), Beta {:.2f} (Lower the better), "
                 "Profit Probability {:.2f}".format(alpha_score, beta_score, profit_probability))
    return alpha_score, beta_score, profit_probability
