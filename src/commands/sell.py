import discord
from discord import app_commands
from config import bot, TugasEnum, SholatEnum, TempatEnum
from server_config import GUILD_ID
from repository.loader import jadwal, save_presence, save_reason
from repository.updater import update_to_sell
from events.on_sale_notification import on_sale_noti
from events.update_schedule_message import update_daily_schedule
from repository.persistent_loader import persistent_vars
from views.sell_modal import SellModal, SellWeekModal
from global_vars import global_vars

@bot.tree.command(name="request", description="Merequest pengganti untuk jadwal yang antum pilih di hari ini", guild=GUILD_ID)
async def sell(interaction: discord.Interaction):
    await sellmodal(interaction)

@bot.tree.command(name="requestpekan", description="Merequest pengganti untuk jadwal yang antum pilih di pekan ini", guild=GUILD_ID)
async def sellweek(interaction: discord.Interaction):
    await sellweekmodal(interaction)

async def sellmodal(interaction: discord.Interaction):
    try:
        await interaction.response.send_modal(SellModal(interaction.user.id))
    except discord.errors.HTTPException:
        await interaction.response.send_message(content="Tidak ada jadwal yang bisa di request pengganti", ephemeral=True)

async def sellweekmodal(interaction: discord.Interaction):
    try:
        await interaction.response.send_modal(SellWeekModal(interaction.user.id))
    except discord.errors.HTTPException:
        await interaction.response.send_message(content="Tidak ada jadwal yang bisa di request pengganti", ephemeral=True)

# failed to confirm on time
async def emergency_sell(tugas: str, sholat: str, tempat: str):
    jadwal_harian = jadwal.presensi_rawatib[global_vars.system_date]
    id_petugas = jadwal_harian[tempat][sholat][tugas]["id_anggota"]
    alasan = "Gagal konfirmasi tepat waktu"
    alasan_dict = {id_petugas: alasan}
    jadwal.alasan_absen[global_vars.system_date][id_petugas] = alasan_dict
    await save_reason()

    update_to_sell(tugas, sholat, tempat)
    await save_presence(jadwal.presensi_rawatib[global_vars.system_date])
    await on_sale_noti(tugas, sholat, tempat, emergency=True)

@bot.tree.command(name="forcerequest", description="[ADMIN] Merequest pengganti untuk suatu jadwal", guild=GUILD_ID)
@app_commands.checks.has_role("Marbot Mar-bot")
async def forcesell(interaction: discord.Interaction, tugas: TugasEnum, sholat: SholatEnum, tempat: TempatEnum):
    jadwal_harian = jadwal.presensi_rawatib[global_vars.system_date]
    if sholat.value not in jadwal_harian[tempat.value] or tugas.value not in jadwal_harian[tempat.value][sholat.value]:
        await interaction.response.send_message(f"Jadwal {tugas.name} Sholat {sholat.name} di {tempat.name} tidak ada", ephemeral=True)
        return

    update_to_sell(tugas, sholat, tempat)
    emergency = persistent_vars["reminder_sent"][sholat.value]
    await on_sale_noti(tugas.value, sholat.value, tempat.value, emergency=emergency)
    await save_presence(jadwal.presensi_rawatib[global_vars.system_date])

    await interaction.response.send_message(f"Berhasil meminta pengganti untuk {tugas.name} Sholat {sholat.name} di {tempat.name}", ephemeral=True)
    await update_daily_schedule()