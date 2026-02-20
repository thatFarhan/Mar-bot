from discord import app_commands
import discord
import json
from config import bot, TugasEnum, SholatEnum, TempatEnum, GUILD_ID
from data.loader import jadwal, save_presence
from data.updater import update_to_confirm

@bot.tree.command(name="confirm", description="Mengonfirmasi presensi suatu jadwal antum di hari ini", guild=GUILD_ID)
@app_commands.describe(tugas="Tugas yang mana?", sholat="Sholat apa?", tempat="Dimana?")
async def confirm(interaction: discord.Interaction, tugas: TugasEnum, sholat: SholatEnum, tempat: TempatEnum):
    if sholat.value not in jadwal.jadwal_hariini[tempat.value] or tugas.value not in jadwal.jadwal_hariini[tempat.value][sholat.value]:
        await interaction.response.send_message(f"Jadwal {tugas.name} Sholat {sholat.name} di {tempat.name} tidak ada", ephemeral=True)
        return
    
    petugas = jadwal.jadwal_hariini[tempat.value][sholat.value][tugas.value]
    detail_petugas = jadwal.anggota[petugas['id_anggota']]

    if detail_petugas['uid'] == interaction.user.id and not petugas['confirmed']:
        update_to_confirm(tugas.value, sholat.value, tempat.value)
        save_presence(jadwal.jadwal_hariini)

        await interaction.response.send_message(f"Berhasil mengonfirmasi jadwal {tugas.name} Sholat {sholat.name} di {tempat.name}, Syukran Jazilan 🙏", ephemeral=True)
    else:
        await interaction.response.send_message(f"Jadwal sudah dikonfirmasi atau antum tidak memiliki jadwal {tugas.name} Sholat {sholat.name} di {tempat.name} pada hari ini", ephemeral=True)

@bot.tree.command(name="confirmall", description="Mengonfirmasi presensi untuk seluruh jadwal antum hari ini", guild=GUILD_ID)
async def confirmall(interaction: discord.Interaction):
    await confirm_all(interaction)

async def confirm_all(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    confirmed_anything = False
    for tempat in jadwal.jadwal_hariini:
        for sholat in jadwal.jadwal_hariini[tempat]:
            for tugas in jadwal.jadwal_hariini[tempat][sholat]:
                petugas = jadwal.jadwal_hariini[tempat][sholat][tugas]
                detail_petugas = jadwal.anggota[petugas['id_anggota']]
                if detail_petugas['uid'] == interaction.user.id and not petugas['confirmed']:
                    update_to_confirm(tugas, sholat, tempat)
                    confirmed_anything = True
        
    if confirmed_anything:
        save_presence(jadwal.jadwal_hariini)
        await interaction.followup.send(content="Berhasil mengonfirmasi seluruh jadwal antum hari ini, Syukran Jazilan 🙏", ephemeral=True)
    else:
        await interaction.followup.send(content="Jadwal sudah dikonfirmasi atau antum tidak memiliki jadwal hari ini", ephemeral=True)

async def quick_confirm(interaction: discord.Interaction, sholat: str):
    await interaction.response.defer(ephemeral=True)
    for tempat in jadwal.jadwal_hariini:

        if sholat not in jadwal.jadwal_hariini[tempat]:
            continue

        for tugas in jadwal.jadwal_hariini[tempat][sholat]:
            petugas = jadwal.jadwal_hariini[tempat][sholat][tugas]
            detail_petugas = jadwal.anggota[petugas['id_anggota']]

            if detail_petugas['uid'] != interaction.user.id or petugas['confirmed']:
                continue

            update_to_confirm(tugas, sholat, tempat)
            save_presence(jadwal.jadwal_hariini)

            await interaction.followup.send(f"Berhasil mengonfirmasi jadwal {tugas} Sholat {sholat.capitalize()} di {tempat.upper()}, Syukran Jazilan 🙏", ephemeral=True)
            return

    await interaction.followup.send(f"Antum tidak memiliki jadwal untuk Sholat {sholat.capitalize()} hari ini", ephemeral=True)