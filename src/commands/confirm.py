import discord
from discord import app_commands
from config import bot
from server_config import GUILD_ID
from events.update_schedule_message import update_daily_schedule
from views.confirm_modal import TakeRespModal
from views.force_confirm_modal import ForceConfirmModal
from global_vars import global_vars

from database.presensi import update_to_confirm_all, get_all_my_unconfirmed_schedule_today, update_to_confirm_from_reminder, get_all_unconfirmed_schedule_today

@bot.tree.command(name="konfirmasi", description="Mengonfirmasi presensi untuk jadwal yang Anda pilih di hari ini", guild=GUILD_ID)
async def konfirmasi(interaction: discord.Interaction):
    await confirm(interaction)

async def confirm(interaction: discord.Interaction):
    schedules = await get_all_my_unconfirmed_schedule_today(global_vars.system_date, interaction.guild_id, interaction.user.id)

    if schedules:
        await interaction.response.send_modal(TakeRespModal(schedules))
    else:
        await interaction.response.send_message(content="Tidak ada jadwal yang bisa dikonfirmasi.", ephemeral=True)

async def confirm_all(interaction: discord.Interaction):
    jadwal_confirmed = await update_to_confirm_all(global_vars.system_date, interaction.guild_id, interaction.user.id)
        
    if jadwal_confirmed:
        await interaction.response.send_message(content=f"Berhasil mengonfirmasi {jadwal_confirmed} jadwal Anda hari ini, Terima kasih 🙏", ephemeral=True)
        await update_daily_schedule(interaction.guild_id)
    else:
        await confirm(interaction)

async def quick_confirm(interaction: discord.Interaction, sholat: str):
    await interaction.response.defer(ephemeral=True)

    confirmed_anything = await update_to_confirm_from_reminder(global_vars.system_date, interaction.guild_id, sholat.capitalize(), interaction.user.id)

    if confirmed_anything:
        await interaction.followup.send(f"Berhasil mengonfirmasi jadwal Sholat {sholat.capitalize()} hari ini, Terima kasih 🙏", ephemeral=True)    
        await update_daily_schedule(interaction.guild_id)
    else:
        await interaction.followup.send(f"Anda tidak memiliki jadwal untuk Sholat {sholat.capitalize()} hari ini", ephemeral=True)

@bot.tree.command(name="forcekonfirmasi", description="[ADMIN] Mengonfirmasi presensi untuk jadwal yang dipilih di hari ini", guild=GUILD_ID)
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
async def forcekonfirmasi(interaction: discord.Interaction):
    schedules = await get_all_unconfirmed_schedule_today(global_vars.system_date, interaction.guild_id)
    
    if schedules:
        await interaction.response.send_modal(ForceConfirmModal(schedules))
    else:
        await interaction.response.send_message(content="Tidak ada jadwal yang bisa dikonfirmasi.", ephemeral=True)