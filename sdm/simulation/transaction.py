from pydantic import BaseModel, field_validator, Field
import datetime as dt
from sdm.util.date_utils import datetime_to_string


class Transaction(BaseModel):
    amount: int = Field(description="the number of shares to be traded in the transaction", gt=0)
    symbol: str
    action: int
    price: float = Field(description="price of the stock in the transaction", gt=0)
    datetime: dt.datetime

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

    @field_validator("action")
    @classmethod
    def action(cls, action):
        if action not in [-1, 0, 1]:
            raise ValueError(f"action given {action} is invalid. Must be one of these: -1, 0, 1")
        return action
