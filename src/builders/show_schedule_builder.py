import discord
from config import TEMPAT_TITLE, SHOLAT_TITLE
from repository.loader import jadwal

def build_schedule(tempat: str, system_day_name: str):
    schedule=discord.Embed(
            title=TEMPAT_TITLE[tempat],
            color=discord.Color.green()
        )

    for sholat in jadwal.jadwal_rawatib[system_day_name][tempat]:
        field_values=[]
        for tugas in jadwal.jadwal_rawatib[system_day_name][tempat][sholat]:
            id_anggota = jadwal.jadwal_rawatib[system_day_name][tempat][sholat][tugas]['id_anggota']
            anggota = jadwal.anggota[id_anggota]
            field_values.append(f"{tugas}: **{anggota['nama']}**")

        schedule.add_field(
            name=SHOLAT_TITLE[sholat],
            value="\n".join(field_values),
            inline=True
        )
    
    return schedule