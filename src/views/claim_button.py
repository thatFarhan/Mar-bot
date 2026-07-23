import discord
from commands.claim import claim
from models.Schedule import Schedule

class ClaimButton(discord.ui.View):
    def __init__(self, requested_schedule: Schedule):
        super().__init__(timeout=None)
        self.requested_schedule = requested_schedule

    @discord.ui.button(label="Klaim Jadwal", style=discord.ButtonStyle.primary)
    async def button_claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        await claim(interaction, self.requested_schedule)