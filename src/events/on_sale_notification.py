import discord
from config import bot, mention_everyone, SHOLAT_NUMBER
from global_vars import global_vars
from views.claim_button import ClaimButton
from views.swap_offer_button import OfferButton
from models.Schedule import Schedule

from database.discord_server import get_channel, get_reminders_sent
from database.notifikasi import insert_sub_request_noti, update_request_message_id, insert_swap_request_noti
from database.alasan_absen import get_alasan_absen

async def on_sale_noti(guild_id: int, schedule: dict, alasan: str = None, selected_members=[], prev_id_notifikasi: int = None, is_sub: bool = True):
    sub_request_channel = await get_channel("sub_requests_channel", guild_id)
    target = bot.get_channel(sub_request_channel)

    schedule_obj = Schedule(schedule)

    if alasan is None:
        row_alasan = await get_alasan_absen(schedule_obj.id_presensi, schedule_obj.id_petugas)
        if row_alasan: alasan = row_alasan["alasan"]

    embed=discord.Embed(
        title="Detail Jadwal",
        description=schedule_obj.get_desc(alasan)
    )

    reminders_sent = await get_reminders_sent(guild_id)
    sholat_reminder_sent = reminders_sent >= SHOLAT_NUMBER[schedule_obj.sholat.lower()]
    if len(selected_members) == 0 or sholat_reminder_sent:
        tags = "@everyone"
    else:
        mentions = []
            
        for member in selected_members:
            mentions.append(member.mention)

        tags = " ".join(mentions)

    if is_sub:
        if sholat_reminder_sent:
            content=f"🚨 {schedule_obj.tugas} Sholat {schedule_obj.sholat} di {schedule_obj.nama_masjid} Perlu Pengganti!\n{tags}"
        elif schedule_obj.tanggal == global_vars.system_date:
            content=f"📢 {schedule_obj.tugas} Sholat {schedule_obj.sholat} di {schedule_obj.nama_masjid} Perlu Pengganti!\n{tags}"
        else:
            content=f"📢 ({schedule_obj.hari}) {schedule_obj.tugas} Sholat {schedule_obj.sholat} di {schedule_obj.nama_masjid} Perlu Pengganti!\n{tags}"

        message = await target.send(content=content, embed=embed, view=ClaimButton(schedule_obj.id_presensi), allowed_mentions=mention_everyone)
        if prev_id_notifikasi is None:
            await insert_sub_request_noti(global_vars.system_date, schedule_obj.tanggal, message.id, sub_request_channel, schedule_obj.id_presensi)
        else:
            await update_request_message_id(prev_id_notifikasi, message.id)
    else:
        content=f"🔁 Ada Permintaan Tukar Jadwal!\n{tags}"
        message = await target.send(content=content, embed=embed, view=OfferButton(schedule_obj.id_presensi), allowed_mentions=mention_everyone)
        if prev_id_notifikasi is None:
            await insert_swap_request_noti(global_vars.system_date, schedule_obj.tanggal, message.id, sub_request_channel, schedule_obj.id_presensi)
        else:
            await update_request_message_id(prev_id_notifikasi, message.id)