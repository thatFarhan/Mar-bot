import discord
import json
from data.loader import jadwal
from config import TEMPAT_TITLE, SHOLAT_TITLE
from views.confirmation_buttons import ConfirmationButtons
from global_vars import global_vars

def build_schedule_and_tags(tempat: str, system_day_name: str):
    jadwal=discord.Embed(
            title=TEMPAT_TITLE[tempat],
            color=discord.Color.green()
        )

    tags=set()
    for sholat in jadwal.jadwal_petugas[f'{system_day_name}'][tempat]:
        field_values=[]
        for tugas in jadwal.jadwal_petugas[f'{system_day_name}'][tempat][sholat]:
            field_values.append(f"**{tugas}:** {jadwal.jadwal_petugas[system_day_name][tempat][sholat][tugas]['nama']}")
            tags.add(f"<@{jadwal.jadwal_petugas[system_day_name][tempat][sholat][tugas]['uid']}>")

        jadwal.add_field(
            name=f"{SHOLAT_TITLE[sholat]} ({jadwal.jadwal_sholat_bulanini[global_vars.system_date][sholat]})",
            value="\n".join(field_values),
            inline=True
        )
    
    return [jadwal, tags]

async def send_daily_schedule(target):
    if target:
        system_day_name=jadwal.jadwal_sholat_bulanini[global_vars.system_date]['hari']

        embeds=[]
        tags=set()
        for tempat in jadwal.jadwal_petugas[system_day_name]:
            schedule_and_tags=build_schedule_and_tags(tempat, system_day_name)
            embeds.append(schedule_and_tags[0])
            for tag in schedule_and_tags[1]:
                tags.add(tag)

        await target.send(
            content=f"# 💫 Jadwal hari {system_day_name}\n## 🌃 Lailatukumus Sa'idah Ikhwan~\nBerikut adalah jadwal petugas untuk esok hari. Mohon untuk konfirmasi kehadiran jika bisa berhadir atau request pengganti jika tidak.\nJazaakumullaahu Khoiron, Baarakallahu Fiikum 🙏\n\n{' '.join(tags)}\n\n",
            embeds=embeds,
            view=ConfirmationButtons()
        )
    else:
        print("Send schedule failed")

def write_todays_pic():
    petugas_hariini = jadwal.jadwal_petugas[global_vars.system_day_name]

    for tempat in petugas_hariini:
        for sholat in petugas_hariini[tempat]:
            for tugas in petugas_hariini[tempat][sholat]:
                # additional attributes
                petugas=petugas_hariini[tempat][sholat][tugas]
                petugas['confirmed'] = False
                petugas['need_sub'] = False
                petugas['nama_sub'] = None
                petugas['uid_sub'] = None

    with open('jadwal_hariini.json', 'w') as file:
        json.dump(jadwal.jadwal_petugas[global_vars.system_day_name], file, indent=2)
        print(f"Jadwal hari {global_vars.system_day_name} telah dibuat menjadi json derulo")

    with open('jadwal_hariini.json') as file:
        jadwal.jadwal_hariini=json.load(file)