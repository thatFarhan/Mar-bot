from config import bot, TugasEnum, SholatEnum, TempatEnum
from server_config import GUILD_ID, SUB_REQUESTS_CHANNEL
import discord
from discord import app_commands
from repository.updater import update_to_claim
from repository.loader import jadwal, save_presence
from repository.persistent_loader import persistent_vars, save_persistent
from global_vars import global_vars
from events.update_schedule_message import update_daily_schedule
from models.Schedule import Schedule

@bot.tree.command(name="forceclaim", description="[ADMIN] Mengklaim suatu jadwal yang perlu pengganti untuk seseorang", guild=GUILD_ID)
@app_commands.checks.has_role("Marbot Mar-bot")
async def forceclaim(interaction: discord.Interaction, tugas: TugasEnum, sholat: SholatEnum, tempat: TempatEnum, pengganti: discord.Member):
    await interaction.response.defer(ephemeral=True)
    jadwal_harian = jadwal.presensi_rawatib[global_vars.system_date]
    if sholat.value not in jadwal_harian[tempat.value] or tugas.value not in jadwal_harian[tempat.value][sholat.value]:
        await interaction.response.send_message(f"Jadwal {tugas.name} Sholat {sholat.name} di {tempat.name} tidak ada", ephemeral=True)
        return

    for id in range(1, len(jadwal.anggota)):
        if pengganti.id == jadwal.anggota[id]['uid']:
            nama_pengklaim = jadwal.anggota[id]['nama']
            schedule = Schedule(global_vars.system_date, tugas, sholat, tempat)
            update_to_claim(schedule, id)
            break
    # for else = will run when for is completed without break
    else:
        await interaction.followup.send("Akun tercantum belum teregistrasi sebagai akun anggota", ephemeral=True)
        return

    await save_presence()
    await update_daily_schedule()

    key = f"{global_vars.system_date}_{tugas.value}_{sholat.value}_{tempat.value}"

    if key not in persistent_vars["notification_ids"]:
        await interaction.followup.send(f"Berhasil mengklaim untuk {nama_pengklaim}, namun notifikasi request pengganti tidak ditemukan")
        return
    
    noti_id = persistent_vars["notification_ids"][key]

    channel = bot.get_channel(SUB_REQUESTS_CHANNEL)
    message = await channel.fetch_message(noti_id)

    embed = discord.Embed(
        title="Detail Jadwal",
        color=discord.Color.green(),
        description=schedule.get_reasoned_desc("Petugas Sebelumnya")
    )

    content=f"**✅ Jadwal telah diklaim oleh {nama_pengklaim}**"

    persistent_vars["notification_ids"].pop(schedule.get_key(), None)
    await save_persistent()

    await message.edit(content=content, embed=embed, view=None)

    await interaction.followup.send(f"Berhasil mengklaim untuk {nama_pengklaim}")

async def claim(interaction: discord.Interaction, requested_schedule: Schedule):
    for id in range(1, len(jadwal.anggota)):
        if interaction.user.id == jadwal.anggota[id]['uid']:
            nama_pengklaim = jadwal.anggota[id]['nama']
            update_to_claim(requested_schedule, id)
            break
    # for else = will run when for is completed without break
    else:
        await interaction.response.send_message("Akun antum belum teregistrasi sebagai akun anggota", ephemeral=True)
        return

    await save_presence()

    embed = discord.Embed(
        title="Detail Jadwal",
        color=discord.Color.green(),
        description=requested_schedule.get_reasoned_desc("Petugas Pengganti", nama_pengklaim)
    )
    content=f"**✅ Jadwal telah diklaim oleh {nama_pengklaim}**"

    persistent_vars["notification_ids"].pop(requested_schedule.get_key(), None)
    await save_persistent()
    
    await interaction.response.edit_message(content=content, embed=embed, view=None)
    await update_daily_schedule()