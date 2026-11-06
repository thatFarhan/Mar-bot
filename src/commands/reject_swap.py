import discord
from config import bot
from models.Schedule import Schedule

from events.update_schedule_message import update_daily_schedule

from database.notifikasi import get_swap_offer_noti, delete_noti_by_id

async def reject(interaction: discord.Interaction, requested_schedule: Schedule, offered_schedule: Schedule):
    if interaction.user.id != requested_schedule.uid_petugas and interaction.user.id != offered_schedule.uid_petugas:
        await interaction.response.send_message("Lau sape mpruy? 🫵😂", ephemeral=True)
        return

    if interaction.user.id == requested_schedule.uid_petugas:
        content=f"**❌ Tawaran Ditolak**"
    else:
        content=f"**❌ Tawaran Dibatalkan**"
    
    await interaction.response.edit_message(content=content, view=None)

    swap_offer_noti = await get_swap_offer_noti(requested_schedule.id_presensi, offered_schedule.id_presensi)
    offerer_channel_id = swap_offer_noti["offerer_channel_id"]
    offerer_message_id = swap_offer_noti["offerer_message_id"]
    dm_channel = bot.get_channel(offerer_channel_id)

    if dm_channel is None:
        dm_channel = await bot.fetch_channel(offerer_channel_id)

    try:
        dm_message = await dm_channel.fetch_message(offerer_message_id)
        await dm_message.edit(content="**❌ Maaf, Tawaran Anda Ditolak.**", view=None)
    except Exception:
        pass

    await delete_noti_by_id(swap_offer_noti["id_notifikasi"])
    await update_daily_schedule(interaction.guild_id)