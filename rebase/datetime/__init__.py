from calendar import timegm
from datetime import datetime, timedelta, tzinfo


ZERO = timedelta(0)

DAY_SECONDS = timedelta(days=1).total_seconds()


class UTC(tzinfo):
    def utcoffset(self, dt):
        return ZERO

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return ZERO


utc = UTC()


def utcnow():
    return datetime.now(utc)


def time_to_epoch(datetime_):
    ''' returns a UNIX timestamp for datetime_ '''
    return timegm(datetime_.utctimetuple())


def utcnow_timestamp():
    return time_to_epoch(utcnow())


