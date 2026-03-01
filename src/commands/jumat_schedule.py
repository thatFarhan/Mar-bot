import datetime
import discord
from discord import app_commands
from config import bot, GUILD_ID, TEMPAT_TITLE
from data.loader import jadwal, save_json

@bot.tree.command(name="modifyjumatschedule", description="[ADMIN] Menambah atau mengubah jadwal Muadzin Jum'at", guild=GUILD_ID)
@app_commands.checks.has_role("Marbot Mar-bot")
async def modifyjumatschedule(interaction: discord.Interaction, tanggal: str, nama: int):
    try:
        chosen_date = tanggal.split("-")
        year = int(chosen_date[0])
        month = int(chosen_date[1])
        day = int(chosen_date[2])
        date_obj = datetime.date(year, month, day)

        if date_obj.weekday() != 4:
            await interaction.response.send_message("Tanggal harus bertepatan dengan hari Jum'at", ephemeral=True)
            return
    except ValueError:
        await interaction.response.send_message("Tanggal harus menggunakan format YYYY-MM-DD", ephemeral=True)
        return

    jadwal.jadwal_jumat[tanggal] = nama
    save_json("src/data/jadwal_jumat.json", jadwal.jadwal_jumat)
    await interaction.response.send_message("Berhasil memodifikasi jadwal Jum'at", ephemeral=True)

@modifyjumatschedule.autocomplete("tanggal")
async def tanggal_autocomplete(interaction: discord.Interaction, tanggal: str):
    choices = []
    for date in jadwal.jadwal_jumat:
        choices.append(app_commands.Choice(name=date, value=date))

    return choices

@modifyjumatschedule.autocomplete("nama")
async def nama_autocomplete(interaction: discord.Interaction, nama: int):
    choices = []
    for i in range(1, len(jadwal.anggota)):
        choices.append(app_commands.Choice(name=jadwal.anggota[i]['nama'], value=i))

    return choices

@bot.tree.command(name="deletejumatschedule", description="[ADMIN] Menghapus suatu jadwal Muadzin Jum'at", guild=GUILD_ID)
@app_commands.checks.has_role("Marbot Mar-bot")
async def deletejumatschedule(interaction: discord.Interaction, tanggal: str):
    if tanggal not in jadwal.jadwal_jumat:
        await interaction.response.send_message("Tanggal tidak valid", ephemeral=True)
        return

    jadwal.jadwal_jumat.pop(tanggal)
    save_json("src/data/jadwal_jumat.json", jadwal.jadwal_jumat)
    await interaction.response.send_message("Berhasil menghapus jadwal", ephemeral=True)

@deletejumatschedule.autocomplete("tanggal")
async def tanggal_autocomplete(interaction: discord.Interaction, tanggal: str):
    choices = []
    for date in jadwal.jadwal_jumat:
        choices.append(app_commands.Choice(name=date, value=date))

    return choices

@bot.tree.command(name="jadwaljumat", description="Menampilkan jadwal Muadzin Jum'at", guild=GUILD_ID)
async def jadwaljumat(interaction: discord.Interaction):
    embed_desc = []
    for tanggal in jadwal.jadwal_jumat:
        anggota = jadwal.anggota[jadwal.jadwal_jumat[tanggal]]["nama"]
        embed_desc.append(f"{tanggal}: **{anggota}**")

    content = "## ☀️ Jadwal Muadzin Jum'at"
    embed = discord.Embed(
        title=TEMPAT_TITLE["msu"],
        description="\n".join(embed_desc), 
        color=discord.Color.green()
    )
    await interaction.response.send_message(content=content, embed=embed)