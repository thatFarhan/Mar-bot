import discord
from config import TEMPAT_TITLE, SHOLAT_TITLE, bot, DAILY_SCHEDULE_CHANNEL
from data.loader import jadwal
from data.persistent_loader import persistent_vars
from global_vars import global_vars

def build_schedule_and_tags(tempat: str):
    schedule=discord.Embed(
            title=TEMPAT_TITLE[tempat],
            color=discord.Color.green()
        )

    tags=set()
    for sholat in jadwal.jadwal_hariini[tempat]:
        field_values=[]
        for tugas in jadwal.jadwal_hariini[tempat][sholat]:
            id_anggota = jadwal.jadwal_hariini[tempat][sholat][tugas]['id_anggota']
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
            name=f"{SHOLAT_TITLE[sholat]} ({jadwal.jadwal_sholat_bulanini[global_vars.system_date][sholat]})",
            value="\n".join(field_values),
            inline=True
        )
    
    return [schedule, tags]

async def update_daily_schedule():
    if persistent_vars["current_daily_schedule_id"] == 0:
        return
    
    embeds=[]
    for tempat in jadwal.jadwal_hariini:
        schedule=build_schedule_and_tags(tempat)[0]
        embeds.append(schedule)

    daily_schedule_channel=bot.get_channel(DAILY_SCHEDULE_CHANNEL)
    message = await daily_schedule_channel.fetch_message(persistent_vars["current_daily_schedule_id"])

    await message.edit(embeds=embeds)