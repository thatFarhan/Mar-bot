import discord
from commands.cancel_swap_request import cancel_swap_request
from views.swap_offer_modal import SwapOfferModal
from models.Schedule import Schedule
from repository.loader import jadwal

class OfferButton(discord.ui.View):
    def __init__(self, requested_schedule: Schedule):
        super().__init__(timeout=None)
        self.requested_schedule = requested_schedule

    @discord.ui.button(label="Tawarkan Penukaran", style=discord.ButtonStyle.primary)
    async def button_offer(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == jadwal.anggota[self.requested_schedule.get_pic_id()]["uid"]:
            await interaction.response.send_message("Tidak bisa menawarkan penukaran ke jadwal sendiri.", ephemeral=True)
            return
        
        try:
            await interaction.response.send_modal(SwapOfferModal(interaction.user.id, self.requested_schedule))
        except discord.errors.HTTPException:
            await interaction.response.send_message(content="Tidak ada jadwal yang bisa ditawarkan", ephemeral=True)

    @discord.ui.button(label="Batalkan", style=discord.ButtonStyle.red)
    async def button_cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await cancel_swap_request(interaction, self.requested_schedule)