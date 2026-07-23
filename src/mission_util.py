from datetime import timedelta, datetime
from config import NAMA_BULAN

def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += 7
    return d + timedelta(days=days_ahead)

def to_datetime(str_date: str) -> datetime:
    return datetime.strptime(str_date, "%Y-%m-%d")

def to_indo_date_format(str_date: str) -> str:
    date = to_datetime(str_date)
    tanggal_day = date.day
    tanggal_month = NAMA_BULAN[date.month]
    tanggal_year = date.year
    return f"{tanggal_day} {tanggal_month} {tanggal_year}"