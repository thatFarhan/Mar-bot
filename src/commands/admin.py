from discord import app_commands
from config import bot, GUILD_ID, SholatEnum
from events.daily_schedule import send_daily_schedule, write_todays_pic
from events.reminder import send_reminder, reset_reminder_sent, set_reminders
import discord

@bot.tree.command(name="dailyschedule", description="[ADMIN] Mengirim ulang jadwal harian", guild=GUILD_ID)
@app_commands.checks.has_role("Marbot Mar-bot")
async def dailyschedule(interaction: discord.Interaction):
    await send_daily_schedule()
    await interaction.response.send_message(content="Daily schedule sent", ephemeral=True)
    set_reminders()
    await reset_reminder_sent()

@bot.tree.command(name="rewritejson", description="[ADMIN] Menulis ulang file json jadwal hari ini", guild=GUILD_ID)
@app_commands.checks.has_role("Marbot Mar-bot")
async def rewritejson(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True);
    await write_todays_pic()
    await interaction.followup.send("presensi_rawatib.json telah ditulis ulang", ephemeral=True)

@bot.tree.command(name="testreminder", description="[ADMIN] Tes reminder",guild=GUILD_ID)
@app_commands.checks.has_role("Marbot Mar-bot")
async def testreminder(interaction: discord.Interaction, sholat: SholatEnum):
    await interaction.response.send_message(content="test", ephemeral=True)
    await send_reminder(sholat)