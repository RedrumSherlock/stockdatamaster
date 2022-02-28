from sdm.util.date_utils import datetime_to_string


class Transaction:
    def __init__(self, action, symbol, amount, price, datetime):
        self.amount = amount
        self.symbol = symbol
        self.action = action
        self.price = price
        self.datetime = datetime

    def get_action_name(self):
        return "buy" if self.action > 0 else "sell" if self.action < 0 else "hold"

    def is_buy(self):
        return self.action > 0

    def is_sell(self):
        return self.action < 0

    def to_dict(self):
        return {"datetime": datetime_to_string(self.datetime),
                "action": self.get_action_name(),
                "symbol": self.symbol,
                "amount": self.amount,
                "price": self.price}

    @property
    def amount(self):
        return self._amount

    @amount.setter
    def amount(self, amount):
        if not isinstance(amount, int) or amount < 0:
            raise ValueError("Incorrect amount {} is assigned to a transaction!".format(amount))
        self._amount = amount

    @property
    def symbol(self):
        return self._symbol

    @symbol.setter
    def symbol(self, symbol):
        self._symbol = symbol.upper()

    @property
    def action(self):
        return self._action

    @action.setter
    def action(self, action):
        if action not in [-1, 0, 1]:
            raise ValueError("action given {} is invalid. Must be one of these: -1, 0, 1".format(action))
        self._action = action

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, price):
        if price < 0:
            raise ValueError("Incorrect price {} is assigned to a transaction!".format(price))
        self._price = price
