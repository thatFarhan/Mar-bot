from discord import app_commands
from config import bot, SholatEnum
from server_config import GUILD_ID
from events.daily_schedule import send_daily_schedule
from events.reminder import send_reminder
from views.edit_schedule_view import EditScheduleView
from views.botconfig_modal import BotConfigModal
from builders.edit_schedule_builder import build_schedule
from repository.loader import jadwal
from repository.export import export_to_excel, export_json
from database.discord_server import ChannelTypeEnum, update_channel, get_channel, get_bot_config
import discord

@bot.tree.command(name="jadwalharian", description="[ADMIN] Mengirim ulang jadwal harian", guild=GUILD_ID)
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
async def jadwalharian(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    daily_schedule_channel = await get_channel("daily_schedule_channel", interaction.guild_id)
    await send_daily_schedule(interaction.guild_id, daily_schedule_channel)
    await interaction.followup.send(content="Daily schedule sent", ephemeral=True)

@bot.tree.command(name="kirimreminder", description="[ADMIN] Mengirim reminder untuk jadwal sholat yang ditentukan",guild=GUILD_ID)
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
async def testreminder(interaction: discord.Interaction, sholat: SholatEnum):
    await interaction.response.send_message(content=f"Test reminder sholat {sholat.value}", ephemeral=True)
    await send_reminder(sholat.value, interaction.guild_id)

@bot.tree.command(name="editjadwal", description="[ADMIN] Menampilkan interface untuk mengedit jadwal rawatib", guild=GUILD_ID)
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
async def editschedule(interaction: discord.Interaction):
    embeds=[]
    for tempat in jadwal.jadwal_rawatib["Senin"]:
        embeds.append(build_schedule(tempat, "Senin", "subuh", "msu"))

    await interaction.response.send_message(content="# `📝 Edit jadwal hari Senin`", embeds=embeds, view=EditScheduleView(day_name="Senin", sholat_chosen="subuh", tempat_chosen="msu"))

@bot.tree.command(name="export", description="[ADMIN] Mengekspor data presensi dari seminggu terakhir", guild=GUILD_ID)
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(export_range="Berapa hari ke belakang yang di export")
async def export(interaction: discord.Interaction, export_range: int = 7):
    await interaction.response.defer()
    await export_to_excel(interaction.followup, export_range + 1)

@bot.tree.command(name="exportjson", description="[ADMIN] Mengekspor data presensi keseluruhan dalam bentuk json", guild=GUILD_ID)
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
async def exportjson(interaction: discord.Interaction):
    await interaction.response.defer()
    await export_json(interaction.followup)

@bot.tree.command(name="botconfig", description="[ADMIN] Mengatur konfigurasi bot", guild=GUILD_ID)
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
async def botconfig(interaction: discord.Interaction):
    bot_config = await get_bot_config(interaction.guild_id)
    await interaction.response.send_modal(BotConfigModal(bot_config))

@bot.tree.command(name="setchannel", description="[ADMIN] Mengatur channel ini menjadi channel yang dipilih", guild=GUILD_ID)
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
async def setchannel(interaction: discord.Interaction, channel_type: ChannelTypeEnum):
    await update_channel(channel_type.value, interaction.guild_id, interaction.channel_id)
    await interaction.response.send_message(content=f"Berhasil mengatur channel ini menjadi channel {channel_type.name}", ephemeral=True)