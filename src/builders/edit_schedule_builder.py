import discord
from config import TEMPAT_TITLE
from repository.loader import jadwal

def build_schedule(tempat: str, day_name: str, sholat_chosen: str, tempat_chosen: str):
    schedule=discord.Embed(
        title=TEMPAT_TITLE[tempat],
        color=discord.Color.blue() if tempat == tempat_chosen else discord.Color.ash_embed()
    )

    for sholat in jadwal.jadwal_rawatib[day_name][tempat]:
        cluster_chosen = sholat_chosen == sholat and tempat_chosen == tempat
        field_values=[]
        for tugas in jadwal.jadwal_rawatib[day_name][tempat][sholat]:
            id_anggota = jadwal.jadwal_rawatib[day_name][tempat][sholat][tugas]['id_anggota']
            anggota = jadwal.anggota[id_anggota]
            field_values.append(f"{tugas}: **{anggota['nama']}**" if cluster_chosen else f"{tugas}: {anggota['nama']}")

        schedule.add_field(
            name=f"➡️ *{sholat.capitalize()}*" if cluster_chosen else f"⬛ {sholat.capitalize()}",
            value="\n".join(field_values),
            inline=True
        )

    return schedule