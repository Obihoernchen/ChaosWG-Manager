from datetime import datetime, timezone

from flask_babel import format_datetime, format_timedelta


def utcnow():
    """
    Current UTC time as an aware datetime.

    Replacement for datetime.utcnow(), deprecated since Python 3.12.
    """
    return datetime.now(timezone.utc)


def make_aware(dt):
    """
    Attach UTC to naive datetimes, e.g. values read from SQLite.

    App-written values come back from peewee 4.x already aware; legacy
    rows and rows written through forms are naive. Both are stored as
    UTC, so treating naive as UTC keeps aware/naive arithmetic valid.
    """
    if dt is not None and dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def format_datetime_custom(value):
    if value is None:
        return 'Not yet'
    return format_datetime(value, 'dd.MM.yy HH:mm')


def format_timedelta_custom(value):
    if value is None:
        return 'Not yet'
    now = utcnow()
    return format_timedelta(make_aware(value) - now, granularity='day', add_direction=True)
