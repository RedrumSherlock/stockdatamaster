import logging
import time
from collections import defaultdict, OrderedDict
import sdm.constants as c


def is_float(obj):
    if obj is None or str(obj).upper() == 'NAN' or str(obj).upper() == 'INF':
        return False
    try:
        float(obj)
        return True
    except ValueError:
        return False


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def timer(func):
    def timing(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        logging.info("{} ran for {:.3f} seconds".format(func.__name__, end - start))
        return result

    return timing


def transpose_dict(data):
    """
    Switch the first and second layer of keys in a nested dict, similar to matrix transposing.
    :param data: A nested dict like
    {"MSFT": {"2020-01-01": 103, "2020-01-02": 100},
     "AAPL": {"2020-01-01": 400, "2020-01-02": 432}}
    :return: Another nested dict with the same value of input but flipped set of keys, like
    {"2020-01-01": {"MSFT": 103, "AAPL": 400},
    ""2020-01-02": {"MSFT": 100, "AAPL": 432}}
    """
    transposed_dict = defaultdict(dict)
    for key, val in data.items():
        for sub_key, sub_val in val.items():
            transposed_dict[sub_key][key] = sub_val
    return OrderedDict(sorted(transposed_dict.items()))


def enforce_precision(obj):
    if isinstance(obj, float):
        return round(obj, c.FLOAT_PRECISION)
    elif isinstance(obj, dict):
        return dict((k, enforce_precision(v)) for k, v in obj.items())
    elif isinstance(obj, (list, tuple)):
        return list(map(enforce_precision, obj))
    return obj
