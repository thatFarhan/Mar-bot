from discord import app_commands
from config import bot, GUILD_ID
from events.daily_schedule import send_daily_schedule, write_todays_pic
from global_vars import scheduler
from events.reminder import send_reminder, reset_reminder_sent
import discord

@bot.tree.command(name="dailyschedule", description="[ADMIN] Mengirim ulang jadwal harian", guild=GUILD_ID)
@app_commands.checks.has_role("Marbot Mar-bot")
async def dailyschedule(interaction: discord.Interaction):
    await interaction.response.defer()
    await send_daily_schedule(interaction.followup)

@bot.tree.command(name="rewritejson", description="[ADMIN] Menulis ulang file json jadwal hari ini", guild=GUILD_ID)
@app_commands.checks.has_role("Marbot Mar-bot")
async def rewritejson(interaction: discord.Interaction):
    write_todays_pic()
    await interaction.response.send_message("presensi_rawatib.json telah ditulis ulang", ephemeral=True)

@bot.tree.command(name="testreminder", description="[ADMIN] Tes reminder",guild=GUILD_ID)
@app_commands.checks.has_role("Marbot Mar-bot")
async def testreminder(interaction: discord.Interaction):
    await interaction.response.send_message(content="test", ephemeral=True)
    await send_reminder('maghrib')
    for schedule in scheduler.get_jobs():
        print(schedule)

@bot.tree.command(name="resetremindersent", description="[ADMIN] Reset tracker reminder yang telah dikirim", guild=GUILD_ID)
@app_commands.checks.has_role("Marbot Mar-bot")
async def resetremindersent(interaction: discord.Interaction):
    reset_reminder_sent()
    await interaction.response.send_message(content="Tracker reminder telah di reset", ephemeral=True)