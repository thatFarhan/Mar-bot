from config import bot, GUILD_ID
from discord import app_commands
from data.loader import jadwal
from views.edit_schedule_view import EditScheduleView
from builders.edit_schedule_builder import build_schedule
import discord

@bot.tree.command(name="editschedule", description="[ADMIN] Menampilkan interface untuk mengedit jadwal rawatib", guild=GUILD_ID)
@app_commands.checks.has_role("Marbot Mar-bot")
async def editschedule(interaction: discord.Interaction):
    embeds=[]
    for tempat in jadwal.jadwal_rawatib["Senin"]:
        embeds.append(build_schedule(tempat, "Senin", "subuh", "msu"))

    await interaction.response.send_message(content="# `📝 Edit jadwal hari Senin`", embeds=embeds, view=EditScheduleView(day_name="Senin", sholat_chosen="subuh", tempat_chosen="msu"))