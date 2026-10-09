import datetime
import discord
from discord import app_commands
from config import bot, TEMPAT_TITLE
from server_config import GUILD_ID
from repository.loader import jadwal, save_json
from views.jumat_schedule_modal import JumatScheduleModal

@bot.tree.command(name="editjadwaljumat", description="[ADMIN] Menambah atau mengubah jadwal Muadzin Jum'at", guild=GUILD_ID)
@app_commands.checks.has_role("Marbot Mar-bot")
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
async def editjadwaljumat(interaction: discord.Interaction):
    await interaction.response.send_modal(JumatScheduleModal())

@bot.tree.command(name="hapusjadwaljumat", description="[ADMIN] Menghapus suatu jadwal Muadzin Jum'at", guild=GUILD_ID)
@app_commands.checks.has_role("Marbot Mar-bot")
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
async def hapusjadwaljumat(interaction: discord.Interaction, tanggal: str):
    if tanggal not in jadwal.jadwal_jumat:
        await interaction.response.send_message("Tanggal tidak valid", ephemeral=True)
        return

    jadwal.jadwal_jumat.pop(tanggal)
    await save_json("src/data/jadwal_jumat.json", jadwal.jadwal_jumat)
    await interaction.response.send_message("Berhasil menghapus jadwal", ephemeral=True)

@hapusjadwaljumat.autocomplete("tanggal")
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
        embed_desc.append(f"`{tanggal}:` **{anggota}**")

    content = "## ☀️ Jadwal Muadzin Jum'at"
    embed = discord.Embed(
        title=TEMPAT_TITLE["msu"],
        description="\n".join(embed_desc)
    )
    await interaction.response.send_message(content=content, embed=embed)

@bot.tree.command(name="clearjadwaljumat", description="[ADMIN] Menghapus seluruh jadwal Muadzin Jum'at", guild=GUILD_ID)
@app_commands.checks.has_role("Marbot Mar-bot")
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
async def clearjadwaljumat(interaction: discord.Interaction):
    jadwal.jadwal_jumat.clear()
    await save_json("src/data/jadwal_jumat.json", jadwal.jadwal_jumat)
    await interaction.response.send_message("Berhasil menghapus seluruh jadwal Muadzin Jum'at", ephemeral=True)