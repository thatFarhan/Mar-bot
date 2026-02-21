import discord
from discord import app_commands
from config import bot, GUILD_ID, WELCOME_CHANNEL
from data.loader import jadwal, save_json

@bot.event
async def on_member_join(member: discord.Member):
    role = discord.utils.get(member.guild.roles, name="Unregistered")
    await member.add_roles(role)

    channel = bot.get_channel(WELCOME_CHANNEL)
    embed = discord.Embed(
        title=f"👋 Ahlan wa Sahlan, akhi {member.display_name}!",
        description="Sebelum menggunakan layanan Mar-bot, silahkan untuk melakukan registrasi dengan command di bawah ini:\n\n`✨ /register [nama antum]`\n\n Jika nama antum tidak tertera, harap untuk menghubungi admin terdekat. Jazaakallaahu Khoiron, Baarakallahu Fiik 🙏",
        color=discord.Color.green()
    )
    await channel.send(content=member.mention, embed=embed)

@bot.event
async def on_member_remove(member: discord.Member):
    uid = member.id
    for anggota in jadwal.anggota:
        if anggota['uid'] == uid:
            anggota['uid'] = 0
            save_json("src/data/anggota.json", jadwal.anggota)
            break

@app_commands.checks.has_role("Unregistered")
@bot.tree.command(name="register", description="Memasukkan UID Discord antum ke dalam sistem", guild=GUILD_ID)
async def register(interaction: discord.Interaction, nama: int):
    jadwal.anggota[nama]['uid'] = interaction.user.id
    save_json("src/data/anggota.json", jadwal.anggota)

    role = []
    role.append(discord.utils.get(interaction.guild.roles, name="Registered"))
    await interaction.user.edit(nick=jadwal.anggota[nama]['nama'], roles=role)
    await interaction.response.send_message(content=f"Berhasil registrasi atas nama {jadwal.anggota[nama]['nama_lengkap']}. Syukran 🙏", ephemeral=True)

@register.autocomplete("nama")
async def nama_autocomplete(interaction: discord.Interaction, nama: int):
    choices = []
    for i in range(1, len(jadwal.anggota)):
        if jadwal.anggota[i]['uid'] == 0:
            choices.append(app_commands.Choice(name=jadwal.anggota[i]['nama_lengkap'], value=i))

    return choices