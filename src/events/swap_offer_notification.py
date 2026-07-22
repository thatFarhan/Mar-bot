import discord
from config import bot, mention_everyone, NAMA_HARI
from server_config import SUB_REQUESTS_CHANNEL
from mission_util import to_datetime
from repository.loader import jadwal
from repository.persistent_loader import persistent_vars, save_persistent
from models.Schedule import Schedule
from views.accept_offer_button import AcceptButton
from views.cancel_button import CancelButton

async def swap_offer_noti(interaction: discord.Interaction, requested_schedule: Schedule, offered_schedule: Schedule):
    if offered_schedule.tugas == 'Hadits' or offered_schedule.tugas == 'Badal': return

    requested_hari = NAMA_HARI[to_datetime(requested_schedule.tanggal).weekday()]
    offered_hari = NAMA_HARI[to_datetime(offered_schedule.tanggal).weekday()]

    embeds_peminta = []

    id_peminta = requested_schedule.get_pic_id()
    id_penawar = offered_schedule.get_pic_id()
        
    nama_peminta = jadwal.anggota[id_peminta]['nama']
    desc_peminta=f"Hari: {requested_hari}\nTugas: {requested_schedule.tugas}\nSholat: {requested_schedule.sholat.capitalize()}\nTempat: {requested_schedule.tempat.upper()}\nPetugas Sebelumnya: {nama_peminta}"

    nama_penawar = jadwal.anggota[id_penawar]['nama']
    desc_penawar=f"Hari: {offered_hari}\nTugas: {offered_schedule.tugas}\nSholat: {offered_schedule.sholat.capitalize()}\nTempat: {offered_schedule.tempat.upper()}\nPetugas Sebelumnya: {nama_penawar}"

    embed_permintaan1=discord.Embed(
        title="Jadwal yang Akan Diserahkan", 
        color=discord.Color.dark_gold(),
        description=desc_peminta
    )
    embeds_peminta.append(embed_permintaan1)

    embed_tawaran1=discord.Embed(
        title="Jadwal yang Akan Diterima", 
        color=discord.Color.gold(),
        description=desc_penawar
    )
    embeds_peminta.append(embed_tawaran1)

    content1=f"🔁 Ada Tawaran dari {nama_penawar}!"

    uid_peminta = jadwal.anggota[id_peminta]['uid']
    user_peminta = bot.get_user(uid_peminta)

    if user_peminta is None:
        user_peminta = await bot.fetch_user(uid_peminta)

    try:
        message = await user_peminta.send(content=content1, embeds=embeds_peminta, view=AcceptButton(requested_schedule, offered_schedule))

    except discord.Forbidden:
        target=bot.get_channel(SUB_REQUESTS_CHANNEL)
        content1=f"🔁 Ada Tawaran dari {nama_penawar}!\n<@{uid_peminta}>"
        message = await target.send(content=content1, embeds=embeds_peminta, view=AcceptButton(requested_schedule, offered_schedule), allowed_mentions=mention_everyone)
    
    store_noti_id = dict()

    store_noti_id["expiry_date"] = requested_schedule.tanggal if to_datetime(requested_schedule.tanggal) < to_datetime(offered_schedule.tanggal) else offered_schedule.tanggal
    
    store_noti_id["requestor_channel_id"] = message.channel.id
    store_noti_id["requestor_message_id"] = message.id

    embeds_penawar = []

    embed_tawaran2=discord.Embed(
        title="Jadwal yang Akan Diserahkan", 
        color=discord.Color.dark_gold(),
        description=desc_penawar
    )
    embeds_penawar.append(embed_tawaran2)

    embed_permintaan2=discord.Embed(
        title="Jadwal yang Akan Diterima", 
        color=discord.Color.gold(),
        description=desc_peminta
    )
    embeds_penawar.append(embed_permintaan2)

    content2=f"🔁 Berhasil Mengirim Tawaran ke {nama_peminta}!"

    uid_penawar = jadwal.anggota[id_penawar]['uid']
    user_penawar = bot.get_user(uid_penawar)

    if user_penawar is None:
        user_penawar = await bot.fetch_user(uid_penawar)

    try:
        message2 = await user_penawar.send(content=content2, view=CancelButton(requested_schedule, offered_schedule), embeds=embeds_penawar)
        await interaction.response.send_message("Berhasil menawarkan jadwal untuk ditukar", ephemeral=True)

        store_noti_id["offerer_channel_id"] = message2.channel.id
        store_noti_id["offerer_message_id"] = message2.id
    except discord.Forbidden:
        await interaction.response.send_message(content=content2, view=CancelButton(requested_schedule, offered_schedule), embeds=embeds_penawar, ephemeral=True)

    key = f"{requested_schedule.get_key()}_{offered_schedule.get_key()}"

    persistent_vars["swap_notification_ids"][key] = store_noti_id

    await save_persistent()