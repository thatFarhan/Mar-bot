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

    if interaction.user.id == uid_peminta:
        content=f"**❌ Tawaran Ditolak**"
    else:
        content=f"**❌ Tawaran Dibatalkan**"
    
    await interaction.response.edit_message(content=content, view=None)

    offer_key = f"{requested_schedule.get_key()}_{offered_schedule.get_key()}"
    offerer_channel_id = persistent_vars["swap_notification_ids"][offer_key]["offerer_channel_id"]
    offerer_message_id = persistent_vars["swap_notification_ids"][offer_key]["offerer_message_id"]
    dm_channel = bot.get_channel(offerer_channel_id)

    if dm_channel is None:
        dm_channel = await bot.fetch_channel(offerer_channel_id)

    try:
        dm_message = await dm_channel.fetch_message(offerer_message_id)
        await dm_message.edit(content="**❌ Afwan, Tawaran Antum Ditolak.**", view=None)
    except Exception:
        pass

    persistent_vars["swap_notification_ids"].pop(f"{requested_schedule.get_key()}_{offered_schedule.get_key()}", None)
    await save_persistent()