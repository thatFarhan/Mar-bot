import time

from config import bot
from global_vars import global_vars
from models.Schedule import Schedule

from database.notifikasi import get_related_notis, delete_related_notis, get_swap_offer_noti, delete_noti_by_id, get_offers_from_request, delete_notis_by_ids, get_expired_notis, delete_expireds

async def delete_offer(requested_schedule: Schedule, offered_schedule: Schedule):
    id_requested_schedule = requested_schedule.id_presensi
    id_offered_schedule = offered_schedule.id_presensi

    swap_offer_noti = await get_swap_offer_noti(id_requested_schedule, id_offered_schedule)

    await edit_to_disable_message(swap_offer_noti["requestor_channel_id"], swap_offer_noti["requestor_message_id"], "❌ Tawaran Dibatalkan Oleh Penawar")
    await delete_noti_by_id(swap_offer_noti["id_notifikasi"])

async def delete_request(requested_schedule: Schedule):
    id_requested_schedule = requested_schedule.id_presensi

    offers = await get_offers_from_request(id_requested_schedule)
    noti_ids = []

    for offer in offers:
        await edit_to_disable_message(offer["offerer_channel_id"], offer["offerer_message_id"], "❌ Permintaan Dibatalkan")
        await edit_to_disable_message(offer["requestor_channel_id"], offer["requestor_message_id"], "❌ Permintaan Dibatalkan")
        noti_ids.append(offer["id_notifikasi"])

    await delete_notis_by_ids(noti_ids)

async def purge_expireds():
    expired_notis = await get_expired_notis(global_vars.system_date)
    for expired_noti in expired_notis:
        await edit_to_disable_message(expired_noti["offerer_channel_id"], expired_noti["offerer_message_id"], "⌛ Jadwal Kadaluarsa")
        await edit_to_disable_message(expired_noti["requestor_channel_id"], expired_noti["requestor_message_id"], "⌛ Jadwal Kadaluarsa")
        time.sleep(1)
    
    await delete_expireds(global_vars.system_date)

async def purge_related_notifications(id_presensi: int):
    related_notis = await get_related_notis(id_presensi)
    for related_noti in related_notis:
        match related_noti["type"]:
            case "sub_request":
                await edit_to_disable_message(related_noti["requestor_channel_id"], related_noti["requestor_message_id"], "🤷 Jadwal Telah Diisi")
            case "swap_request":
                await edit_to_disable_message(related_noti["requestor_channel_id"], related_noti["requestor_message_id"], "🤷 Jadwal Telah Diisi")
            case "swap_offer":
                await edit_to_disable_message(related_noti["offerer_channel_id"], related_noti["offerer_message_id"], "🤷 Jadwal Telah Diisi")
                await edit_to_disable_message(related_noti["requestor_channel_id"], related_noti["requestor_message_id"], "🤷 Jadwal Telah Diisi")
    
    await delete_related_notis(id_presensi)

async def edit_to_disable_message(channel_id: int, message_id: int, content: str):
    if channel_id is None or message_id is None: return
    channel = bot.get_channel(channel_id)
    try:
        message = await channel.fetch_message(message_id)
        await message.edit(content=f"**{content}**", view=None)
    except Exception:
        pass