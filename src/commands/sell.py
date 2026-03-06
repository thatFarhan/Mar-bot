import discord
from discord import app_commands
from config import bot, TugasEnum, SholatEnum, TempatEnum, GUILD_ID
from data.loader import jadwal, save_presence, save_reason
from data.updater import update_to_sell
from events.on_sale_notification import on_sale_noti
from events.update_schedule_message import update_daily_schedule
from data.persistent_loader import persistent_vars
from views.sell_modal import SellModal

@bot.tree.command(name="sell", description="Merequest pengganti untuk jadwal yang antum pilih di hari ini", guild=GUILD_ID)
async def sell(interaction: discord.Interaction):
    await sellmodal(interaction)

async def sellmodal(interaction: discord.Interaction):
    try:
        await interaction.response.send_modal(SellModal(interaction.user.id))
    except discord.errors.HTTPException:
        await interaction.response.send_message(content="Antum tidak memiliki jadwal hari ini", ephemeral=True)

# failed to confirm on time
async def emergency_sell(tugas: str, sholat: str, tempat: str):
    alasan_absen = "Gagal konfirmasi tepat waktu"
    id_petugas = jadwal.jadwal_hariini[tempat][sholat][tugas]["id_anggota"]

    if jadwal.alasan_absen_hariini is None:
        jadwal.alasan_absen_hariini = {}

    jadwal.alasan_absen_hariini[str(id_petugas)] = alasan_absen
    await save_reason()

    update_to_sell(tugas, sholat, tempat)
    await save_presence(jadwal.jadwal_hariini)
    await on_sale_noti(tugas, sholat, tempat, emergency=True, alasan=alasan_absen)

@bot.tree.command(name="forcesell", description="[ADMIN] Merequest pengganti untuk suatu jadwal", guild=GUILD_ID)
@app_commands.checks.has_role("Marbot Mar-bot")
async def forcesell(interaction: discord.Interaction, tugas: TugasEnum, sholat: SholatEnum, tempat: TempatEnum):
    if sholat.value not in jadwal.jadwal_hariini[tempat.value] or tugas.value not in jadwal.jadwal_hariini[tempat.value][sholat.value]:
        await interaction.response.send_message(f"Jadwal {tugas.name} Sholat {sholat.name} di {tempat.name} tidak ada", ephemeral=True)
        return

    update_to_sell(tugas, sholat, tempat)
    emergency = persistent_vars["reminder_sent"][sholat.value]
    await on_sale_noti(tugas.value, sholat.value, tempat.value, emergency=emergency)
    await save_presence(jadwal.jadwal_hariini)

    await interaction.response.send_message(f"Berhasil meminta pengganti untuk {tugas.name} Sholat {sholat.name} di {tempat.name}", ephemeral=True)
    await update_daily_schedule()