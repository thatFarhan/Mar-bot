import discord
import json
from discord import app_commands
from config import bot, TugasEnum, SholatEnum, TempatEnum, GUILD_ID
from data.loader import jadwal
from data.updater import update_to_sell
from events.on_sale_notification import on_sale_noti

@bot.tree.command(name="sell", description="Merequest pengganti untuk suatu jadwal antum di hari ini", guild=GUILD_ID)
@app_commands.describe(tugas="Tugas yang mana?", sholat="Sholat apa?", tempat="Dimana?")
async def sell(interaction: discord.Interaction, tugas: TugasEnum, sholat: SholatEnum, tempat: TempatEnum):
    if sholat.value not in jadwal.jadwal_hariini[tempat.value] or tugas.value not in jadwal.jadwal_hariini[tempat.value][sholat.value]:
        await interaction.response.send_message(f"Jadwal {tugas.name} Sholat {sholat.name} di {tempat.name} tidak ada", ephemeral=True)
        return

    petugas = jadwal.jadwal_hariini[tempat.value][sholat.value][tugas.value]
    if (petugas['uid'] == interaction.user.id or petugas['uid_sub'] == interaction.user.id) and not petugas['need_sub']:
        update_to_sell(tugas, sholat, tempat)
        await on_sale_noti(tugas.value, sholat.value, tempat.value)
        with open('jadwal_hariini.json', 'w') as file:
            json.dump(jadwal.jadwal_hariini, file, indent=2)

        await interaction.response.send_message(f"Berhasil meminta pengganti untuk {tugas.name} Sholat {sholat.name} di {tempat.name}", ephemeral=True)
    else:
        await interaction.response.send_message(f"Antum tidak memiliki jadwal {tugas.name} Sholat {sholat.name} di {tempat.name} pada hari ini", ephemeral=True)

@bot.tree.command(name="sellall", description="Merequest pengganti untuk seluruh jadwal antum di hari ini", guild=GUILD_ID)
async def sellall(interaction: discord.Interaction):
    await sell_all(interaction)

async def sell_all(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    sold_anything = False
    for tempat in jadwal.jadwal_hariini:
        for sholat in jadwal.jadwal_hariini[tempat]:
            for tugas in jadwal.jadwal_hariini[tempat][sholat]:
                
                petugas = jadwal.jadwal_hariini[tempat][sholat][tugas]
                if (petugas['uid'] == interaction.user.id or petugas['uid_sub'] == interaction.user.id) and not petugas['need_sub']:
                    update_to_sell(tugas, sholat, tempat)
                    await on_sale_noti(tugas, sholat, tempat)
                    sold_anything = True
        
    if sold_anything:
        with open('jadwal_hariini.json', 'w') as file:
            json.dump(jadwal.jadwal_hariini, file, indent=2)

        await interaction.followup.send(content="Berhasil meminta pengganti untuk seluruh jadwal antum hari ini", ephemeral=True)
    else:
        await interaction.followup.send(content="Antum tidak memiliki jadwal hari ini", ephemeral=True)

async def quick_sell(interaction: discord.Interaction, sholat: str):
    await interaction.response.defer(ephemeral=True)
    for tempat in jadwal.jadwal_hariini:

        if sholat not in jadwal.jadwal_hariini[tempat]:
            continue

        for tugas in jadwal.jadwal_hariini[tempat][sholat]:
            petugas=jadwal.jadwal_hariini[tempat][sholat][tugas]

            if tugas == 'Pembaca Hadits': continue

            if (petugas['uid'] == interaction.user.id or petugas['uid_sub'] == interaction.user.id) and not petugas['need_sub']:
                update_to_sell(tugas, sholat, tempat)
                await on_sale_noti(tugas, sholat, tempat, emergency=True)
                with open('jadwal_hariini.json', 'w') as file:
                    json.dump(jadwal.jadwal_hariini, file, indent=2)

                await interaction.followup.send(f"Berhasil meminta pengganti untuk {tugas} Sholat {sholat.capitalize()} di {tempat.upper()}", ephemeral=True)
                return

    await interaction.followup.send(f"Antum tidak memiliki jadwal untuk Sholat {sholat.capitalize()} hari ini", ephemeral=True)

# failed to confirm on time
async def emergency_sell(tugas: str, sholat: str, tempat: str):
    update_to_sell(tugas, sholat, tempat)
    await on_sale_noti(tugas, sholat, tempat, emergency=True)
    with open('jadwal_hariini.json', 'w') as file:
        json.dump(jadwal.jadwal_hariini, file, indent=2)