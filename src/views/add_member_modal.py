import discord
from database.anggota import insert_anggota

class AddMemberModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Tambah Anggota")

        self.add_item(
            discord.ui.Label(
                id=0,
                text="Nama Lengkap",
                component=discord.ui.TextInput()
            )
        )

        self.add_item(
            discord.ui.Label(
                id=1,
                text="Nama Panggilan",
                component=discord.ui.TextInput()
            )
        )

        self.add_item(
            discord.ui.Label(
                id=2,
                text="Akun Discord anggota (opsional)",
                component=discord.ui.UserSelect(
                    placeholder="Pilih anggota",
                    required=False
                )
            )
        )

    async def on_submit(self, interaction):
        guild_id = interaction.guild_id
        nama_panggilan = self.find_item(1).component.value
        nama_lengkap = self.find_item(0).component.value
        discord_uid = self.find_item(2).component.values[0].id if self.find_item(2).component.values else None
        await insert_anggota(guild_id, nama_panggilan, nama_lengkap, discord_uid)
        await interaction.response.send_message(f"Berhasil menambahkan {nama_panggilan} sebagai anggota baru", ephemeral=True)
        
        if discord_uid is not None:
            role = []
            role.append(discord.utils.get(interaction.guild.roles, name="Registered"))
            try:
                await self.find_item(2).component.values[0].edit(nick=nama_panggilan, roles=role)
            except Exception:
                return