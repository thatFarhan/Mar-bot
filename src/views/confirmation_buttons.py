import discord
from commands.confirm import confirm_all
from commands.sell import sellmodal
from commands.swap import swaprequestmodal

class ConfirmationButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Konfirmasi Semua", style=discord.ButtonStyle.green, custom_id="button_confirm_all")
    async def button_confirmall(self, interaction: discord.Interaction, button: discord.ui.Button):
        await confirm_all(interaction)

    @discord.ui.button(label="Request Pengganti", style=discord.ButtonStyle.red, custom_id="button_sell")
    async def button_sell(self, interaction: discord.Interaction, button: discord.ui.Button):
        await sellmodal(interaction)

    @discord.ui.button(label="Tukar Jadwal", style=discord.ButtonStyle.primary, custom_id="button_swap")
    async def button_swap(self, interaction: discord.Interaction, button: discord.ui.Button):
        await swaprequestmodal(interaction)