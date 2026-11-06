import discord
from models.Schedule import Schedule
from events.purge_transaction import delete_offer

async def cancel_swap_offer(interaction: discord.Interaction, requested_schedule: Schedule, offered_schedule: Schedule):
    uid_requestor = requested_schedule.uid_petugas
    uid_offerer = offered_schedule.uid_petugas

    if interaction.user.id != uid_requestor and interaction.user.id != uid_offerer:
        await interaction.response.send_message("Lau sape mpruy? 🫵😂", ephemeral=True)
        return

    content=f"**❌ Tawaran Dibatalkan**"
    
    await interaction.response.edit_message(content=content, view=None)
    await delete_offer(requested_schedule, offered_schedule)