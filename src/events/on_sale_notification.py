import discord
from config import bot, mention_everyone, NAMA_HARI
from server_config import SUB_REQUESTS_CHANNEL
from global_vars import global_vars
from mission_util import to_datetime, to_indo_date_format
from repository.loader import jadwal
from repository.persistent_loader import persistent_vars, save_persistent
from views.claim_button import ClaimButton
from models.Schedule import Schedule

async def on_sale_noti(requested_schedule: Schedule, emergency=False, selected_members=[]):
    tanggal = requested_schedule.tanggal
    tugas = requested_schedule.tugas
    sholat = requested_schedule.sholat
    tempat = requested_schedule.tempat
    if tugas == 'Hadits': return

    target=bot.get_channel(SUB_REQUESTS_CHANNEL)

    jadwal_harian = jadwal.presensi_rawatib[tanggal]
    hari = NAMA_HARI[to_datetime(tanggal).weekday()]

    sold_jadwal = Schedule(tanggal, requested_schedule.tugas, sholat, tempat)

    id_anggota = sold_jadwal.get_pic_id()

    nama_petugas_sebelumnya = jadwal.anggota[id_anggota]['nama']
    alasan_harian = jadwal.alasan_absen.get(tanggal)
    alasan = alasan_harian.get(str(id_anggota))
    embed_desc=f"Hari: {hari}\nTanggal: {to_indo_date_format(tanggal)}\nTugas: {tugas}\nSholat: {sholat.capitalize()}\nTempat: {tempat.upper()}\nPetugas Sebelumnya: {nama_petugas_sebelumnya}\n\nAlasan:\n>>> {alasan}"

    embed=discord.Embed(
        title="Detail Jadwal", 
        color=discord.Color.red() if emergency else discord.Color.gold(),
        description=requested_schedule.get_reasoned_desc("Petugas Sebelumnya")
    )

    if emergency or len(selected_members) == 0:
        tags = "@everyone"
    else:
        mentions = []

        if tugas == "Imam":
            id_badal = jadwal_harian[tempat][sholat]['Badal']['id_anggota']
            uid_badal = jadwal.anggota[id_badal]['uid']
            if uid_badal != 0:
                mentions.append(f"Badal: <@{uid_badal}>\n")
            
        for member in selected_members:
            mentions.append(member.mention)

        tags = " ".join(mentions)

    if emergency:
        content=f"🚨 {tugas} Sholat {sholat.capitalize()} di {tempat.upper()} Perlu Pengganti!\n{tags}"
    else:
        if tanggal == global_vars.system_date:
            content=f"📢 {tugas} Sholat {sholat.capitalize()} di {tempat.upper()} Perlu Pengganti!\n{tags}"
        else:
            content=f"📢 ({hari}) {tugas} Sholat {sholat.capitalize()} di {tempat.upper()} Perlu Pengganti!\n{tags}"

    message = await target.send(content=content, embed=embed, view=ClaimButton(requested_schedule), allowed_mentions=mention_everyone)
    persistent_vars["notification_ids"][requested_schedule.get_key()] = message.id
    await save_persistent()