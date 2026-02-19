import discord
from data.loader import jadwal, save_presence
from config import TEMPAT_TITLE, SHOLAT_TITLE
from views.confirmation_buttons import ConfirmationButtons
from global_vars import global_vars

def build_schedule_and_tags(tempat: str, system_day_name: str):
    schedule=discord.Embed(
            title=TEMPAT_TITLE[tempat],
            color=discord.Color.green()
        )

    tags=set()
    for sholat in jadwal.jadwal_rawatib[f'{system_day_name}'][tempat]:
        field_values=[]
        for tugas in jadwal.jadwal_rawatib[f'{system_day_name}'][tempat][sholat]:
            id_anggota = jadwal.jadwal_rawatib[system_day_name][tempat][sholat][tugas]['id_anggota']
            anggota = jadwal.anggota[id_anggota]
            field_values.append(f"**{tugas}:** {anggota['nama']}")
            tags.add(f"<@{anggota['uid']}>")

        schedule.add_field(
            name=f"{SHOLAT_TITLE[sholat]} ({jadwal.jadwal_sholat_bulanini[global_vars.system_date][sholat]})",
            value="\n".join(field_values),
            inline=True
        )
    
    return [schedule, tags]

async def send_daily_schedule(target):
    if target:
        global_vars.system_day_name=jadwal.jadwal_sholat_bulanini[global_vars.system_date]['hari']

        embeds=[]
        tags=set()
        for tempat in jadwal.jadwal_rawatib[global_vars.system_day_name]:
            schedule_and_tags=build_schedule_and_tags(tempat, global_vars.system_day_name)
            embeds.append(schedule_and_tags[0])
            for tag in schedule_and_tags[1]:
                tags.add(tag)

        await target.send(
            content=f"# 💫 Jadwal hari {global_vars.system_day_name}\n## 🌃 Lailatukumus Sa'idah Ikhwan~\nBerikut adalah jadwal petugas untuk esok hari. Mohon untuk konfirmasi kehadiran jika bisa berhadir atau request pengganti jika tidak.\nJazaakumullaahu Khoiron, Baarakallahu Fiikum 🙏\n\n{' '.join(tags)}\n\n",
            embeds=embeds,
            view=ConfirmationButtons()
        )
    else:
        print("Send schedule failed")

def write_todays_pic():
    jadwal_hariini = jadwal.jadwal_rawatib[global_vars.system_day_name]

    for tempat in jadwal_hariini:
        for sholat in jadwal_hariini[tempat]:
            for tugas in jadwal_hariini[tempat][sholat]:
                # additional attributes
                petugas=jadwal_hariini[tempat][sholat][tugas]
                petugas['confirmed'] = False
                petugas['need_sub'] = False
                petugas['id_sub'] = 0

    save_presence(jadwal_hariini)