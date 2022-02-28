from sdm.api.fmp import FMPAPI
from sdm.util.io_utils import get_token

import unittest


class TestSymbol(unittest.TestCase):

    def test_single_symbol(self):
        token = get_token("fmp")
        fmp_caller = FMPAPI(token) # replace with your API key
        response = fmp_caller.get_real_time_price(market='nasdaq')
        symbol_list = []
        # Check for values
        for symbol_data in response:
            if "symbol" not in symbol_data or "price" not in symbol_data or "volume" not in symbol_data or \
                    (symbol_data["price"] is not None and symbol_data["price"] <= 0):
                raise ValueError("Something is wrong about this {}".format(symbol_data))

            if symbol_data["symbol"] in symbol_list:
                raise ValueError("Duplicate symbol found for {}!".format(symbol_data["symbol"]))
            symbol_list.append(symbol_data["symbol"])


if __name__ == '__main__':
    unittest.main()
