import discord
from commands.claim import claim

class ClaimButton(discord.ui.View):
    def __init__(self, tugas: str, sholat: str, tempat: str, embed_desc: str):
        super().__init__()
        self.tugas = tugas
        self.sholat = sholat
        self.tempat = tempat
        self.embed_desc = embed_desc

    @discord.ui.button(label="Klaim Jadwal", style=discord.ButtonStyle.primary)
    async def button_claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        await claim(interaction, self.tugas, self.sholat, self.tempat, self.embed_desc)