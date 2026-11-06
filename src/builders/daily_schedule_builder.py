import discord
from config import SHOLAT_TITLE, SHOLAT_TUPLE
from repository.loader import jadwal
from global_vars import global_vars

def build_schedule_and_tags(jadwal_harian: list):
    schedule_message=discord.Embed(
        title="🕌 " + jadwal_harian[0]["nama_masjid"]
    )

    tags=set()
    need_subs=[]
    swap_requesteds=[]

    field_values = dict()

    for sholat in SHOLAT_TUPLE:
        field_values[sholat.capitalize()] = []

    for schedule in jadwal_harian:
        nama_reg = schedule["nama_reg"]
        if nama_reg is None: continue

        id_presensi = schedule["id_presensi"]
        tugas = schedule["tugas"]
        confirmed = schedule["confirmed"]
        need_sub = schedule["need_sub"]
        swap_requested = schedule["swap_requested"]
        nama_pic = schedule["nama_pic"]
        uid_reg = schedule["uid_reg"]
        uid_pic = schedule["uid_pic"]

        display_nama = nama_pic if nama_pic is not None else nama_reg
        display_uid = uid_pic if uid_pic is not None else uid_reg

        emoji = "⬛"

        if nama_reg == nama_pic and confirmed:
            emoji = "✅"
        if nama_reg != nama_pic and confirmed:
            emoji = "☑️"
        if swap_requested:
            emoji = "🔁"
            swap_requesteds.append(id_presensi)
        if need_sub:
            emoji = "⚠️"
            need_subs.append(id_presensi)
        
        field_values[schedule["sholat"]].append(f"{emoji} {tugas}: **{display_nama}**")

        if display_uid is not None: tags.add(f"<@{display_uid}>")

    for sholat in SHOLAT_TUPLE:
        if global_vars.system_day_name == "Jum'at" and sholat == "dzuhur":
            sholat_title = "jum'at"
        else:
            sholat_title = sholat
        if field_values[sholat.capitalize()]:
            schedule_message.add_field(
                name=f"{SHOLAT_TITLE[sholat_title]} ({jadwal.jadwal_sholat[global_vars.system_day][sholat]})",
                value="\n".join(field_values[sholat.capitalize()]),
                inline=True
            )
    
    if schedule_message.fields:
        return {
            "embed": schedule_message,
            "tags": tags,
            "need_subs": need_subs,
            "swap_requesteds": swap_requesteds
        }
    else:
        return None