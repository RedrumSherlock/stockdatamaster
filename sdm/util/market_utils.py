import datetime as dt

from dateutil.relativedelta import MO
from pandas import DateOffset
from pandas.tseries.holiday import AbstractHolidayCalendar, Holiday, nearest_workday, USMartinLutherKingJr, \
    USPresidentsDay, GoodFriday, USMemorialDay, USLaborDay, USThanksgivingDay, next_monday

import sdm.constants as c
from sdm.util.date_utils import trunc_date


class USTradingCalendar(AbstractHolidayCalendar):
    rules = [
        Holiday('NewYearsDay', month=1, day=1, observance=nearest_workday),
        USMartinLutherKingJr,
        USPresidentsDay,
        GoodFriday,
        USMemorialDay,
        Holiday('USIndependenceDay', month=7, day=4, observance=nearest_workday),
        USLaborDay,
        USThanksgivingDay,
        Holiday('Christmas', month=12, day=25, observance=nearest_workday)
    ]


class CATradingCalendar(AbstractHolidayCalendar):
    rules = [
        Holiday('NewYearsDay', month=1, day=1, observance=next_monday),
        Holiday('FamilyDay', start_date=dt.datetime(2008, 1, 1), month=2, day=1, offset=DateOffset(weekday=MO(3))),
        GoodFriday,
        Holiday('VictoriaDay', month=5, day=24, offset=DateOffset(weekday=MO(-1))),
        Holiday('CanadaDay', month=7, day=1, observance=next_monday),
        Holiday('CivicHoliday', month=8, day=1, offset=DateOffset(weekday=MO(1))),
        USLaborDay,
        Holiday('CAThanksgiving', month=10, day=1, offset=DateOffset(weekday=MO(2))),
        Holiday('Christmas', month=12, day=25, observance=
        lambda d: d + dt.timedelta(2) if d.weekday() == 5 or d.weekday() == 6 else d),
        Holiday('BoxingDay', month=12, day=26, observance=
        lambda d: d + dt.timedelta(2) if d.weekday() == 5 or d.weekday() == 6 else d)
    ]


inst = USTradingCalendar()
DEFAULT_CALENDAR = inst.holidays(c.EARLIEST_DATE - dt.timedelta(days=1), c.LATEST_DATE + dt.timedelta(days=1))
inst_ca = CATradingCalendar()
CA_CALENDAR = inst_ca.holidays(c.EARLIEST_DATE - dt.timedelta(days=1), c.LATEST_DATE + dt.timedelta(days=1))


def is_open_day(date, market, holidays=DEFAULT_CALENDAR):
    if date.weekday() >= 5:
        return False

    if market != 'tsx':
        if trunc_date(date) in c.US_SPECIAL_CLOSED_DAYS:
            return False
        if trunc_date(date) in holidays and not (date.weekday() == 4 and date.month == 12 and date.day == 31):
            # If a new year is on Saturday and new years eve falls on Friday, then Friday is partially open even it is
            # the nearest observed new years day. Only applicable to US though.
            return False
    else:
        holidays = CA_CALENDAR
        if trunc_date(date) in c.CA_SPECIAL_OPEN_DAYS:
            return True
        if trunc_date(date) in c.CA_SPECIAL_CLOSED_DAYS:
            return False
        if trunc_date(date) in holidays:
            return False

    return True


def shift_open_days(date, days_to_shift, market, holidays=DEFAULT_CALENDAR):
    if days_to_shift == 0:
        raise ValueError("Need to shift for at least one day!")
    delta = 1 if days_to_shift > 0 else -1
    days_shifted = 0
    while abs(days_shifted) < abs(days_to_shift):
        date = date + dt.timedelta(days=delta)
        if is_open_day(date, market, holidays):
            days_shifted += delta
    return date


def is_open_time(current_time, market):
    start_time = dt.datetime.combine(current_time.date(), dt.time(9, 30, 00))
    end_time = dt.datetime.combine(current_time.date(), dt.time(16, 00, 00))
    return start_time <= current_time <= end_time
