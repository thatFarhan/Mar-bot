from discord.ext import tasks
from datetime import time, datetime
from config import bot, ACTUAL_TIMEZONE, SYSTEM_TIMEZONE, DAILY_SCHEDULE_CHANNEL
from events.daily_schedule import send_daily_schedule, write_todays_pic
from events.reminder import set_reminders, reset_reminder_sent
from global_vars import global_vars

@tasks.loop(time=time(hour=20, tzinfo=ACTUAL_TIMEZONE))
async def new_system_day():
    # update system date
    global_vars.system_date=datetime.now(SYSTEM_TIMEZONE).date().day-1

    # send daily
    channel=bot.get_channel(DAILY_SCHEDULE_CHANNEL)
    await send_daily_schedule(channel)

    write_todays_pic()
    set_reminders()

@tasks.loop(time=time(hour=0, tzinfo=ACTUAL_TIMEZONE))
async def new_actual_day():
    # update actual date
    global_vars.actual_date=datetime.now(ACTUAL_TIMEZONE).date().day-1
    reset_reminder_sent