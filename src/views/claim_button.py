import discord
from commands.claim import claim

class ClaimButton(discord.ui.View):
    def __init__(self, id_presensi: int):
        super().__init__(timeout=None)
        self.id_presensi = id_presensi

    @discord.ui.button(label="Klaim Jadwal", style=discord.ButtonStyle.primary)
    async def button_claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        await claim(interaction, self.id_presensi)