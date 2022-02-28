from sdm.util.io_utils import load_symbol_list
import unittest


class TestSymbol(unittest.TestCase):

    def test_symbol_list(self):
        symbol_list = load_symbol_list()
        self.assertTrue(len(symbol_list) > 0)
        # Check for duplicates
        dup = set([x for x in symbol_list if symbol_list.count(x) > 1])
        self.assertTrue(len(dup) == 0)


if __name__ == '__main__':
    unittest.main()
