import os
import csv
from collections import OrderedDict
import logging

from sdm.persistence.file_operator import FileOperator
import sdm.constants as c
from sdm.util.date_utils import get_current_datetime, datetime_to_string, string_to_datetime
from sdm.util.io_utils import is_non_empty_file
from sdm.util.misc_utils import enforce_precision


class CSVOperator(FileOperator):

    def __init__(self, directory):
        super().__init__(directory)

    def save_to_file(self, data, file_name, data_type="historical", append=True):
        file_mode = "a" if append else "w"
        if data_type not in c.DATA_TYPES:
            raise ValueError("Incorrect data type! Must be one of these: {}".format(c.DATA_TYPES))
        if data_type == "historical":
            csv_data = self.historical_data_to_csv_format(data)
        elif data_type == "realtime":
            csv_data = self.realtime_data_to_csv_format(data)

        if len(csv_data) > 0:
            keys = csv_data[0].keys()
            with open(os.path.join(self._directory, file_name), file_mode, newline='') as csv_file:
                dict_writer = csv.DictWriter(csv_file, keys)
                if not append or not is_non_empty_file(self._directory, file_name):
                    dict_writer.writeheader()
                dict_writer.writerows(csv_data)
            logging.info("Data has been written to file {}".format(file_name))
        else:
            logging.warning("Data is empty so not writing to the file specified.")

    def load_from_file(self, file_name, data_type="historical", symbol=None, start_date=c.EARLIEST_DATE,
                       end_date=c.LATEST_DATE, datetime_format=c.DATETIME_FORMAT):
        if data_type not in c.DATA_TYPES:
            raise ValueError("Incorrect data type! Must be one of these: {}".format(c.DATA_TYPES))

        with open(os.path.join(self._directory, file_name), "r") as f:
            reader = csv.DictReader(f)
            csv_data = list(reader)
        logging.info("Total of {} records have been loaded from file {}.".format(len(csv_data), file_name))
        if data_type == "historical":
            return self.csv_data_to_historical(csv_data, symbol, start_date, end_date, datetime_format)
        elif data_type == "realtime":
            return self.csv_data_to_realtime(csv_data, symbol, start_date, end_date, datetime_format)

    @staticmethod
    def historical_data_to_csv_format(raw_data):
        result = []
        for symbol in raw_data:
            for datetime in raw_data[symbol]:
                new_record= OrderedDict()
                new_record[c.SYMBOL_KEY] = symbol
                new_record[c.DATETIME_KEY] = datetime_to_string(datetime)
                record = raw_data[symbol][datetime]
                if c.SYMBOL_KEY in record:
                    del record[c.SYMBOL_KEY]
                if c.DATETIME_KEY in record:
                    del record[c.DATETIME_KEY]
                new_record.update(record)
                result.append(enforce_precision(new_record))
        return result

    def load_symbol_list(self, file_name):
        with open(os.path.join(self._directory, file_name), "r") as f:
            reader = csv.DictReader(f)
            csv_data = list(reader)
        return [csv_record[c.SYMBOL_KEY] for csv_record in csv_data]

    @staticmethod
    def realtime_data_to_csv_format(raw_data):
        result = []
        for symbol in raw_data:
            new_record = OrderedDict()
            record = raw_data[symbol]
            new_record[c.SYMBOL_KEY] = symbol
            if c.SYMBOL_KEY in record:
                del record[c.SYMBOL_KEY]
            if c.DATETIME_KEY not in record:
                new_record[c.DATETIME_KEY] = datetime_to_string(get_current_datetime())
            else:
                new_record[c.DATETIME_KEY] = datetime_to_string(record[c.DATETIME_KEY])
                del record[c.DATETIME_KEY]
            new_record.update(record)
            result.append(enforce_precision(new_record))
        return result

    @staticmethod
    def csv_data_to_historical(csv_data, target_symbol, start_date, end_date, csv_datetime_format=c.DATETIME_FORMAT):
        if len(csv_data) == 0:
            return csv_data

        result = {}
        for record in csv_data:
            if c.SYMBOL_KEY not in record or c.DATETIME_KEY not in record:
                continue
            if target_symbol is not None and target_symbol != record[c.SYMBOL_KEY]:
                continue
            datetime = string_to_datetime(record[c.DATETIME_KEY], csv_datetime_format)
            if datetime > end_date or datetime < start_date:
                continue
            symbol = record[c.SYMBOL_KEY]
            del record[c.SYMBOL_KEY]
            del record[c.DATETIME_KEY]

            if symbol not in result:
                result[symbol] = {}
            result[symbol][datetime] = record

        for symbol in result:
            result[symbol] = OrderedDict(sorted(result[symbol].items()))

        return result

    @staticmethod
    def csv_data_to_realtime(csv_data, target_symbol, start_date, end_date, csv_datetime_format=c.DATETIME_FORMAT):
        if len(csv_data) == 0:
            return csv_data

        result = {}
        for record in csv_data:
            if c.SYMBOL_KEY not in record or c.DATETIME_KEY not in record:
                continue
            if target_symbol is not None and target_symbol != record[c.SYMBOL_KEY]:
                continue
            datetime = string_to_datetime(record[c.DATETIME_KEY], csv_datetime_format)
            if datetime > end_date or datetime < start_date:
                continue
            record[c.DATETIME_KEY] = datetime
            symbol = record[c.SYMBOL_KEY]
            del record[c.SYMBOL_KEY]
            result[symbol] = record
        return result
