import discord
from config import bot
from repository.persistent_loader import persistent_vars, save_persistent
from repository.loader import jadwal
from models.Schedule import Schedule

async def cancel_swap_offer(interaction: discord.Interaction, requested_schedule: Schedule, offered_schedule: Schedule):
    id_peminta = requested_schedule.get_pic_id()
    id_penawar = offered_schedule.get_pic_id()
    uid_peminta = jadwal.anggota[id_peminta]['uid']
    uid_penawar = jadwal.anggota[id_penawar]['uid']

    if interaction.user.id != uid_peminta and interaction.user.id != uid_penawar:
        await interaction.response.send_message("Lau sape mpruy? 🫵😂", ephemeral=True)
        return

    embeds_penawar = []

    embed_tawaran=discord.Embed(
        title="Jadwal yang Akan Diserahkan", 
        color=discord.Color.red(),
        description=requested_schedule.get_unreasoned_desc("Petugas Sebelumnya:")
    )
    embeds_penawar.append(embed_tawaran)

    embed_permintaan=discord.Embed(
        title="Jadwal yang Akan Diterima", 
        color=discord.Color.red(),
        description=offered_schedule.get_unreasoned_desc("Petugas Sebelumnya:")
    )
    embeds_penawar.append(embed_permintaan)

    content=f"**❌ Tawaran Dibatalkan**"
    
    await interaction.response.edit_message(content=content, embeds=embeds_penawar, view=None)

    request_key = f"{requested_schedule.get_key()}_{offered_schedule.get_key()}"
    requestor_channel_id = persistent_vars["swap_notification_ids"][request_key]["requestor_channel_id"]
    requestor_message_id = persistent_vars["swap_notification_ids"][request_key]["requestor_message_id"]
    dm_channel = bot.get_channel(requestor_channel_id)

    if dm_channel is None:
        dm_channel = await bot.fetch_channel(requestor_channel_id)

    embed_permintaan.title = "Jadwal yang Akan Diserahkan"
    embed_tawaran.title = "Jadwal yang Akan Diterima"
    embeds_peminta = [embed_permintaan, embed_tawaran]

    try:
        dm_message = await dm_channel.fetch_message(requestor_message_id)
        await dm_message.edit(content="**❌ Tawaran Dibatalkan Oleh Penawar**", embeds=embeds_peminta, view=None)
    except Exception:
        # TODO: make the logic for this
        pass    

    persistent_vars["swap_notification_ids"].pop(request_key, None)
    await save_persistent()