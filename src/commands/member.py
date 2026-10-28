import discord
from discord import app_commands
from config import bot
from server_config import GUILD_ID, WELCOME_CHANNEL
from views.add_member_modal import AddMemberModal
from views.name_picker import NamePicker, ConfirmDeletionView, ConfirmUnregisterView, ConfirmRegisterView, ForceRegisterView
from database.anggota import update_to_remove_uid_using_details, get_all_anggota_from_server, get_all_registered_anggota_from_server, check_anggota_exists, get_all_unregistered_anggota_from_server


class RegisterButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Daftar", style=discord.ButtonStyle.primary)
    async def button_claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        await register(interaction)
@bot.event
async def on_member_join(member: discord.Member):
    role = discord.utils.get(member.guild.roles, name="Unregistered")
    await member.add_roles(role)

    channel = bot.get_channel(WELCOME_CHANNEL)
    embed = discord.Embed(
        title=f"👋 Ahlan wa Sahlan, akhi {member.display_name}!",
        description="Sebelum menggunakan layanan Mar-bot, silahkan untuk melakukan registrasi dengan tombol **\"Daftar\"** atau command di bawah ini:\n## `✨ /daftar`\n Jika nama Anda tidak tertera, harap untuk menghubungi admin terdekat. Jazaakallaahu Khoiron, Baarakallahu Fiik 🙏"
    )
    await channel.send(content=member.mention, embed=embed, view=RegisterButton())

@bot.event
async def on_member_remove(member: discord.Member):
    await update_to_remove_uid_using_details(member.id, member.guild.id)

@bot.tree.command(name="daftar", description="Memasukkan UID Discord Anda ke dalam sistem", guild=GUILD_ID)
async def daftar(interaction: discord.Interaction):
    await register(interaction)

async def register(interaction: discord.Interaction):
    already_registered = await check_anggota_exists(interaction.guild_id, interaction.user.id)
    if already_registered:
        await interaction.response.send_message("Anda sudah terdaftar", ephemeral=True)
        return

    rows = await get_all_unregistered_anggota_from_server(interaction.guild_id)
    if not rows:
        await interaction.response.send_message("Tidak ada nama yang tersedia. Hubungi admin terdekat.", ephemeral=True)
        return
    await interaction.response.send_message("## 📝 Pendaftaran Anggota", view=NamePicker(rows, ConfirmRegisterView), ephemeral=True)

@bot.tree.command(name="forcedaftar", description="[ADMIN] Memasukkan UID Discord seorang member ke dalam sistem", guild=GUILD_ID)
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
async def forcedaftar(interaction: discord.Interaction):
    rows = await get_all_unregistered_anggota_from_server(interaction.guild_id)
    if not rows:
        await interaction.response.send_message("Tidak ada nama yang tersedia.", ephemeral=True)
        return
    await interaction.response.send_message("## 📝 Force Pendaftaran Anggota", view=NamePicker(rows, ForceRegisterView), ephemeral=True)

@bot.tree.command(name="undaftar", description="[ADMIN] Membatalkan pendaftaran seorang member", guild=GUILD_ID)
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
async def unregister(interaction: discord.Interaction, member: discord.Member):
    removed = await update_to_remove_uid_using_details(member.id, interaction.guild_id)
    if removed:
        await interaction.response.send_message(content=f"Berhasil menghapus UID {member.nick}.", ephemeral=True)
    else:
        await interaction.response.send_message("Akun tersebut belum teregistrasi sebagai akun anggota", ephemeral=True)

    role = []
    role.append(discord.utils.get(interaction.guild.roles, name="Unregistered"))
    try:
        await member.edit(roles=role, nick=member.global_name)
    except Exception:
        return

@bot.tree.command(name="hapusuid", description="[ADMIN] Hapus UID dari anggota.", guild=GUILD_ID)
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
async def hapusuid(interaction: discord.Interaction):
    rows = await get_all_registered_anggota_from_server(interaction.guild_id)
    if not rows:
        await interaction.response.send_message("Tidak ada nama yang tersedia.", ephemeral=True)
        return
    await interaction.response.send_message("## 📝 Batalkan Pendaftaran Anggota", view=NamePicker(rows, ConfirmUnregisterView), ephemeral=True)

@bot.tree.command(name="tambahanggota", description="[ADMIN] Menambah anggota baru.", guild=GUILD_ID)
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
async def tambahanggota(interaction: discord.Interaction):
    await interaction.response.send_modal(AddMemberModal())

@bot.tree.command(name="editanggota", description="[ADMIN] Mengubah nama anggota.", guild=GUILD_ID)
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
async def editanggota(interaction: discord.Interaction):
    rows = await get_all_anggota_from_server(interaction.guild_id)
    if not rows:
        await interaction.response.send_message("Tidak ada nama yang tersedia.", ephemeral=True)
        return
    await interaction.response.send_message("## 📝 Edit Nama Anggota", view=NamePicker(rows), ephemeral=True)

@bot.tree.command(name="hapusanggota", description="[ADMIN] Menghapus anggota.", guild=GUILD_ID)
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
async def hapusanggota(interaction: discord.Interaction):
    rows = await get_all_anggota_from_server(interaction.guild_id)
    if not rows:
        await interaction.response.send_message("Tidak ada nama yang tersedia.", ephemeral=True)
        return
    await interaction.response.send_message("## 🗑️ Penghapusan Anggota", view=NamePicker(rows, ConfirmDeletionView), ephemeral=True)