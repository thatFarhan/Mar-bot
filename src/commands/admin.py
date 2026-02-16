from discord.ext import commands
from discord import app_commands
from config import *
from events.daily_schedule import *
from global_vars import scheduler
from events.reminder import send_reminder
import discord

@bot.tree.command(name="resend", description="[ADMIN] Mengirim ulang jadwal harian", guild=GUILD_ID)
@app_commands.checks.has_role("Marbot Mar-bot")
async def resend(interaction: discord.Interaction):
    await interaction.response.defer()
    await send_daily_schedule(interaction.followup)

@bot.tree.command(name="rewrite", description="[ADMIN] Menulis ulang file json jadwal hari ini", guild=GUILD_ID)
@app_commands.checks.has_role("Marbot Mar-bot")
async def rewrite(interaction: discord.Interaction):
    write_todays_pic()
    await interaction.response.send_message("jadwal_hariini.json telah ditulis ulang", ephemeral=True)

@bot.tree.command(name="testscheduled", description="[ADMIN] Tes scheduled message",guild=GUILD_ID)
@app_commands.checks.has_role("Marbot Mar-bot")
async def testschedule(interaction: discord.Interaction):
    await interaction.response.send_message(content="test", ephemeral=True)
    await send_reminder('maghrib')
    for schedule in scheduler.get_jobs():
        print(schedule)