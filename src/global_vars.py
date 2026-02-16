from config import ACTUAL_TIMEZONE, SYSTEM_TIMEZONE
from datetime import datetime
from data.loader import jadwal
from apscheduler.schedulers.asyncio import AsyncIOScheduler

class GlobalVars:
    def __init__(self):
        self.system_date = None
        self.actual_date = None
        self.system_day_name = None

global_vars = GlobalVars()

global_vars.actual_date=datetime.now(ACTUAL_TIMEZONE).date().day-1
global_vars.system_date=datetime.now(SYSTEM_TIMEZONE).date().day-1

global_vars.system_day_name=jadwal.jadwal_sholat_bulanini[global_vars.system_date]['hari']

scheduler = AsyncIOScheduler(timezone=ACTUAL_TIMEZONE)