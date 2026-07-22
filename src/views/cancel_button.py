import discord
from models.Schedule import Schedule
from commands.cancel_swap_offer import cancel_swap_offer

class CancelButton(discord.ui.View):
    def __init__(self, requested_schedule: Schedule, offered_schedule: Schedule):
        super().__init__(timeout=None)
        self.requested_schedule = requested_schedule
        self.offered_schedule = offered_schedule

    @discord.ui.button(label="Batalkan", style=discord.ButtonStyle.red)
    async def button_cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await cancel_swap_offer(interaction, self.requested_schedule, self.offered_schedule)