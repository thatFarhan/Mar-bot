import discord
from models.Schedule import Schedule
from commands.accept_swap import accept
from commands.reject_swap import reject

class AcceptButton(discord.ui.View):
    def __init__(self, requested_schedule: Schedule, offered_schedule: Schedule):
        super().__init__(timeout=None)
        self.requested_schedule = requested_schedule
        self.offered_schedule = offered_schedule

    @discord.ui.button(label="Terima", style=discord.ButtonStyle.green)
    async def button_claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        await accept(interaction, self.requested_schedule, self.offered_schedule)

    @discord.ui.button(label="Tolak", style=discord.ButtonStyle.red)
    async def button_reject(self, interaction: discord.Interaction, button: discord.ui.Button):
        await reject(interaction, self.requested_schedule, self.offered_schedule)