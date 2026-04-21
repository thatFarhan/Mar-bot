from discord import app_commands
from config import bot, SholatEnum
from server_config import GUILD_ID
from events.daily_schedule import send_daily_schedule, write_todays_pic
from events.reminder import send_reminder, reset_reminder_sent, set_reminders
from views.edit_schedule_view import EditScheduleView
from builders.edit_schedule_builder import build_schedule
from repository.loader import jadwal
from repository.export import export_to_excel, export_json
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

@bot.tree.command(name="sendreminder", description="[ADMIN] Mengirim reminder untuk jadwal sholat yang ditentukan",guild=GUILD_ID)
@app_commands.checks.has_role("Marbot Mar-bot")
async def testreminder(interaction: discord.Interaction, sholat: SholatEnum):
    await interaction.response.send_message(content=f"Test reminder sholat {sholat}", ephemeral=True)
    await send_reminder(sholat)

@bot.tree.command(name="editjadwal", description="[ADMIN] Menampilkan interface untuk mengedit jadwal rawatib", guild=GUILD_ID)
@app_commands.checks.has_role("Marbot Mar-bot")
async def editschedule(interaction: discord.Interaction):
    embeds=[]
    for tempat in jadwal.jadwal_rawatib["Senin"]:
        embeds.append(build_schedule(tempat, "Senin", "subuh", "msu"))

    await interaction.response.send_message(content="# `📝 Edit jadwal hari Senin`", embeds=embeds, view=EditScheduleView(day_name="Senin", sholat_chosen="subuh", tempat_chosen="msu"))

@bot.tree.command(name="export", description="[ADMIN] Mengekspor data presensi dari seminggu terakhir", guild=GUILD_ID)
@app_commands.checks.has_role("Marbot Mar-bot")
@app_commands.describe(export_range="Berapa hari ke belakang yang di export")
async def export(interaction: discord.Interaction, export_range: int = 7):
    await interaction.response.defer()
    await export_to_excel(interaction.followup, export_range + 1)

@bot.tree.command(name="exportjson", description="[ADMIN] Mengekspor data presensi keseluruhan dalam bentuk json", guild=GUILD_ID)
@app_commands.checks.has_role("Marbot Mar-bot")
async def exportjson(interaction: discord.Interaction):
    await interaction.response.defer()
    await export_json(interaction.followup)