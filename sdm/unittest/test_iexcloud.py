from sdm.api.iex_cloud import IEXCloudAPI
from sdm.util.io_utils import get_token

import unittest


class TestSymbol(unittest.TestCase):

    def test_previous_price_market(self):
        token = get_token("iex_cloud")
        iex_caller = IEXCloudAPI(token) # replace with your API key
        response = iex_caller.get_previous_day_market_price()
        symbol_list = []
        # Check for values
        for symbol_data in response:
            if "symbol" not in symbol_data or "open" not in symbol_data or "volume" not in symbol_data or \
                "close" not in symbol_data or "high" not in symbol_data or "low" not in symbol_data or \
                    symbol_data["high"] is None or symbol_data["low"] is None or symbol_data["open"] is None or \
                    symbol_data["close"] is None or symbol_data["volume"] is None \
                    or symbol_data["high"] < symbol_data["low"]:
                raise ValueError("Something is wrong about this {}".format(symbol_data))

            if symbol_data["symbol"] in symbol_list:
                raise ValueError("Duplicate symbol found for {}!".format(symbol_data["symbol"]))
            symbol_list.append(symbol_data["symbol"])


if __name__ == '__main__':
    unittest.main()
