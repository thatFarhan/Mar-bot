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
from datetime import timedelta
from models.Schedule import Schedule

async def send_daily_schedule():
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
        content=f"📜 Antum ada jadwal esok hari!\n\n{' '.join(tags)}\n# 📌 {global_vars.system_day_name} ({to_indo_date_format(global_vars.system_date)})",
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

async def write_pic(date: str):
    datetime_object = to_datetime(date)
    day_name = NAMA_HARI[datetime_object.weekday()]
    jadwal_sehari = copy.deepcopy(jadwal.jadwal_rawatib[day_name])

    if day_name == "Jum'at":
        if date in jadwal.jadwal_jumat:
            jadwal_sehari["msu"]["dzuhur"] = {"Muadzin": {"id_anggota": jadwal.jadwal_jumat[date]}}

    for tempat in jadwal_sehari:
        for sholat in jadwal_sehari[tempat]:
            for tugas in jadwal_sehari[tempat][sholat]:
                # additional attributes
                petugas=jadwal_sehari[tempat][sholat][tugas]
                petugas['confirmed'] = False
                petugas['need_sub'] = False
                petugas['id_sub'] = 0
    
    await save_new_schedule(jadwal_sehari, date)

async def write_pics_weekahead():
    for i in range(7):
        iterated_date = to_datetime(global_vars.system_date) + timedelta(i)
        str_iterated_date = str(iterated_date.date())
        if str_iterated_date not in jadwal.presensi_rawatib:
            await write_pic(str_iterated_date)