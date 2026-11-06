import discord
from config import bot, mention_everyone

from models.Schedule import Schedule
from views.accept_offer_button import AcceptButton
from views.cancel_button import CancelButton
from builders.swap_schedule_builder import build_swap_embeds
from global_vars import global_vars

from database.presensi import get_schedule_by_id
from database.discord_server import get_channel
from database.notifikasi import insert_swap_offer_noti

async def swap_offer_noti(interaction: discord.Interaction, requested_schedule: dict, offered_schedule_id: str):
    offered_schedule = await get_schedule_by_id(offered_schedule_id)

    requested_schedule_obj = Schedule(requested_schedule)
    offered_schedule_obj = Schedule(offered_schedule)

    offerer_embeds = build_swap_embeds(offered_schedule, requested_schedule)

    offerer_content=f"🔁 Berhasil Mengirim Tawaran ke {requested_schedule_obj.nama_petugas}!"

    uid_offerer = offered_schedule_obj.uid_petugas
    user_offerer = bot.get_user(uid_offerer)

    if user_offerer is None:
        user_offerer = await bot.fetch_user(uid_offerer)

    expiry_date = requested_schedule_obj.tanggal if requested_schedule_obj.tanggal < offered_schedule_obj.tanggal else offered_schedule_obj.tanggal

    try:
        offerer_message = await user_offerer.send(content=offerer_content, view=CancelButton(requested_schedule_obj, offered_schedule_obj), embeds=offerer_embeds)
        await interaction.response.send_message("Berhasil menawarkan jadwal untuk ditukar", ephemeral=True)
    except discord.Forbidden:
        offerer_message = await interaction.response.send_message(content=offerer_content, view=CancelButton(requested_schedule_obj, offered_schedule_obj), embeds=offerer_embeds, ephemeral=True)

    offerer_channel_id = offerer_message.channel.id
    offerer_message_id = offerer_message.id

    requestor_embeds = build_swap_embeds(requested_schedule, offered_schedule)

    requestor_content=f"🔁 Ada Tawaran dari {offered_schedule_obj.nama_petugas}!"

    uid_requestor = requested_schedule_obj.uid_petugas
    user_requestor = bot.get_user(uid_requestor)

    if user_requestor is None:
        user_requestor = await bot.fetch_user(uid_requestor)

    try:
        requestor_message = await user_requestor.send(content=requestor_content, embeds=requestor_embeds, view=AcceptButton(requested_schedule_obj, offered_schedule_obj, interaction.guild_id))

    except discord.Forbidden:
        sub_requests_channel_id = await get_channel("sub_requests_channel", interaction.guild_id)
        target=bot.get_channel(sub_requests_channel_id)
        requestor_content=f"🔁 Ada Tawaran dari {offered_schedule_obj.nama_petugas}!\n<@{uid_requestor}>"
        requestor_message = await target.send(content=requestor_content, embeds=requestor_embeds, view=AcceptButton(requested_schedule_obj, offered_schedule_obj, interaction.guild_id), allowed_mentions=mention_everyone)
        
    requestor_channel_id = requestor_message.channel.id
    requestor_message_id = requestor_message.id

    await insert_swap_offer_noti(
        sent_date=global_vars.system_date, 
        expiry_date=expiry_date, 
        requestor_message_id=requestor_message_id, 
        requestor_channel_id=requestor_channel_id, 
        offerer_message_id=offerer_message_id, 
        offerer_channel_id=offerer_channel_id, 
        id_requested_schedule=requested_schedule_obj.id_presensi, 
        id_offered_schedule=offered_schedule_id
    )