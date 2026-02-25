from discord.ext import tasks
from datetime import time, datetime
from config import ACTUAL_TIMEZONE, SYSTEM_TIMEZONE
from events.daily_schedule import send_daily_schedule, write_todays_pic
from events.reminder import set_reminders, reset_reminder_sent
from global_vars import global_vars
from data.loader import jadwal
from data.persistent_loader import persistent_vars, save_persistent

@tasks.loop(time=time(hour=20, tzinfo=ACTUAL_TIMEZONE))
async def new_system_day():
    # update system date
    global_vars.system_date=datetime.now(SYSTEM_TIMEZONE).date().day-1
    global_vars.system_day_name=jadwal.jadwal_sholat_bulanini[global_vars.system_date]['hari']
    persistent_vars["notification_ids"].clear()
    save_persistent()

    write_todays_pic()

    await send_daily_schedule()

    set_reminders()

    reset_reminder_sent