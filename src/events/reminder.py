import discord
from datetime import datetime, timedelta
from data.loader import jadwal
from global_vars import global_vars, scheduler
from config import SHOLAT_TITLE, ACTUAL_TIMEZONE, TEMPAT_TITLE, bot, REMINDERS_CHANNEL, SUB_REQUESTS_CHANNEL
from views.quick_confirmation_buttons import QuickConfirmationButtons
from events.on_sale_notification import on_sale_noti
from commands.sell import emergency_sell

def set_reminders():
    for sholat in ('subuh', 'dzuhur', 'ashar', 'maghrib', 'isya'):
        date=jadwal.jadwal_sholat_bulanini[global_vars.system_date]['tanggal_lengkap'].split('-')
        time=jadwal.jadwal_sholat_bulanini[global_vars.system_date][sholat].split(':')

        year, month, day = int(date[0]), int(date[1]), int(date[2])
        hour, minute = int(time[0]), int(time[1])

        run_date=datetime(year=year, month=month, day=day, hour=hour, minute=minute) - timedelta(minutes=30)

        scheduler.add_job(func=send_reminder, args=[sholat], trigger='date', run_date=run_date, id=f"reminder_{sholat}", replace_existing=True, misfire_grace_time=60)
    
    for schedule in scheduler.get_jobs():
        print(schedule)

async def send_reminder(sholat: str):
    global_vars.reminder_sent[sholat] = True
    embed=discord.Embed(
        title=f"{SHOLAT_TITLE[sholat]} ({jadwal.jadwal_sholat_bulanini[global_vars.system_date][sholat]})",
        color=discord.Color.green()
    )

    tags_need_confirmation=set()

    tags=set()
    for tempat in jadwal.jadwal_hariini:
        if sholat not in jadwal.jadwal_hariini[tempat]:
            continue

        list_petugas=[]
        for tugas in jadwal.jadwal_hariini[tempat][sholat]:
            petugas = jadwal.jadwal_hariini[tempat][sholat][tugas]
            if petugas['id_sub'] != 0:
                anggota = jadwal.anggota[petugas['id_sub']]
                list_petugas.append(f"{tugas}: **{anggota['nama']}**")
            else:
                anggota = jadwal.anggota[petugas['id_anggota']]
                list_petugas.append(f"{tugas}: **{anggota['nama']}**")
                if not petugas['confirmed'] and not petugas['need_sub'] and anggota['uid'] != 0:
                    tags_need_confirmation.add(f"<@{anggota['uid']}>")

                    # auto sell after 10 minutes if there's no confirmation
                    run_date=datetime.now(ACTUAL_TIMEZONE) + timedelta(minutes=10)

                    scheduler.add_job(func=emergency_sell, args=[tugas, sholat, tempat], trigger='date', run_date=run_date, id=f"emergency_{tugas}_{sholat}_{tempat}", replace_existing=True, misfire_grace_time=60)
                elif petugas['need_sub']:
                    key = f"{tugas}_{sholat}_{tempat}"
                    if key in global_vars.notification_ids:
                        channel = bot.get_channel(SUB_REQUESTS_CHANNEL)
                        noti_id = global_vars.notification_ids[key]
                        message = await channel.fetch_message(noti_id)

                        await message.delete()
                    
                    await on_sale_noti(tugas, sholat, tempat, emergency=True)

            if anggota['uid'] != 0:
                tags.add(f"<@{anggota['uid']}>")

        embed.add_field(
            name=TEMPAT_TITLE[tempat],
            value="\n".join(list_petugas),
            inline=True
        )

    content=f"# ⏰ 30 Menit Menjelang Sholat {sholat.capitalize()} ⏰\nDiingatkan kembali kepada para petugas, harap untuk hadir sesuai dengan plotingannya masing-masing.\nJazaakumullaahu Khoiron, Baarakallahu Fiikum 🙏\n\n{' '.join(tags)}"

    reminders_channel=bot.get_channel(REMINDERS_CHANNEL)
    await reminders_channel.send(content=content, embed=embed)
    if tags_need_confirmation:
        unix_timestamp=int(run_date.timestamp())
        await reminders_channel.send(
            content=f"**⚠️ PERHATIAN (KONFIRMASI) ⚠️**\n\nNama di bawah ini belum melakukan konfirmasi. harap untuk melakukan konfirmasi <t:{unix_timestamp}:R>\n{' '.join(tags_need_confirmation)}",
            view=QuickConfirmationButtons(sholat)
        )

def reset_reminder_sent():
    for sholat in ('subuh', 'dzuhur', 'ashar', 'maghrib', 'isya'):
        global_vars.reminder_sent[sholat] = False