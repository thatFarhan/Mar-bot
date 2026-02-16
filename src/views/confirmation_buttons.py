import discord
from commands.confirm import confirm_all
from commands.sell import sell_all

class ConfirmationButtons(discord.ui.View):
    @discord.ui.button(label="Konfirmasi Semua", style=discord.ButtonStyle.green)
    async def button_confirmall(self, interaction: discord.Interaction, button: discord.ui.Button):
        await confirm_all(interaction)

    @discord.ui.button(label="Request Pengganti Semua", style=discord.ButtonStyle.red)
    async def button_sellall(self, interaction: discord.Interaction, button: discord.ui.Button):
        await sell_all(interaction)