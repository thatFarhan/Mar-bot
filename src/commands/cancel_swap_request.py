import discord
from config import NAMA_HARI
from repository.loader import jadwal
from repository.persistent_loader import save_persistent
from models.Schedule import Schedule
from events.purge_transaction import purge_offerers

async def cancel_swap_request(interaction: discord.Interaction, requested_schedule: Schedule):
    id_peminta = requested_schedule.get_pic_id()
    uid_peminta = jadwal.anggota[id_peminta]['uid']

    if interaction.user.id != uid_peminta:
        await interaction.response.send_message("Lau sape mpruy? 🫵😂", ephemeral=True)
        return
    
    embed=discord.Embed(
        title="Detail Jadwal", 
        color=discord.Color.red(),
        description=requested_schedule.get_reasoned_desc("Petugas Sebelumnya")
    )

    content=f"❌ **Permintaan Dibatalkan**"

    await interaction.response.edit_message(content=content, embed=embed, view=None)

    await purge_offerers(requested_schedule, "❌ Permintaan Dibatalkan")
    await save_persistent()