"""
This module has all the global setting/options parameters for this tool.
"""

import os
import datetime as dt

# ----------------------------------------------------------------------------------------------------------------
# The following section contains configurations that can be tuned for your own preference without any impact to the
# program itself.
# root directory for loading the symbol file.
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# symbol list saved on a file
SYMBOL_LIST_FILE = "symbol_list.csv"

# Earliest date allowed
EARLIEST_DATE = dt.datetime(1970, 1, 1)

# Latest date allowed
LATEST_DATE = dt.datetime.today()

# Validation level for data loaded from database file. Higher ones will always contain the checks from lower ones
# 0 - No validation, pass all the data
# 1 - Check for only the basics, e.g. min <= open&close, max >= open&close
# 2 - There can be gaps during the time range, but each entry should have all the columns filled with valid number
# 3 - Ensure all the work days between start_day and end_day for the selected stock have data, and each entry have all
#     the columns filled with valid number
DEFAULT_DATA_VALIDATION_LEVEL = 2

# Whether we go verbose in output
VERBOSE = False

# Float precision to be saved in files
FLOAT_PRECISION = 3

# ----------------------------------------------------------------------------------------------------------------
# The following section is for some global parameters used by the program, and are not advised to be modified. Any
# modification could cause the program to run in an unexpected behaviour
# Date format saved in database and used elsewhere in the program for historical data, e.g. 2019-01-20
DATE_FORMAT = "%Y-%m-%d"

# Date time format saved in db or csv for real time data, e.g. 2020-02-14 13:47:00
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

# Markets that are currently supported
MARKETS = ['nyse', 'nasdaq', 'tsx']

# Formats of the response that are supported
RESPONSE_FORMATS = ['json', 'csv']

# API supported so far: fmp, iex_cloud
API_NAME = ["fmp", "iex_cloud"]

# Key used to find the symbols
SYMBOL_KEY = "symbol"

# Key used to find date
DATE_KEY = "date"

# Key used to find datetime
DATETIME_KEY = "datetime"

# Table name used to save data in SQL
TABLE_NAME = "stock_data"

# Column name used to save symbol in SQL
SYMBOL_COLUMN = "symbol"

# Column name used to save timestamp in SQL
TIMESTAMP_COLUMN = "timestamp"

# Column name used to save stock data as json in SQL
DATA_COLUMN = "jsondata"

# File operator types supported
FILE_TYPE = ["csv", "sql"]

# Data types
DATA_TYPES = ["historical", "realtime"]

# Interval of data supported so far: daily
INTERVAL = ["daily"]

# essential columns provided from every API
BASE_COLUMNS = ["open", "high", "low", "close", "volume"]

# time gap in seconds between API calls to not exceed limit. 0 if no such limit
PAUSE_BETWEEN_API_CALLS = 0

# The special days that US market closed such as 9-1-1 attack, mourning for former presidents, hurricane, etc.
US_SPECIAL_CLOSED_DAYS = [dt.datetime(2001, 9, 11), dt.datetime(2001, 9, 12), dt.datetime(2001, 9, 13),
                            dt.datetime(2001, 9, 14), dt.datetime(2004, 6, 11), dt.datetime(2007, 1, 2),
                            dt.datetime(2012, 10, 29), dt.datetime(2012, 10, 30), dt.datetime(2018, 12, 5)]

# The special days that Canada market closed such as 9-1-1 attack, etc.
CA_SPECIAL_CLOSED_DAYS = [dt.datetime(2001, 9, 11), dt.datetime(2001, 9, 12)]

# The special days that Canada market opened even it is a holiday.
CA_SPECIAL_OPEN_DAYS = [dt.datetime(2003, 12, 26)]

# ----------------------------------------------------------------------------------------------------------------
# The following section is only for FMP (Financial Modeling Prep) API formats. Will need to revise when FMP changes
# their API.
# base URL for the API
FMP_BASE_URL = "https://financialmodelingprep.com/api/v3/"

# Date format in FMP API
FMP_DATE_FORMAT = '%Y-%m-%d'

# Datetime format in FMP API
FMP_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

# ----------------------------------------------------------------------------------------------------------------
# The following section is only for IEX Cloud API formats. Will need to revise when IEX Cloud changes
# their API.
# base URL for the API
IEX_CLOUD_BASE_URL = "https://cloud.iexapis.com/v1/"

# Date format in IEX Cloud API
IEX_CLOUD_DATE_FORMAT = '%Y-%m-%d'

# IEX Cloud batch limit
IEX_CLOUD_BATCH_LIMIT = 100
