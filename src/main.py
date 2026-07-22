import discord
from datetime import datetime, timedelta

# file imports
from config import bot, SYSTEM_TIMEZONE, ACTUAL_TIMEZONE, token
from server_config import GUILD_ID
from global_vars import global_vars
from repository.loader import jadwal
from repository.export import export_next_monday
from events.daily_tasks import new_system_day
from events.daily_schedule import write_pics_weekahead
from events.reminder import set_reminders, scheduler
from views.confirmation_buttons import ConfirmationButtons
from events.new_prayer_schedule import get_new_schedule
from mission_util import to_datetime

from commands import admin, confirm, extras, sell, register, claim, member, jumat_schedule, swap

@bot.event
async def on_ready():
    print("Mar-bot siap bertugas pada", datetime.now(ACTUAL_TIMEZONE))

    activity = discord.Game(name="InsyaAllah Hadir")
    await bot.change_presence(
        status=discord.Status.online,
        activity=activity
    )

    bot.add_view(ConfirmationButtons())

    try:
        guild=GUILD_ID
        synced=await bot.tree.sync(guild=guild)
        print(f"Synced {len(synced)} commands to guild {guild.id}")
    except Exception as e:
        print(f"Error syncing commands: {e}")

    if jadwal.data_sholat["bulan"] != datetime.now(SYSTEM_TIMEZONE).month:
        await get_new_schedule()

    date_next_week = str(to_datetime(global_vars.system_date) + timedelta(6))
    if date_next_week not in jadwal.presensi_rawatib:
        await write_pics_weekahead()

    if not new_system_day.is_running():
        new_system_day.start()

    if not scheduler.running:
        scheduler.start()

    export_next_monday()
    set_reminders()

bot.run(token)