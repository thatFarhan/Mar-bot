import discord
from config import bot, mention_everyone, NAMA_HARI
from server_config import SUB_REQUESTS_CHANNEL
from global_vars import global_vars
from mission_util import to_datetime
from repository.loader import jadwal
from repository.persistent_loader import persistent_vars, save_persistent
from views.claim_button import ClaimButton
from models.Schedule import Schedule

async def on_sale_noti(requested_schedule: Schedule, emergency=False, selected_members=None):
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
    embed_desc=f"Hari: {hari}\nTugas: {tugas}\nSholat: {sholat.capitalize()}\nTempat: {tempat.upper()}\nPetugas Sebelumnya: {nama_petugas_sebelumnya}\n\nAlasan:\n>>> {alasan}"

    embed=discord.Embed(
        title="Detail Jadwal", 
        color=discord.Color.red() if emergency else discord.Color.gold(),
        description=embed_desc
    )

    if emergency:
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

        if len(mentions) == 0:
            tags = "@everyone"
        else:  
            tags = " ".join(mentions)

    if emergency:
        content=f"🚨 {tugas} Sholat {sholat.capitalize()} di {tempat.upper()} Perlu Pengganti!\n{tags}"
    else:
        if tanggal == global_vars.system_date:
            content=f"📢 {tugas} Sholat {sholat.capitalize()} di {tempat.upper()} Perlu Pengganti!\n{tags}"
        else:
            content=f"📢 ({hari}) {tugas} Sholat {sholat.capitalize()} di {tempat.upper()} Perlu Pengganti!\n{tags}"

    message = await target.send(content=content, embed=embed, view=ClaimButton(tanggal, tugas, sholat, tempat, embed_desc), allowed_mentions=mention_everyone)
    persistent_vars["notification_ids"][f"{tanggal}_{tugas}_{sholat}_{tempat}"] = message.id
    await save_persistent()