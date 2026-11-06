from config import bot
from views.confirmation_buttons import ConfirmationButtons
from global_vars import global_vars
from builders.daily_schedule_builder import build_schedule_and_tags
from events.resend_notification import resend_request_noti
from mission_util import to_indo_date_format
from datetime import timedelta
from events.update_schedule_message import remove_buttons_from_daily_schedule

from database.presensi import tanggal_and_masjid_exists_in_presensi, insert_many_presensi, get_daily_schedule_for_masjid
from database.masjid import get_all_id_masjid_and_is_weekly, get_enabled_masjids_from_server
from database.jadwal_tetap import get_id_jadwal_tetap_on_day
from database.discord_server import update_daily_schedule_message_id, get_daily_schedule_message_id

async def send_daily_schedule(id_server: int, schedule_channel: int):
    schedule_message_id = await get_daily_schedule_message_id(id_server)
    await remove_buttons_from_daily_schedule(schedule_channel, schedule_message_id)
    embeds=[]
    tags=set()
    date_object = global_vars.system_date
    masjids = await get_enabled_masjids_from_server(id_server)
    for masjid in masjids:
        jadwal_harian = await get_daily_schedule_for_masjid(date_object, masjid["id_masjid"])
        schedule_and_tags = build_schedule_and_tags(jadwal_harian)

        if not schedule_and_tags:
            continue

        embeds.append(schedule_and_tags["embed"])
        for tag in schedule_and_tags["tags"]:
            tags.add(tag)

        for id_presensi in schedule_and_tags["need_subs"]:
            await resend_request_noti(id_presensi, id_server, is_sub=True)

        for id_presensi in schedule_and_tags["swap_requesteds"]:
            await resend_request_noti(id_presensi, id_server, is_sub=False)

    daily_schedule_channel=bot.get_channel(schedule_channel)
    message = await daily_schedule_channel.send(
        content=f"📜 Anda ada jadwal esok hari!\n\n{' '.join(tags)}\n# 📌 {global_vars.system_day_name} ({to_indo_date_format(global_vars.system_date)})",
        embeds=embeds,
        view=ConfirmationButtons()
    )

    await update_daily_schedule_message_id(id_server, message.id)

async def write_pics_weekahead():
    pics = []
    masjids = await get_all_id_masjid_and_is_weekly()
    for i in range(7):
        iterated_date = global_vars.system_date + timedelta(days=i)
        for masjid in masjids:
            if await tanggal_and_masjid_exists_in_presensi(iterated_date, masjid["id_masjid"]):
                continue

            if masjid["is_weekly"]:
                hari = iterated_date.weekday()
            else:
                hari = iterated_date.day

            jadwal_ids = await get_id_jadwal_tetap_on_day(hari, masjid["id_masjid"])
            for jadwal_id in jadwal_ids:
                pics.append((iterated_date, jadwal_id))

    if pics:   
        await insert_many_presensi(pics)
