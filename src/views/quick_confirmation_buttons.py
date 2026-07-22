import discord
from commands.confirm import quick_confirm
from commands.sell import sellmodal
from commands.swap import swaprequestmodal

class QuickConfirmationButtons(discord.ui.View):
    def __init__(self, sholat: str):
        super().__init__(timeout=None)
        self.sholat = sholat

    @discord.ui.button(label="Konfirmasi", style=discord.ButtonStyle.green)
    async def button_confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        await quick_confirm(interaction, self.sholat)

    @discord.ui.button(label="Request Pengganti", style=discord.ButtonStyle.red)
    async def button_sell(self, interaction: discord.Interaction, button: discord.ui.Button):
        await sellmodal(interaction)

    @discord.ui.button(label="Tukar Jadwal", style=discord.ButtonStyle.primary)
    async def button_swap(self, interaction: discord.Interaction, button: discord.ui.Button):
        await swaprequestmodal(interaction)