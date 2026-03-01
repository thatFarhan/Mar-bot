from config import ACTUAL_TIMEZONE, SYSTEM_TIMEZONE, NAMA_HARI
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler

class GlobalVars:
    def __init__(self):
        self.system_day = None
        self.system_date = None
        self.system_day_name = None

global_vars = GlobalVars()

global_vars.system_day = datetime.now(SYSTEM_TIMEZONE).date().day-1

global_vars.system_date = str(datetime.now(SYSTEM_TIMEZONE).date())

global_vars.system_day_name = NAMA_HARI[datetime.now(SYSTEM_TIMEZONE).date().weekday()]

scheduler = AsyncIOScheduler(timezone=ACTUAL_TIMEZONE)