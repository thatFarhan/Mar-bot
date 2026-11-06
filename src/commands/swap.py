import discord
from config import bot
from server_config import GUILD_ID
from views.sell_modal import RequestModal
from global_vars import global_vars

from database.presensi import get_all_my_unswapped_schedule_today, get_all_my_unswapped_schedule_thisweek

@bot.tree.command(name="tukar", description="Meminta penukaran jadwal yang Anda pilih di pekan ini", guild=GUILD_ID)
async def swap(interaction: discord.Interaction):
    await swaprequestweekmodal(interaction)

async def swaprequestmodal(interaction: discord.Interaction):
    schedules = await get_all_my_unswapped_schedule_today(global_vars.system_date, interaction.guild_id, interaction.user.id)
    if schedules:
        await interaction.response.send_modal(RequestModal(schedules, is_sub=False, is_week=False))
    else:
        await swaprequestweekmodal(interaction)

async def swaprequestweekmodal(interaction: discord.Interaction):
    schedules = await get_all_my_unswapped_schedule_thisweek(global_vars.system_date, interaction.guild_id, interaction.user.id)
    if schedules:
        await interaction.response.send_modal(RequestModal(schedules, is_sub=False, is_week=True))
    else:
        await interaction.response.send_message(content="Tidak ada jadwal yang bisa diminta penukaran pekan ini", ephemeral=True)