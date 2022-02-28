from abc import ABC, abstractmethod


class FileOperator(ABC):

    def __init__(self, directory):
        self._directory = directory

    @abstractmethod
    def save_to_file(self, data, file_name, data_type, append):
        raise NotImplementedError

    @abstractmethod
    def load_from_file(self, file_name, data_type, symbol, start_date, end_date, datetime_format):
        raise NotImplementedError

    @abstractmethod
    def load_symbol_list(self, file_name):
        raise NotImplementedError