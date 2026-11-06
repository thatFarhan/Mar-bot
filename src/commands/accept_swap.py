import discord
from config import bot
from events.update_schedule_message import update_daily_schedule
from models.Schedule import Schedule
from events.purge_transaction import purge_related_notifications
from global_vars import global_vars

from database.presensi import update_to_claim_by_id
from database.notifikasi import get_swap_request_noti, get_swap_offer_noti, delete_noti_by_id

async def accept(interaction: discord.Interaction, requested_schedule: Schedule, offered_schedule: Schedule, id_server: int):
    if interaction.user.id != requested_schedule.uid_petugas:
        await interaction.response.send_message("Lau sape mpruy? 🫵😂", ephemeral=True)
        return

    id_requestor = requested_schedule.id_petugas
    id_offerer = offered_schedule.id_petugas

    id_requested_schedule = requested_schedule.id_presensi
    id_offered_schedule = offered_schedule.id_presensi

    await update_to_claim_by_id(id_requested_schedule, id_offerer, requested_schedule.tanggal == global_vars.system_date)
    await update_to_claim_by_id(id_offered_schedule, id_requestor, offered_schedule.tanggal == global_vars.system_date)

    content=f"**✅ Tawaran Diterima**"

    await interaction.response.edit_message(content=content, view=None)
    await update_daily_schedule(id_server)

    embed_accepted_swap = discord.Embed(
        title="Detail Penukaran Jadwal"
    )

    embed_accepted_swap.add_field(
        name="Jadwal A",
        value=requested_schedule.get_desc(),
        inline=False
    )

    embed_accepted_swap.add_field(
        name="🔃",
        value="",
        inline=False
    )

    embed_accepted_swap.add_field(
        name="Jadwal B",
        value=offered_schedule.get_desc(),
        inline=False
    )

    swap_request_noti = await get_swap_request_noti(id_requested_schedule)
    request_message_id = swap_request_noti["requestor_message_id"]
    requestor_channel_id = swap_request_noti["requestor_channel_id"]
    channel = bot.get_channel(requestor_channel_id)
    request_message = await channel.fetch_message(request_message_id)
    await request_message.edit(content="**✅ Jadwal Telah Ditukar**", embed=embed_accepted_swap, view=None)

    swap_offer_noti = await get_swap_offer_noti(id_requested_schedule, id_offered_schedule)
    offerer_channel_id = swap_offer_noti["offerer_channel_id"]
    offerer_message_id = swap_offer_noti["offerer_message_id"]
    dm_channel = bot.get_channel(offerer_channel_id)

    if dm_channel is None:
        dm_channel = await bot.fetch_channel(offerer_channel_id)

    try:
        await dm_channel.send(content="✅ Tawaran Anda Diterima!", embed=embed_accepted_swap)
    except Exception:
        # TODO: make the logic for this
        pass

    dm_message = await dm_channel.fetch_message(offerer_message_id)
    await dm_message.delete()

    await delete_noti_by_id(swap_request_noti["id_notifikasi"])
    await delete_noti_by_id(swap_offer_noti["id_notifikasi"])
    await purge_related_notifications(id_requested_schedule)
    await purge_related_notifications(id_offered_schedule)