from discord.ext import tasks
from datetime import time, datetime
from config import ACTUAL_TIMEZONE, SYSTEM_TIMEZONE, NAMA_HARI
from events.daily_schedule import send_daily_schedule, write_todays_pic
from events.reminder import set_reminders, reset_reminder_sent
from global_vars import global_vars
from data.loader import jadwal
from data.persistent_loader import persistent_vars, save_persistent
from events.new_prayer_schedule import get_new_schedule

@tasks.loop(time=time(hour=20, tzinfo=ACTUAL_TIMEZONE))
async def new_system_day():
    # update system date
    global_vars.system_day = datetime.now(SYSTEM_TIMEZONE).date().day-1
    global_vars.system_date = str(datetime.now(SYSTEM_TIMEZONE).date())
    global_vars.system_day_name = NAMA_HARI[datetime.now(SYSTEM_TIMEZONE).date().weekday()]
    persistent_vars["notification_ids"].clear()

    if jadwal.data_sholat["bulan"] != datetime.now(SYSTEM_TIMEZONE).month:
        await get_new_schedule()

    await save_persistent()

    await write_todays_pic()

    await send_daily_schedule()

    set_reminders()

    await reset_reminder_sent()