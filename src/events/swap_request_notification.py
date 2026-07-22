import discord
from config import bot, mention_everyone, NAMA_HARI
from server_config import SUB_REQUESTS_CHANNEL
from global_vars import global_vars
from mission_util import to_datetime
from repository.loader import jadwal
from repository.persistent_loader import persistent_vars, save_persistent
from views.swap_offer_button import OfferButton
from models.Schedule import Schedule

async def swap_request_noti(requested_schedule: Schedule, emergency=False, selected_members=None):
    if requested_schedule.tugas == 'Hadits' or requested_schedule.tugas == 'Badal': return

    target=bot.get_channel(SUB_REQUESTS_CHANNEL)

    hari = NAMA_HARI[to_datetime(requested_schedule.tanggal).weekday()]

    id_anggota = requested_schedule.get_pic_id()
        
    nama_petugas_sebelumnya = jadwal.anggota[id_anggota]['nama']
    alasan_harian = jadwal.alasan_absen.get(requested_schedule.tanggal)
    alasan = alasan_harian.get(str(id_anggota))
    embed_desc=f"Hari: {hari}\nTugas: {requested_schedule.tugas}\nSholat: {requested_schedule.sholat.capitalize()}\nTempat: {requested_schedule.tempat.upper()}\nPetugas Sebelumnya: {nama_petugas_sebelumnya}\n\nAlasan:\n>>> {alasan}"

    embed=discord.Embed(
        title="Detail Jadwal", 
        color=discord.Color.blue(),
        description=embed_desc
    )

    if emergency:
        tags = "@everyone"
    else:
        mentions = []
        for member in selected_members:
            mentions.append(member.mention)

        if len(mentions) == 0:
            tags = "@everyone"
        else:
            tags = " ".join(mentions)

    content=f"🔁 Ada Permintaan Tukar Jadwal!\n{tags}"

    message = await target.send(content=content, embed=embed, view=OfferButton(requested_schedule), allowed_mentions=mention_everyone)

    store_noti_id = dict()
    store_noti_id["expiry_date"] = requested_schedule.tanggal
    store_noti_id["message_id"] = message.id

    persistent_vars["swap_notification_ids"][requested_schedule.get_key()] = store_noti_id
    await save_persistent()