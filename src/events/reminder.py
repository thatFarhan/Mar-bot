import discord
from datetime import datetime, timedelta
from repository.loader import jadwal
from repository.persistent_loader import persistent_vars, save_persistent
from global_vars import global_vars, scheduler
from config import SHOLAT_TITLE, ACTUAL_TIMEZONE, TEMPAT_TITLE, bot, SHOLAT_TUPLE
from server_config import REMINDERS_CHANNEL, SUB_REQUESTS_CHANNEL
from views.quick_confirmation_buttons import QuickConfirmationButtons
from events.on_sale_notification import on_sale_noti
from commands.sell import emergency_sell

def set_reminders():
    for sholat in SHOLAT_TUPLE:
        date=jadwal.jadwal_sholat[global_vars.system_day]['tanggal_lengkap'].split('-')
        time=jadwal.jadwal_sholat[global_vars.system_day][sholat].split(':')

        year, month, day = int(date[0]), int(date[1]), int(date[2])
        hour, minute = int(time[0]), int(time[1])

        run_date=datetime(year=year, month=month, day=day, hour=hour, minute=minute) - timedelta(minutes=30)

        scheduler.add_job(func=send_reminder, args=[sholat], trigger='date', run_date=run_date, id=f"reminder_{sholat}", replace_existing=True, misfire_grace_time=60)
    
    for schedule in scheduler.get_jobs():
        print(schedule)

async def send_reminder(sholat: str):
    persistent_vars["reminder_sent"][sholat] = True
    await save_persistent()

    if global_vars.system_day_name == "Jum'at" and sholat == "dzuhur":
        sholat_title = "jum'at"
    else:
        sholat_title = sholat

    embed=discord.Embed(
        title=f"{SHOLAT_TITLE[sholat_title]} ({jadwal.jadwal_sholat[global_vars.system_day][sholat]})",
        color=discord.Color.green()
    )

    embed.set_footer(text="* Indikator kehadiran tidak diperbarui secara langsung (real-time). Untuk pembaruan langsung, lihat jadwal harian.")

    tags_need_confirmation=set()

    tags=set()
    jadwal_harian = jadwal.presensi_rawatib[global_vars.system_date]
    for tempat in jadwal_harian:
        if sholat not in jadwal_harian[tempat]: continue

        list_petugas=[]
        for tugas in jadwal_harian[tempat][sholat]:
            petugas = jadwal_harian[tempat][sholat][tugas]

            if petugas["id_anggota"] == 0 and petugas["id_sub"] == 0: continue

            confirmed = jadwal_harian[tempat][sholat][tugas]['confirmed']
            need_sub = jadwal_harian[tempat][sholat][tugas]['need_sub']
            id_sub = jadwal_harian[tempat][sholat][tugas]['id_sub']

            id_anggota = jadwal_harian[tempat][sholat][tugas]['id_anggota']
            anggota = jadwal.anggota[id_anggota]
            emoji = "⬛"

            if confirmed and id_sub == 0:
                emoji = "✅"
            if id_sub != 0:
                anggota = jadwal.anggota[id_sub]
                if confirmed:
                    emoji = "☑️"
            if need_sub:
                emoji = "⚠️"

            if not confirmed and not need_sub and anggota['uid'] != 0:
                tags_need_confirmation.add(f"<@{anggota['uid']}>")

                # auto sell after 10 minutes if there's no confirmation
                run_date=datetime.now(ACTUAL_TIMEZONE) + timedelta(minutes=10)

                if tugas != "Hadits" and tugas != "Badal`":
                    scheduler.add_job(func=emergency_sell, args=[tugas, sholat, tempat], trigger='date', run_date=run_date, id=f"emergency_{tugas}_{sholat}_{tempat}", replace_existing=True, misfire_grace_time=60)
                    
            elif petugas['need_sub']:
                key = f"{global_vars.system_date}_{tugas}_{sholat}_{tempat}"
                if key in persistent_vars["notification_ids"]:
                    channel = bot.get_channel(SUB_REQUESTS_CHANNEL)
                    noti_id = persistent_vars["notification_ids"][key]
                    message = await channel.fetch_message(noti_id)

                    await message.delete()
                
                await on_sale_noti(tugas, sholat, tempat, emergency=True)

            list_petugas.append(f"{emoji} {tugas}: **{anggota['nama']}**")

            if anggota['uid'] != 0:
                tags.add(f"<@{anggota['uid']}>")

        if list_petugas:
            embed.add_field(
                name=TEMPAT_TITLE[tempat],
                value="\n".join(list_petugas),
                inline=True
            )

    content=f"⏰ 30 Menit Menjelang Sholat {sholat_title.capitalize()}\n\n{' '.join(tags)}"

    reminders_channel=bot.get_channel(REMINDERS_CHANNEL)
    await reminders_channel.send(content=content, embed=embed)
    if tags_need_confirmation:
        unix_timestamp=int(run_date.timestamp())
        await reminders_channel.send(
            content=f"⚠️ Nama di bawah ini belum melakukan konfirmasi.\n\nHarap untuk melakukan konfirmasi <t:{unix_timestamp}:R>\n{' '.join(tags_need_confirmation)}",
            view=QuickConfirmationButtons(sholat)
        )

async def reset_reminder_sent():
    for sholat in SHOLAT_TUPLE:
        persistent_vars["reminder_sent"][sholat] = False

    await save_persistent()