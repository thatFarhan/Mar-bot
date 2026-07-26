import discord
from config import bot
from repository.persistent_loader import persistent_vars, save_persistent
from repository.loader import jadwal
from models.Schedule import Schedule
from events.purge_transaction import purge_requestors

async def cancel_swap_offer(interaction: discord.Interaction, requested_schedule: Schedule, offered_schedule: Schedule):
    id_peminta = requested_schedule.get_pic_id()
    id_penawar = offered_schedule.get_pic_id()
    uid_peminta = jadwal.anggota[id_peminta]['uid']
    uid_penawar = jadwal.anggota[id_penawar]['uid']

    if interaction.user.id != uid_peminta and interaction.user.id != uid_penawar:
        await interaction.response.send_message("Lau sape mpruy? 🫵😂", ephemeral=True)
        return

    content=f"**❌ Tawaran Dibatalkan**"
    
    await interaction.response.edit_message(content=content, view=None)
    await purge_requestors(offered_schedule, "❌ Tawaran Dibatalkan Oleh Penawar")
    await save_persistent()