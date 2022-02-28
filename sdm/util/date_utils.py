import sdm.constants as c
import datetime as dt
import pytz


def date_to_string(date, date_format=c.DATE_FORMAT):
    return dt.datetime.strftime(date, date_format)


def string_to_date(string, date_format=c.DATE_FORMAT):
    return dt.datetime.strptime(string, date_format)


def datetime_to_string(date, date_format=c.DATETIME_FORMAT):
    return dt.datetime.strftime(date, date_format)


def string_to_datetime(string, date_format=c.DATETIME_FORMAT):
    return dt.datetime.strptime(string, date_format)


def timestamp_to_datetime(timestamp):
    return dt.datetime.fromtimestamp(timestamp, tz=pytz.timezone('America/Toronto')).replace(tzinfo=None)


def datetime_to_timestamp(datetime):
    return int(datetime.timestamp())


def get_current_datetime():
    return dt.datetime.today()


def trunc_date(date):
    return dt.datetime(date.year, date.month, date.day)


def trunc_today():
    return trunc_date(dt.datetime.today())


def date_difference(date_1, date_2):
    delta = date_1 - date_2
    return abs(delta.days)