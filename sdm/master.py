import sdm.constants as c
from sdm.operation.validation import validate_historical_data, validate_realtime_data
from sdm.persistence.csv_operator import CSVOperator
from sdm.persistence.sql_operator import SQLOperator


class StockDataMaster:

    def __init__(self, file_path, file_type="sql", data_type="historical", response_format="json"):
        self.file_path = file_path
        self.data_type = data_type
        self.file_type = file_type
        self._symbol_list = None
        self._response_format = response_format

    def save_data(self, data, file_name, data_type=None, append=True):
        if data_type is None:
            data_type = self.data_type
        self._file_operator.save_to_file(data, file_name, data_type, append)

    def load_data(self, file_name, data_type=None, symbol=None, start_date=c.EARLIEST_DATE, end_date=c.LATEST_DATE,
                  datetime_format=c.DATETIME_FORMAT):
        if data_type is None:
            data_type = self.data_type
        return self._file_operator.load_from_file(file_name, data_type, symbol, start_date, end_date, datetime_format)

    def validate_data(self, data, market, data_type=None, validation_level=2):
        if data_type is None:
            data_type = self.data_type

        if data_type not in c.DATA_TYPES:
            raise ValueError("Incorrect data type! Must be one of these: {}".format(c.DATA_TYPES))

        if data_type == "historical":
            return validate_historical_data(data, market, validation_level)
        elif data_type == "realtime":
            return validate_realtime_data(data, validation_level)

    def get_symbol_list(self, file_name=None):
        if self._symbol_list is None and file_name is None:
            raise ValueError("Symbol list is empty. Must load it from a file first! Please specify the file name.")
        if file_name is not None:
            self._symbol_list = self._file_operator.load_symbol_list(file_name)
        return self._symbol_list

    @property
    def file_path(self):
        return self._file_path

    @file_path.setter
    def file_path(self, file_path):
        self._file_path = file_path

    @property
    def data_type(self):
        return self._data_type

    @data_type.setter
    def data_type(self, data_type):
        if data_type.lower() not in c.DATA_TYPES:
            raise ValueError("Data type must be in one of these: {}".format(c.DATA_TYPES))
        self._data_type = data_type.lower()

    @property
    def file_type(self):
        return self._file_type

    @file_type.setter
    def file_type(self, file_type):
        if file_type.lower() not in c.FILE_TYPE:
            raise ValueError("File type must be in one of these: {}".format(c.FILE_TYPE))
        self._file_type = file_type.lower()
        if self._file_type == "csv":
            self._file_operator = CSVOperator(self.file_path)
        elif self._file_type == "sql":
            self._file_operator = SQLOperator(self.file_path)
