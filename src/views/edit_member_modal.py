import discord
from database.anggota import update_name

class EditMemberModal(discord.ui.Modal):
    def __init__(self, id_anggota: int, nama_lengkap: str, nama_panggilan: str):
        self.id_anggota = id_anggota
        super().__init__(title="Edit Anggota")

        self.add_item(
            discord.ui.Label(
                id=0,
                text="Nama Lengkap",
                component=discord.ui.TextInput(default=nama_lengkap)
            )
        )

        self.add_item(
            discord.ui.Label(
                id=1,
                text="Nama Panggilan",
                component=discord.ui.TextInput(default=nama_panggilan)
            )
        )

    async def on_submit(self, interaction):
        nama_panggilan = self.find_item(1).component.value
        nama_lengkap = self.find_item(0).component.value
        await update_name(self.id_anggota, nama_panggilan, nama_lengkap)
        await interaction.response.send_message(f"Berhasil mengubah nama anggota dengan id {self.id_anggota}", ephemeral=True)