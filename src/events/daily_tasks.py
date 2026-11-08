from discord.ext import tasks
from datetime import time, datetime
from config import ACTUAL_TIMEZONE, SYSTEM_TIMEZONE, NAMA_HARI
from events.daily_schedule import send_daily_schedule, write_pics_weekahead
from events.reminder import set_reminders
from global_vars import global_vars
from repository.loader import jadwal
from repository.persistent_loader import save_persistent
from events.new_prayer_schedule import get_new_schedule
from events.purge_transaction import purge_expireds

from database.discord_server import get_channel_from_all_servers, update_reminders_sent

@tasks.loop(time=time(hour=20, tzinfo=ACTUAL_TIMEZONE))
async def new_system_day():
    # update system date
    global_vars.system_day = datetime.now(SYSTEM_TIMEZONE).date().day-1
    global_vars.system_date = datetime.now(SYSTEM_TIMEZONE).date()
    global_vars.system_day_name = NAMA_HARI[datetime.now(SYSTEM_TIMEZONE).date().weekday()]

    if jadwal.data_sholat["bulan"] != datetime.now(SYSTEM_TIMEZONE).month:
        await get_new_schedule()

    await save_persistent()

    # await write_todays_pic()
    await write_pics_weekahead()

    servers = await get_channel_from_all_servers("daily_schedule_channel")
    for server in servers:
        await set_reminders(server["id_server"])
        await send_daily_schedule(server["id_server"], server["daily_schedule_channel"])
        await update_reminders_sent(server["id_server"], 0)

    await purge_expireds()