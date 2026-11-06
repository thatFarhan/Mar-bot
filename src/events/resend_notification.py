from config import bot
from events.on_sale_notification import on_sale_noti

from database.presensi import get_schedule_by_id
from database.notifikasi import get_sub_request_noti, get_swap_request_noti

async def resend_request_noti(id_presensi: int, id_server: int, is_sub: bool = True):
    if is_sub:
        notifikasi = await get_sub_request_noti(id_presensi)
    else:
        notifikasi = await get_swap_request_noti(id_presensi)
    id_notifikasi = notifikasi["id_notifikasi"]
    message_id = notifikasi["requestor_message_id"]
    channel_id = notifikasi["requestor_channel_id"]

    channel = bot.get_channel(channel_id)
    if channel is None:
        channel = await bot.fetch_channel(channel_id)

    try:
        message = await channel.fetch_message(message_id)
        await message.delete()
    except Exception:
        pass

    schedule = await get_schedule_by_id(id_presensi)
    await on_sale_noti(id_server, schedule, prev_id_notifikasi=id_notifikasi, is_sub=is_sub)