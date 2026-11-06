import discord
from datetime import datetime, timedelta
from repository.loader import jadwal
from global_vars import global_vars, scheduler
from config import SHOLAT_TITLE, ACTUAL_TIMEZONE, bot, SHOLAT_TUPLE, SHOLAT_NUMBER
from views.quick_confirmation_buttons import QuickConfirmationButtons
from events.update_schedule_message import update_daily_schedule
from events.resend_notification import resend_request_noti
from commands.sell import emergency_sell

from database.presensi import get_reminder
from database.masjid import get_enabled_masjids_from_server
from database.discord_server import get_channel, get_bot_config, update_reminders_sent

async def set_reminders(id_server: int):
    bot_config = await get_bot_config(id_server)
    reminder_send_time = bot_config["reminder_send_time"]
    auto_sell_time = bot_config["auto_sell_time"]
    for sholat in SHOLAT_TUPLE:
        date=jadwal.jadwal_sholat[global_vars.system_day]['tanggal_lengkap'].split('-')
        time=jadwal.jadwal_sholat[global_vars.system_day][sholat].split(':')

        year, month, day = int(date[0]), int(date[1]), int(date[2])
        hour, minute = int(time[0]), int(time[1])

        run_date=datetime(year=year, month=month, day=day, hour=hour, minute=minute) - timedelta(minutes=reminder_send_time)

        scheduler.add_job(func=send_reminder, args=[sholat, id_server, reminder_send_time, auto_sell_time], trigger='date', run_date=run_date, id=f"reminder_{sholat}_{id_server}", replace_existing=True, misfire_grace_time=60)
    
    for schedule in scheduler.get_jobs():
        print(schedule)

async def send_reminder(sholat: str, id_server: int, reminder_send_time: int = "Test", auto_sell_time: int = 0):
    if global_vars.system_day_name == "Jum'at" and sholat == "dzuhur":
        sholat_title = "jum'at"
    else:
        sholat_title = sholat

    embed=discord.Embed(
        title=f"{SHOLAT_TITLE[sholat_title]} ({jadwal.jadwal_sholat[global_vars.system_day][sholat]})"
    )

    embed.set_footer(text="* Indikator kehadiran tidak diperbarui secara langsung (real-time). Untuk pembaruan langsung, lihat jadwal harian.")

    tags_need_confirmation=set()
    tags=set()
    field_values = dict()

    reminder_sholat = await get_reminder(global_vars.system_date, sholat.capitalize(), id_server)

    masjids = await get_enabled_masjids_from_server(id_server)
    for masjid in masjids:
        field_values[masjid["nama_masjid"]] = []

    for schedule in reminder_sholat:
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
        
        if nama_reg == nama_pic and confirmed:
            emoji = "✅"
        elif nama_reg != nama_pic and confirmed:
            emoji = "☑️"
        elif need_sub:
            emoji = "⚠️"
        elif swap_requested:
            emoji = "🔁"
        else:
            emoji = "⬛"
        
        field_values[schedule["nama_masjid"]].append(f"{emoji} {tugas}: **{display_nama}**")
        
        if display_uid is not None and not need_sub and not swap_requested: 
            tags.add(f"<@{display_uid}>")

        if not confirmed and not need_sub and not swap_requested:
            tags_need_confirmation.add(f"<@{display_uid}>")

            if auto_sell_time > 0:
                run_date=datetime.now(ACTUAL_TIMEZONE) + timedelta(minutes=auto_sell_time)
            
                scheduler.add_job(
                    func=emergency_sell, 
                    args=[id_server, id_presensi], 
                    trigger='date', 
                    run_date=run_date, 
                    id=f"emergency_{id_presensi}", 
                    replace_existing=True,
                    misfire_grace_time=60
                )

        if need_sub:
            await resend_request_noti(id_presensi, id_server, is_sub=True)

        if swap_requested:
            await resend_request_noti(id_presensi, id_server, is_sub=False)

    for masjid in field_values:
        if field_values[masjid]:
            embed.add_field(
                name=f"🕌 {masjid}",
                value="\n".join(field_values[masjid]),
                inline=True
            )

    reminder_content=f"⏰ {reminder_send_time} Menit Menjelang Sholat {sholat_title.capitalize()}\n\n{' '.join(tags)}"

    reminders_channel_id = await get_channel("reminders_channel", id_server)
    reminders_channel = bot.get_channel(reminders_channel_id)
    await reminders_channel.send(content=reminder_content, embed=embed, view=QuickConfirmationButtons(sholat))
    
    if tags_need_confirmation:
        need_confirmation_content = f"⚠️ Nama di bawah ini belum melakukan konfirmasi.\n{' '.join(tags_need_confirmation)}"

        if auto_sell_time > 0:
            scheduler.add_job(
                func=update_daily_schedule, 
                args=[id_server], 
                trigger='date', 
                run_date=run_date + timedelta(seconds=5), 
                id=f"refresh_schedule_{id_server}", 
                replace_existing=True,
                misfire_grace_time=60
            )

            unix_timestamp=int(run_date.timestamp())
            need_confirmation_content += f"\n\nHarap untuk melakukan konfirmasi <t:{unix_timestamp}:R>"

        await reminders_channel.send(
            content=need_confirmation_content
        )

    await update_reminders_sent(id_server, SHOLAT_NUMBER[sholat])