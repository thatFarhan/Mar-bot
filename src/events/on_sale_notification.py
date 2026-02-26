import discord
from config import SUB_REQUESTS_CHANNEL, bot, mention_everyone
from global_vars import global_vars
from data.loader import jadwal
from data.persistent_loader import persistent_vars, save_persistent
from views.claim_button import ClaimButton

async def on_sale_noti(tugas, sholat, tempat, emergency=False):
    if tugas == 'Pembaca Hadits': return

    target=bot.get_channel(SUB_REQUESTS_CHANNEL)

    id_anggota = jadwal.jadwal_hariini[tempat][sholat][tugas]['id_anggota']
    nama_petugas_default = jadwal.anggota[id_anggota]['nama']
    waktu_sholat = jadwal.jadwal_sholat_bulanini[global_vars.system_day][sholat]
    embed_desc=f"Hari: {global_vars.system_day_name}\nTugas: {tugas}\nSholat: {sholat.capitalize()}\nWaktu Sholat: {waktu_sholat}\nTempat: {tempat.upper()}\nPetugas Default: {nama_petugas_default}"

    embed=discord.Embed(
        title="Detail Jadwal", 
        color=discord.Color.red() if emergency else discord.Color.gold(),
        description=embed_desc
    )

    tags = ""
    if tugas == "Muadzin" or emergency or "Badal" not in jadwal.jadwal_hariini[tempat][sholat]:
        tags = "@everyone"
    else:
        id_badal = jadwal.jadwal_hariini[tempat][sholat]['Badal']['id_anggota']
        uid_badal = jadwal.anggota[id_badal]['uid']
        tags = f"Badal: <@{uid_badal}>"

    if emergency:
        content=f"## 🚨 PERHATIAN (PENGGANTI) 🚨\n**{tugas} Sholat {sholat.capitalize()} di {tempat.upper()} Perlu Pengganti!**\n{tags}"
    else:
        content=f"**📢 {tugas} Sholat {sholat.capitalize()} di {tempat.upper()} Perlu Pengganti! 📢**\n{tags}"

    message = await target.send(content=content, embed=embed, view=ClaimButton(tugas, sholat, tempat, embed_desc), allowed_mentions=mention_everyone)
    persistent_vars["notification_ids"][f"{tugas}_{sholat}_{tempat}"] = message.id
    save_persistent()