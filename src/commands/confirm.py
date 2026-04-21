from discord import app_commands
import discord
from config import bot, TugasEnum, SholatEnum, TempatEnum
from server_config import GUILD_ID
from repository.loader import jadwal, save_presence
from repository.updater import update_to_confirm
from events.update_schedule_message import update_daily_schedule
from views.confirm_modal import ConfirmModal

@bot.tree.command(name="konfirmasi", description="Mengonfirmasi presensi untuk jadwal yang antum pilih di hari ini", guild=GUILD_ID)
async def confirm(interaction: discord.Interaction):
    select_options = []
    for tempat in jadwal.jadwal_hariini:
        for sholat in jadwal.jadwal_hariini[tempat]:
            for tugas in jadwal.jadwal_hariini[tempat][sholat]:
                
                petugas = jadwal.jadwal_hariini[tempat][sholat][tugas]
                detail_petugas = jadwal.anggota[petugas['id_anggota']]
                    
                if detail_petugas["uid"] != interaction.user.id or petugas["confirmed"]:
                    continue

                select_options.append(discord.SelectOption(label=f"{tugas.capitalize()} Sholat {sholat.capitalize()} di {tempat.upper()}", value=f"{tempat}_{sholat}_{tugas}"))

    if len(select_options) == 0:
        await interaction.response.send_message(content="Tidak ada jadwal yang bisa di konfirmasi", ephemeral=True)
    elif len(select_options) == 1:
        select_values = select_options[0].value.split("_")
        tempat = select_values[0]
        sholat = select_values[1]
        tugas = select_values[2]
        update_to_confirm(tugas, sholat, tempat)
        await save_presence(jadwal.jadwal_hariini)
        await interaction.response.send_message(f"Berhasil mengonfirmasi jadwal {tugas} Sholat {sholat.capitalize()} di {tempat.upper()}, Syukran Jazilan 🙏", ephemeral=True)
        await update_daily_schedule()
    else:
        await interaction.response.send_modal(ConfirmModal(select_options))

async def confirm_all(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    confirmed_anything = False
    for tempat in jadwal.jadwal_hariini:
        for sholat in jadwal.jadwal_hariini[tempat]:
            for tugas in jadwal.jadwal_hariini[tempat][sholat]:
                petugas = jadwal.jadwal_hariini[tempat][sholat][tugas]
                detail_petugas = jadwal.anggota[petugas['id_anggota']]
                if detail_petugas["uid"] == interaction.user.id and not petugas["confirmed"] and not petugas["need_sub"]:
                    update_to_confirm(tugas, sholat, tempat)
                    confirmed_anything = True
        
    if confirmed_anything:
        await save_presence(jadwal.jadwal_hariini)
        await interaction.followup.send(content="Berhasil mengonfirmasi jadwal antum hari ini, Syukran Jazilan 🙏", ephemeral=True)
        await update_daily_schedule()
    else:
        await interaction.followup.send(content="Tidak ada jadwal yang bisa di konfirmasi", ephemeral=True)

async def quick_confirm(interaction: discord.Interaction, sholat: str):
    await interaction.response.defer(ephemeral=True)
    confirmed_anything = False
    for tempat in jadwal.jadwal_hariini:

        if sholat not in jadwal.jadwal_hariini[tempat]:
            continue

        for tugas in jadwal.jadwal_hariini[tempat][sholat]:
            petugas = jadwal.jadwal_hariini[tempat][sholat][tugas]
            detail_petugas = jadwal.anggota[petugas['id_anggota']]

            if detail_petugas['uid'] != interaction.user.id or petugas['confirmed']:
                continue

            update_to_confirm(tugas, sholat, tempat)
            confirmed_anything = True

    if confirmed_anything:
        await save_presence(jadwal.jadwal_hariini)
        await interaction.followup.send(f"Berhasil mengonfirmasi jadwal Sholat {sholat.capitalize()} hari ini, Syukran Jazilan 🙏", ephemeral=True)    
        await update_daily_schedule()
    else:
        await interaction.followup.send(f"Antum tidak memiliki jadwal untuk Sholat {sholat.capitalize()} hari ini", ephemeral=True)

@bot.tree.command(name="forceconfirm", description="[ADMIN] Mengonfirmasi presensi suatu jadwal", guild=GUILD_ID)
@app_commands.checks.has_role("Marbot Mar-bot")
async def forceconfirm(interaction: discord.Interaction, tugas: TugasEnum, sholat: SholatEnum, tempat: TempatEnum):
    if sholat.value not in jadwal.jadwal_hariini[tempat.value] or tugas.value not in jadwal.jadwal_hariini[tempat.value][sholat.value]:
        await interaction.response.send_message(f"Jadwal {tugas.name} Sholat {sholat.name} di {tempat.name} tidak ada", ephemeral=True)
        return
    
    update_to_confirm(tugas.value, sholat.value, tempat.value)
    await save_presence(jadwal.jadwal_hariini)

    await interaction.response.send_message(f"Berhasil mengonfirmasi jadwal {tugas.name} Sholat {sholat.name} di {tempat.name}, Syukran Jazilan 🙏", ephemeral=True)
    await update_daily_schedule()