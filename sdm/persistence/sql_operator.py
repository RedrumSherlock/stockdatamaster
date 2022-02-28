import logging
import os
import sqlite3
import json
from collections import OrderedDict

from sdm.persistence.file_operator import FileOperator
import sdm.constants as c
from sdm.util.date_utils import get_current_datetime, datetime_to_timestamp, timestamp_to_datetime
from sdm.util.misc_utils import enforce_precision


class SQLOperator(FileOperator):

    def __init__(self, directory, db_file_name=None):
        super().__init__(directory)
        self._db_file_name = db_file_name
        if db_file_name is not None:
            self._init_db()

    def save_to_file(self, data, file_name, data_type="historical", append="True"):
        if data_type not in c.DATA_TYPES:
            raise ValueError("Incorrect data type! Must be one of these: {}".format(c.DATA_TYPES))
        if data_type == "historical":
            sql_data = self._historical_data_to_sql_format(data)
        elif data_type == "realtime":
            sql_data = self._realtime_data_to_sql_format(data)

        self.switch_db_file(file_name)

        if not append:
            self._truncate_table()

        conn = self._get_connection()
        cur = conn.cursor()
        cur.executemany('INSERT INTO {} VALUES (?,?,?)'.format(c.TABLE_NAME), sql_data)
        conn.commit()
        logging.info("{} of records have been written to file {}".format(len(sql_data), file_name))
        conn.close()

    def load_from_file(self, file_name, data_type, symbol=None, start_date=c.EARLIEST_DATE, end_date=c.LATEST_DATE,
                       datetime_format=None):
        if data_type not in c.DATA_TYPES:
            raise ValueError("Incorrect data type! Must be one of these: {}".format(c.DATA_TYPES))

        self.switch_db_file(file_name)
        conn = self._get_connection()
        cur = conn.cursor()
        select_stmt = "SELECT {}, {}, {} FROM {} WHERE {} between ? and ?".format(
            c.SYMBOL_COLUMN, c.TIMESTAMP_COLUMN, c.DATA_COLUMN, c.TABLE_NAME, c.TIMESTAMP_COLUMN)
        if symbol is None:
            cur.execute(select_stmt, (datetime_to_timestamp(start_date), datetime_to_timestamp(end_date)))
        else:
            select_stmt = select_stmt + " AND {} = ?".format(c.SYMBOL_COLUMN)
            cur.execute(select_stmt,
                        (datetime_to_timestamp(start_date), datetime_to_timestamp(end_date), symbol.upper()))
        sql_data = cur.fetchall()
        conn.close()
        logging.info("Total of {} records have been loaded from file {}.".format(len(sql_data), file_name))

        if data_type == "historical":
            return self._sql_data_to_historical(sql_data)
        elif data_type == "realtime":
            return self._sql_data_to_realtime(sql_data)

    def load_symbol_list(self, file_name):
        self.switch_db_file(file_name)
        conn = self._get_connection()
        cur = conn.cursor()
        conn.row_factory = lambda cursor, row: row[0]
        sql_select_symbols = "SELECT distinct {} FROM {}".format(c.SYMBOL_COLUMN, c.TABLE_NAME)
        cur.execute(sql_select_symbols)
        symbol_list = cur.fetchall()
        logging.info("There are {} symbols found in the daily table".format(len(symbol_list)))
        conn.close()
        return [symbol[0] for symbol in symbol_list]

    def switch_db_file(self, file_name):
        if self._db_file_name != file_name:
            self._db_file_name = file_name
            if self._db_file_name is not None:
                self._init_db()

    def _get_connection(self):
        return sqlite3.connect(os.path.join(self._directory, self._db_file_name))

    def _init_db(self):
        conn = self._get_connection()
        # Check if tables exist. If not create the base table.
        self._create_db_table(conn)
        logging.info("Database successfully initialized in file: " + self._db_file_name)
        conn.close()

    @staticmethod
    def _table_existing(conn):
        cur = conn.cursor()
        cur.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name=?", (c.TABLE_NAME,))
        return cur.fetchone()[0] > 0

    def _create_db_table(self, conn):
        if not self._table_existing(conn):
            cur = conn.cursor()
            sql_create_daily_table = """ CREATE TABLE IF NOT EXISTS {} (
                                                    {} text NOT NULL,
                                                    {} integer NOT NULL,
                                                    {} text,
                                                    PRIMARY KEY ({}, {}));"""\
                .format(c.TABLE_NAME, c.SYMBOL_COLUMN, c.TIMESTAMP_COLUMN, c.DATA_COLUMN,
                        c.SYMBOL_COLUMN, c.TIMESTAMP_COLUMN,)
            cur.execute(sql_create_daily_table)

    def _truncate_table(self):
        conn = self._get_connection()
        if self._table_existing(conn):
            cur = conn.cursor()
            cur.execute("DELETE FROM {};".format(c.TABLE_NAME))
            conn.commit()
        conn.close()

    @staticmethod
    def _historical_data_to_sql_format(raw_data):
        result = []
        for symbol in raw_data:
            for datetime in raw_data[symbol]:
                record = raw_data[symbol][datetime]
                if c.SYMBOL_KEY in record:
                    del record[c.SYMBOL_KEY]
                if c.DATETIME_KEY in record:
                    del record[c.DATETIME_KEY]
                result.append((symbol, datetime_to_timestamp(datetime), json.dumps(enforce_precision(record))))
        return result

    @staticmethod
    def _realtime_data_to_sql_format(raw_data):
        result = []
        for symbol in raw_data:
            record = raw_data[symbol]
            if c.DATETIME_KEY not in record:
                timestamp = datetime_to_timestamp(get_current_datetime())
            else:
                timestamp = datetime_to_timestamp(record[c.DATETIME_KEY])
                del record[c.DATETIME_KEY]
            result.append((symbol, timestamp, json.dumps(enforce_precision(record))))
        return result

    @staticmethod
    def _sql_data_to_historical(sql_data):
        if len(sql_data) == 0:
            return sql_data

        result = {}
        for record in sql_data:
            symbol = record[0]
            datetime = timestamp_to_datetime(record[1])
            if symbol not in result:
                result[symbol] = {}
            result[symbol][datetime] = json.loads(record[2])

        for symbol in result:
            result[symbol] = OrderedDict(sorted(result[symbol].items()))
        return result

    @staticmethod
    def _sql_data_to_realtime(sql_data):
        if len(sql_data) == 0:
            return sql_data

        result = {}
        for record in sql_data:
            symbol = record[0]
            result[symbol] = json.loads(record[2])
            result[symbol][c.DATETIME_KEY] = timestamp_to_datetime(record[1])
        return result
