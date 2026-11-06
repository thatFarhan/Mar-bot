from datetime import timedelta, datetime, date
from config import NAMA_BULAN

def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += 7
    return d + timedelta(days=days_ahead)

def to_datetime(str_date: str) -> datetime:
    return datetime.strptime(str_date, "%Y-%m-%d")

def to_indo_date_format(tanggal: date) -> str:
    tanggal_day = tanggal.day
    tanggal_month = NAMA_BULAN[tanggal.month]
    tanggal_year = tanggal.year
    return f"{tanggal_day} {tanggal_month} {tanggal_year}"