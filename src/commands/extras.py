import discord
from discord import app_commands
from config import bot, GUILD_ID, SHOLAT_TITLE
from global_vars import global_vars
from data.loader import jadwal

@bot.tree.command(name="jadwalsholat", description="Menampilkan jadwal sholat untuk bulan ini pada tanggal tertentu", guild=GUILD_ID)
async def jadwalsholat(interaction: discord.Interaction, tanggal: str):
    if tanggal == "today":
        target_date=global_vars.actual_date

    elif tanggal == "tomorrow":
        target_date=global_vars.actual_date + 1

    else:
        try:
            target_date=int(tanggal) - 1
        except ValueError:
            await interaction.response.send_message("Parameter harus berupa angka atau 'Hari ini' / 'Besok'", ephemeral=True)
            return
        
    if target_date > len(jadwal.jadwal_sholat_bulanini) - 1:
        await interaction.response.send_message("Tanggal tidak bisa melebihi tanggal terakhir bulan ini", ephemeral=True)
        return
    
    if target_date < 0:
        await interaction.response.send_message("Tanggal harus lebih dari 1", ephemeral=True)
        return

    embed=discord.Embed(
        title=f"🕌 Jadwal Sholat {jadwal.jadwal_sholat_bulanini[target_date]['hari']}, {jadwal.jadwal_sholat_bulanini[target_date]['tanggal_lengkap']}",
        color=discord.Color.green()
    )

    for sholat in SHOLAT_TITLE:
        embed.add_field(
            name=SHOLAT_TITLE[sholat],
            value=jadwal.jadwal_sholat_bulanini[target_date][sholat],
            inline=True
        )

    await interaction.response.send_message(embed=embed)

@jadwalsholat.autocomplete("tanggal")
async def hari_autocomplete(interaction: discord.Interaction, tanggal: str):
    choices=[
        app_commands.Choice(name="Hari ini", value="today"),
        app_commands.Choice(name="Besok", value="tomorrow")
    ]

    return choices