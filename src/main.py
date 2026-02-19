import discord
from datetime import datetime, date
import logging

# file imports
from config import bot, ACTUAL_TIMEZONE, GUILD_ID, token
from data.loader import jadwal, load_json
from events.daily_tasks import new_actual_day, new_system_day, write_todays_pic
from events.reminder import set_reminders, scheduler

from commands import admin, confirm, extras, sell

handler=logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

@bot.event
async def on_ready():
    print("Mar-bot siap bertugas pada", datetime.now(ACTUAL_TIMEZONE))

    activity = discord.Game(name="Under development")
    await bot.change_presence(
        status=discord.Status.online,
        activity=activity
    )

    try:
        guild=GUILD_ID
        synced=await bot.tree.sync(guild=guild)
        print(f"Synced {len(synced)} commands to guild {guild.id}")
    except Exception as e:
        print(f"Error syncing commands: {e}")

    if str(date.today()) not in jadwal.presensi_rawatib:
        write_todays_pic()
        
    jadwal.jadwal_hariini = load_json("src/data/presensi_rawatib.json")[str(date.today())]

    if not new_system_day.is_running:
        new_system_day.start()

    if not new_actual_day.is_running:
        new_actual_day.start()

    if not scheduler.running:
        scheduler.start()

    set_reminders()

bot.run(token, log_handler=handler, log_level=logging.DEBUG)