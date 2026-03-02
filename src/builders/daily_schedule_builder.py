import discord
from config import TEMPAT_TITLE, SHOLAT_TITLE, SHOLAT_TUPLE
from data.loader import jadwal
from global_vars import global_vars

def build_schedule_and_tags(tempat: str):
    schedule=discord.Embed(
            title=TEMPAT_TITLE[tempat],
            color=discord.Color.green()
        )

    tags=set()
    for sholat in SHOLAT_TUPLE:
        if sholat not in jadwal.jadwal_hariini[tempat]:
            continue

        if global_vars.system_day_name == "Jum'at" and sholat == "dzuhur":
            sholat_title = "jum'at"
        else:
            sholat_title = sholat

        field_values=[]
        for tugas in jadwal.jadwal_hariini[tempat][sholat]:
            id_anggota = jadwal.jadwal_hariini[tempat][sholat][tugas]['id_anggota']

            if id_anggota == 0:
                continue

            confirmed = jadwal.jadwal_hariini[tempat][sholat][tugas]['confirmed']
            need_sub = jadwal.jadwal_hariini[tempat][sholat][tugas]['need_sub']
            id_sub = jadwal.jadwal_hariini[tempat][sholat][tugas]['id_sub']

            anggota = jadwal.anggota[id_anggota]
            emoji = "⬛"

            if confirmed and id_sub == 0:
                emoji = "✅"
            if confirmed and id_sub != 0:
                emoji = "🔁"
                anggota = jadwal.anggota[id_sub]
            if need_sub:
                emoji = "⚠️"

            field_values.append(f"{emoji} {tugas}: **{anggota['nama']}**")
            if anggota['uid'] != 0:
                tags.add(f"<@{anggota['uid']}>")

        schedule.add_field(
            name=f"{SHOLAT_TITLE[sholat_title]} ({jadwal.jadwal_sholat[global_vars.system_day][sholat]})",
            value="\n".join(field_values),
            inline=True
        )
    
    return [schedule, tags]