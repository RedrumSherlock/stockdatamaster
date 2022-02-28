from sdm.candlestick.pattern.trend import *

import unittest


class TestTrends(unittest.TestCase):

    def test_down_trend(self):
        curr= {"close": 192}
        prev_5 = {"close": 193.2}
        prev_10 = {"close": 195.2}
        prev_20 = {"close": 230.2}

        self.assertTrue(is_down_trend(curr, prev_5, prev_10, prev_20))

    def test_rsi_calculation(self):
        curr = {"close": 18.5}
        prev_n_list = [{"close": 17.52}, {"close": 17.8}, {"close": 17.92}, {"close": 17.21}, {"close": 17.65},
                       {"close": 17.2}, {"close": 18}, {"close": 18.2}, {"close": 19}, {"close": 18.5},
                       {"close": 18.4}, {"close": 17.1}]
        self.assertEqual(rsi(curr, prev_n_list, n=12, method=RSI_METHODS.simple), 56.9)
        self.assertEqual(rsi(curr, prev_n_list, n=12, method=RSI_METHODS.exponential), 56.46)
        self.assertEqual(rsi(curr, prev_n_list, n=12, method=RSI_METHODS.wilder), 56.62)

        curr = {"close": 17.52}
        prev_zero_list = [{"close": 17.52}, {"close": 17.52}, {"close": 17.52}, {"close": 17.52}, {"close": 17.52},
                       {"close": 17.52}, {"close": 17.52}, {"close": 17.52}, {"close": 17.52}, {"close": 17.52},
                       {"close": 17.52}, {"close": 17.52}]
        self.assertEqual(rsi(curr, prev_zero_list, n=12, method=RSI_METHODS.simple), 50)

if __name__ == '__main__':
    unittest.main()
