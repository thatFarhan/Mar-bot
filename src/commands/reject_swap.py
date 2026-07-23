import discord
from config import bot
from repository.persistent_loader import persistent_vars, save_persistent
from repository.loader import jadwal
from models.Schedule import Schedule

async def reject(interaction: discord.Interaction, requested_schedule: Schedule, offered_schedule: Schedule):
    id_peminta = requested_schedule.get_pic_id()
    id_penawar = offered_schedule.get_pic_id()
    uid_peminta = jadwal.anggota[id_peminta]['uid']
    uid_penawar = jadwal.anggota[id_penawar]['uid']

    if interaction.user.id != uid_peminta and interaction.user.id != uid_penawar:
        await interaction.response.send_message("Lau sape mpruy? 🫵😂", ephemeral=True)
        return

    embeds_peminta = []

    embed_permintaan=discord.Embed(
        title="Jadwal yang Akan Diserahkan", 
        color=discord.Color.red(),
        description=requested_schedule.get_unreasoned_desc("Petugas Sebelumnya")
    )
    embeds_peminta.append(embed_permintaan)
        
    embed_tawaran=discord.Embed(
        title="Jadwal yang Akan Diterima", 
        color=discord.Color.red(),
        description=offered_schedule.get_unreasoned_desc("Petugas Sebelumnya")
    )
    embeds_peminta.append(embed_tawaran)

    if interaction.user.id == uid_peminta:
        content=f"**❌ Tawaran Ditolak**"
    else:
        content=f"**❌ Tawaran Dibatalkan**"
    
    await interaction.response.edit_message(content=content, embeds=embeds_peminta, view=None)

    offer_key = f"{requested_schedule.get_key()}_{offered_schedule.get_key()}"
    offerer_channel_id = persistent_vars["swap_notification_ids"][offer_key]["offerer_channel_id"]
    offerer_message_id = persistent_vars["swap_notification_ids"][offer_key]["offerer_message_id"]
    dm_channel = bot.get_channel(offerer_channel_id)

    if dm_channel is None:
        dm_channel = await bot.fetch_channel(offerer_channel_id)

    embed_tawaran.title = "Jadwal yang Akan Diserahkan"
    embed_permintaan.title = "Jadwal yang Akan Diterima"
    embeds_penawar = [embed_tawaran, embed_permintaan]

    try:
        dm_message = await dm_channel.fetch_message(offerer_message_id)
        await dm_message.edit(content="❌ Afwan, Tawaran Antum Ditolak.", embeds=embeds_penawar)
    except Exception:
        pass

    persistent_vars["swap_notification_ids"].pop(f"{requested_schedule.get_key()}_{offered_schedule.get_key()}", None)
    await save_persistent()