import copy
from repository.loader import jadwal, save_new_schedule
from config import bot, NAMA_HARI
from server_config import DAILY_SCHEDULE_CHANNEL, SUB_REQUESTS_CHANNEL
from views.confirmation_buttons import ConfirmationButtons
from global_vars import global_vars
from repository.persistent_loader import persistent_vars, save_persistent
from builders.daily_schedule_builder import build_schedule_and_tags
from events.on_sale_notification import on_sale_noti
from mission_util import to_datetime, to_indo_date_format
from datetime import timedelta, date
from models.Schedule import Schedule
from events.update_schedule_message import remove_buttons_from_daily_schedule

from database.presensi import tanggal_and_masjid_exists_in_presensi, insert_many_presensi
from database.masjid import get_all_id_masjid_and_is_weekly
from database.jadwal_tetap import get_id_jadwal_tetap_on_day

async def send_daily_schedule():
    await remove_buttons_from_daily_schedule()
    embeds=[]
    tags=set()
    jadwal_harian = jadwal.presensi_rawatib[global_vars.system_date]
    for place in jadwal_harian:
        schedule_and_tags = build_schedule_and_tags(place)
        if schedule_and_tags:
            embeds.append(schedule_and_tags[0])
            for tag in schedule_and_tags[1]:
                tags.add(tag)
            
            need_subs = schedule_and_tags[2]
            if need_subs:
                for need_sub in need_subs:
                    values = need_sub.split("_")
                    tugas = values[0]
                    sholat = values[1]
                    tempat = values[2]
                    schedule = Schedule(global_vars.system_date, tugas, sholat, tempat)
                    key = schedule.get_key()
                    if key in persistent_vars["notification_ids"]:
                        channel = bot.get_channel(SUB_REQUESTS_CHANNEL)
                        noti_id = persistent_vars["notification_ids"][key]
                        try:
                            message = await channel.fetch_message(noti_id)
                            await message.delete()
                        except Exception:
                            pass

                    await on_sale_noti(schedule)

    daily_schedule_channel=bot.get_channel(DAILY_SCHEDULE_CHANNEL)
    message = await daily_schedule_channel.send(
        content=f"📜 Anda ada jadwal esok hari!\n\n{' '.join(tags)}\n# 📌 {global_vars.system_day_name} ({to_indo_date_format(global_vars.system_date)})",
        embeds=embeds,
        view=ConfirmationButtons()
    )
    persistent_vars["current_daily_schedule_id"] = message.id
    await save_persistent()

async def write_todays_pic():
    jadwal_harian = copy.deepcopy(jadwal.jadwal_rawatib[global_vars.system_day_name])

    if global_vars.system_day_name == "Jum'at":
        if global_vars.system_date in jadwal.jadwal_jumat:
            jadwal_harian["msu"]["dzuhur"] = {"Muadzin": {"id_anggota": jadwal.jadwal_jumat[global_vars.system_date]}}

    for tempat in jadwal_harian:
        for sholat in jadwal_harian[tempat]:
            for tugas in jadwal_harian[tempat][sholat]:
                # additional attributes
                petugas=jadwal_harian[tempat][sholat][tugas]
                petugas['confirmed'] = False
                petugas['need_sub'] = False
                petugas['id_sub'] = 0

    await save_new_schedule(jadwal_harian, global_vars.system_date)

async def write_pics_weekahead():
    pics = []
    masjids = await get_all_id_masjid_and_is_weekly()
    for i in range(7):
        iterated_date = (to_datetime(global_vars.system_date) + timedelta(days=i)).date()
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
