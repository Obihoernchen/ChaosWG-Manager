from datetime import datetime

from flask_babel import format_datetime, format_timedelta


def format_datetime_custom(value):
    if value is None:
        return 'Not yet'
    return format_datetime(value, 'dd.MM.yy HH:mm')


def format_timedelta_custom(value):
    if value is None:
        return 'Not yet'
    now = datetime.utcnow()
    return format_timedelta(value - now, granularity='day', add_direction=True)
