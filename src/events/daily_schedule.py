from data.loader import jadwal, save_presence
from config import bot, DAILY_SCHEDULE_CHANNEL
from views.confirmation_buttons import ConfirmationButtons
from global_vars import global_vars
from data.persistent_loader import persistent_vars, save_persistent
from builders.daily_schedule_builder import build_schedule_and_tags
from events.update_schedule_message import update_daily_schedule

async def send_daily_schedule():
    embeds=[]
    tags=set()
    for tempat in jadwal.jadwal_rawatib[global_vars.system_day_name]:
        schedule_and_tags = build_schedule_and_tags(tempat)
        if schedule_and_tags:
            embeds.append(schedule_and_tags[0])
            for tag in schedule_and_tags[1]:
                tags.add(tag)

    daily_schedule_channel=bot.get_channel(DAILY_SCHEDULE_CHANNEL)
    message = await daily_schedule_channel.send(
        content=f"## 💫 Jadwal hari {global_vars.system_day_name}\n## 🌃 Lailatukumus Sa'idah Ikhwan~\nBerikut adalah jadwal petugas untuk esok hari. Mohon untuk konfirmasi kehadiran jika bisa berhadir atau request pengganti jika tidak.\nJazaakumullaahu Khoiron, Baarakallahu Fiikum 🙏\n\n{' '.join(tags)}\n\n",
        embeds=embeds,
        view=ConfirmationButtons()
    )
    persistent_vars["current_daily_schedule_id"] = message.id
    await save_persistent()

async def write_todays_pic():
    jadwal_hariini = dict(jadwal.jadwal_rawatib[global_vars.system_day_name])

    if global_vars.system_day_name == "Jum'at":
        if global_vars.system_date in jadwal.jadwal_jumat:
            jadwal_hariini["msu"]["dzuhur"] = {"Muadzin": {"id_anggota": jadwal.jadwal_jumat[global_vars.system_date]}}

    for tempat in jadwal_hariini:
        for sholat in jadwal_hariini[tempat]:
            for tugas in jadwal_hariini[tempat][sholat]:
                # additional attributes
                petugas=jadwal_hariini[tempat][sholat][tugas]
                petugas['confirmed'] = False
                petugas['need_sub'] = False
                petugas['id_sub'] = 0

    await save_presence(jadwal_hariini)
    await update_daily_schedule()