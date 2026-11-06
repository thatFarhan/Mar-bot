import asyncio

import discord
import traceback
import logging
from datetime import datetime

# file imports
from config import bot, SYSTEM_TIMEZONE, ACTUAL_TIMEZONE, token
from database.connection import init_database, DatabaseError
from server_config import GUILD_ID
from repository.loader import jadwal
from events.daily_tasks import new_system_day
from events.daily_schedule import write_pics_weekahead
from events.reminder import set_reminders, scheduler
from views.confirmation_buttons import ConfirmationButtons
from events.new_prayer_schedule import get_new_schedule

from commands import admin, confirm, extras, sell, claim, member, jumat_schedule, swap
from database.discord_server import get_all_servers

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

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

    await write_pics_weekahead()

    if not new_system_day.is_running():
        new_system_day.start()

    if not scheduler.running:
        scheduler.start()

    # export_next_monday()
    servers = await get_all_servers()
    for server in servers:
        await set_reminders(server["id_server"])

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
    if isinstance(error, discord.app_commands.MissingPermissions):
        msg = "Kamu tidak punya izin untuk menggunakan command ini."
    else:
        # Unwrap so you see the real aiomysql error, not just "CommandInvokeError"
        original = getattr(error, "original", error)
        traceback.print_exception(type(original), original, original.__traceback__)
        msg = "Terjadi kesalahan saat memproses command."

    if interaction.response.is_done():
        await interaction.followup.send(msg, ephemeral=True)
    else:
        await interaction.response.send_message(msg, ephemeral=True)

async def main():
    try:
        bot.db = await init_database()
    except DatabaseError as e:
        print("Aborting startup: ", e)
        return  # never connects to Discord

    try:
        async with bot:
            await bot.start(token)
    finally:
        bot.db.close()
        await bot.db.wait_closed()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Shut down by user. Bye!")