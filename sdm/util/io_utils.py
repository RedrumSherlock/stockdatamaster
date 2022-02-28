import csv
import os

import sdm.constants as c


def load_symbol_list():
    symbol_list = []
    with open(os.path.join(c.ROOT_DIR, c.SYMBOL_LIST_FILE), 'rt') as file:
        companies = csv.DictReader(file)
        for company in companies:
            symbol_list.append(company['Symbol'])
    return symbol_list


def get_token(api_name, file_path, file_name=None):
    if file_name is not None:
        file_path = os.path.join(file_path, file_name)
    with open(file_path, 'rt') as file:
        api_list = csv.DictReader(file)
        for api in api_list:
            if api["name"].upper() == api_name.upper():
                return api["token"]
        raise ValueError("API {} not found in the token file {}".format(api_name, file_path))


def is_non_empty_file(file_path, file_name=None):
    if file_name is not None:
        file_path = os.path.join(file_path, file_name)
    return os.path.isfile(file_path) and os.path.getsize(file_path) > 0
