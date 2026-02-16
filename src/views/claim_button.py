import discord
import json
from data.loader import jadwal
from data.updater import update_to_claim, update_to_confirm

class ClaimButton(discord.ui.View):
    def __init__(self, tugas: str, sholat: str, tempat: str, embed_desc: str):
        super().__init__()
        self.tugas = tugas
        self.sholat = sholat
        self.tempat = tempat
        self.embed_desc = embed_desc

    @discord.ui.button(label="Klaim Jadwal", style=discord.ButtonStyle.primary)
    async def button_claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        tugas = self.tugas
        sholat = self.sholat
        tempat = self.tempat
        embed_desc = self.embed_desc

        petugas = jadwal.jadwal_hariini[tempat][sholat][tugas]

        if petugas['uid'] == interaction.user.id:
            update_to_confirm(tugas, sholat, tempat)
        else:
            update_to_claim(tugas, sholat, tempat, interaction.user.id)

        with open('jadwal_hariini.json', 'w') as file:
            json.dump(jadwal.jadwal_hariini, file, indent=2)

        embed = discord.Embed(
            title=f"Detail Jadwal",
            color=discord.Color.green(),
            description=embed_desc
        )
        content=f"**✅ Jadwal telah diklaim oleh {jadwal.nama_asli[str(interaction.user.id)]} ✅**"
        await interaction.response.edit_message(content=content, embed=embed, view=None)