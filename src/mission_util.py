from datetime import timedelta, datetime

def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += 7
    return d + timedelta(days=days_ahead)

def to_datetime(str_date) -> datetime:
    return datetime.strptime(str_date, "%Y-%m-%d")