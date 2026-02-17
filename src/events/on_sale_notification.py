import discord
from config import SUB_REQUESTS_CHANNEL, bot, mention_everyone
from global_vars import global_vars
from data.loader import jadwal
from views.claim_button import ClaimButton

async def on_sale_noti(tugas, sholat, tempat, emergency=False):
    if tugas == 'Pembaca Hadits': return

    target=bot.get_channel(SUB_REQUESTS_CHANNEL)
    embed_desc=f"Hari: {global_vars.system_day_name}\nTugas: {tugas}\nSholat: {sholat.capitalize()}\nWaktu Sholat: {jadwal.jadwal_sholat_bulanini[global_vars.system_date][sholat]}\nTempat: {tempat.upper()}\nPetugas Default: {jadwal.jadwal_hariini[tempat][sholat][tugas]['nama']}"

    embed=discord.Embed(
        title="Detail Jadwal", 
        color=discord.Color.red() if emergency else discord.Color.gold(),
        description=embed_desc
    )

    tags = ""
    if tugas == "Muadzin" or emergency:
        tags = "@everyone"
    else:
        tags = f"Badal: <@{jadwal.jadwal_hariini[tempat][sholat]['Badal']['uid']}>"

    if emergency:
        content=f"## 🚨 PERHATIAN (PENGGANTI) 🚨\n**{tugas} Sholat {sholat.capitalize()} di {tempat.upper()} Perlu Pengganti!**\n{tags}"
    else:
        content=f"**📢 {tugas} Sholat {sholat.capitalize()} di {tempat.upper()} Perlu Pengganti! 📢**\n{tags}"

    message = await target.send(content=content, embed=embed, view=ClaimButton(tugas, sholat, tempat, embed_desc), allowed_mentions=mention_everyone)
    global_vars.notification_ids[f"{tugas}_{sholat}_{tempat}"] = message.id