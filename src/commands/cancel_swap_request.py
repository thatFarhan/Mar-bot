import discord
from models.Schedule import Schedule
from events.purge_transaction import delete_request

from database.presensi import update_to_unswap

async def cancel_swap_request(interaction: discord.Interaction, requested_schedule: Schedule):
    uid_requestor = requested_schedule.uid_petugas

    if interaction.user.id != uid_requestor:
        await interaction.response.send_message("Lau sape mpruy? 🫵😂", ephemeral=True)
        return

    content=f"❌ **Permintaan Dibatalkan**"

    await interaction.response.edit_message(content=content, view=None)
    await update_to_unswap(requested_schedule.id_presensi)
    await delete_request(requested_schedule)