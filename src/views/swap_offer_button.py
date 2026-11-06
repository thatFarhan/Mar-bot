import discord

from models.Schedule import Schedule
from commands.cancel_swap_request import cancel_swap_request
from commands.offer_swap import offer_swap

from database.presensi import get_schedule_by_id

class OfferButton(discord.ui.View):
    def __init__(self, id_presensi):
        super().__init__(timeout=None)
        self.id_presensi = id_presensi

    @discord.ui.button(label="Tawarkan Penukaran", style=discord.ButtonStyle.primary)
    async def button_offer(self, interaction: discord.Interaction, button: discord.ui.Button):
        requested_schedule = await get_schedule_by_id(self.id_presensi)
        requested_schedule_obj = Schedule(requested_schedule)

        await offer_swap(interaction, requested_schedule_obj)

    @discord.ui.button(label="Batalkan", style=discord.ButtonStyle.red)
    async def button_cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        requested_schedule = await get_schedule_by_id(self.id_presensi)
        requested_schedule_obj = Schedule(requested_schedule)
        
        await cancel_swap_request(interaction, requested_schedule_obj)