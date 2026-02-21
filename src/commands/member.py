import discord
from discord import app_commands
from config import bot, GUILD_ID
from data.loader import jadwal, save_json

@bot.tree.command(name="unregister", description="[ADMIN] Unregisters a member", guild=GUILD_ID)
@app_commands.checks.has_role("Marbot Mar-bot")
async def unregister(interaction: discord.Interaction, member: discord.Member):
    for id in range(1, len(jadwal.anggota)):
        if member.id == jadwal.anggota[id]['uid']:
            role = []
            role.append(discord.utils.get(interaction.guild.roles, name="Unregistered"))
            await member.edit(roles=role, nick=member.global_name)

            jadwal.anggota[id]['uid'] = 0
            save_json("src/data/anggota.json", jadwal.anggota)
            await interaction.response.send_message(content=f"Berhasil menghapus UID {jadwal.anggota[id]['nama_lengkap']}.", ephemeral=True)
            break
    # for else = will run when for is completed without break
    else:
        await interaction.response.send_message("Akun tersebut belum teregistrasi sebagai akun anggota", ephemeral=True)

@bot.tree.command(name="removeuid", description="[ADMIN] Hanya hapus UID dari anggota.", guild=GUILD_ID)
@app_commands.checks.has_role("Marbot Mar-bot")
async def removeuid(interaction: discord.Interaction, nama: int):
    jadwal.anggota[nama]['uid'] = 0
    save_json("src/data/anggota.json", jadwal.anggota)
    await interaction.response.send_message(content=f"Berhasil menghapus UID atas nama {jadwal.anggota[nama]['nama_lengkap']}.", ephemeral=True)

@removeuid.autocomplete("nama")
async def nama_autocomplete(interaction: discord.Interaction, nama: int):
    choices = []
    for i in range(1, len(jadwal.anggota)):
        if jadwal.anggota[i]['uid'] != 0:
            choices.append(app_commands.Choice(name=jadwal.anggota[i]['nama_lengkap'], value=i))

    return choices

@bot.tree.command(name="addmember", description="[ADMIN] Menambah anggota baru.", guild=GUILD_ID)
@app_commands.checks.has_role("Marbot Mar-bot")
async def addmember(interaction: discord.Interaction, nama_panggilan: str, nama_lengkap: str):
    for i in range(1, len(jadwal.anggota)):
        if jadwal.anggota[i]['nama'] != "":
            continue

        jadwal.anggota[i]['nama'] = nama_panggilan
        jadwal.anggota[i]['nama_lengkap'] = nama_lengkap
        break
    # for else = will run when for is completed without break
    else:
        new_anggota = {
            'uid': 0,
            'nama': nama_panggilan,
            'nama_lengkap': nama_lengkap
        }

        jadwal.anggota.append(new_anggota)
    
    save_json("src/data/anggota.json", jadwal.anggota)
    await interaction.response.send_message(content=f"Berhasil menambah anggota baru dengan id_anggota = {i}.", ephemeral=True)

@bot.tree.command(name="removemember", description="[ADMIN] Menghapus anggota.", guild=GUILD_ID)
@app_commands.checks.has_role("Marbot Mar-bot")
async def removemember(interaction: discord.Interaction, nama: int):
    if nama == len(jadwal.anggota) - 1:
        jadwal.anggota.pop(nama)
    else:
        jadwal.anggota[nama]['uid'] = 0
        jadwal.anggota[nama]['nama'] = ""
        jadwal.anggota[nama]['nama_lengkap'] = ""
    save_json("src/data/anggota.json", jadwal.anggota)
    await interaction.response.send_message(content=f"Berhasil menghapus anggota dengan id_member = {nama}.", ephemeral=True)

@removemember.autocomplete("nama")
async def nama_autocomplete(interaction: discord.Interaction, nama: int):
    choices = []
    for i in range(1, len(jadwal.anggota)):
        choices.append(app_commands.Choice(name=jadwal.anggota[i]['nama_lengkap'], value=i))

    return choices