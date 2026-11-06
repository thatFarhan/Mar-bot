import discord

from database.presensi import get_all_my_schedule_thisweek
import global_vars
from models.Schedule import Schedule
from views.confirm_modal import TakeRespModal

async def offer_swap(interaction: discord.Interaction, requested_schedule: Schedule):
    if interaction.user.id == requested_schedule.uid_petugas:
        await interaction.response.send_message("Tidak bisa menawarkan penukaran ke jadwal sendiri.", ephemeral=True)
        return
    
    my_schedules = await get_all_my_schedule_thisweek(global_vars.system_date, interaction.guild_id, interaction.user.id)
    
    if requested_schedule:
        await interaction.response.send_modal(TakeRespModal(my_schedules, requested_schedule))
    else:
        await interaction.response.send_message(content="Tidak ada jadwal yang bisa ditawarkan", ephemeral=True)