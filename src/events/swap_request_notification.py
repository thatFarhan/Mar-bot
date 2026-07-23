import discord
from config import bot, mention_everyone, NAMA_HARI
from server_config import SUB_REQUESTS_CHANNEL
from global_vars import global_vars
from mission_util import to_datetime, to_indo_date_format
from repository.loader import jadwal
from repository.persistent_loader import persistent_vars, save_persistent
from views.swap_offer_button import OfferButton
from models.Schedule import Schedule

async def swap_request_noti(requested_schedule: Schedule, emergency=False, selected_members=[]):
    if requested_schedule.tugas == 'Hadits' or requested_schedule.tugas == 'Badal': return

    target=bot.get_channel(SUB_REQUESTS_CHANNEL)

    embed=discord.Embed(
        title="Detail Jadwal", 
        color=discord.Color.blue(),
        description=requested_schedule.get_reasoned_desc("Petugas Sebelumnya")
    )

    if emergency or len(selected_members) == 0:
        tags = "@everyone"
    else:
        mentions = []
        for member in selected_members:
            mentions.append(member.mention)

        tags = " ".join(mentions)

    content=f"🔁 Ada Permintaan Tukar Jadwal!\n{tags}"

    message = await target.send(content=content, embed=embed, view=OfferButton(requested_schedule), allowed_mentions=mention_everyone)

    store_noti_id = dict()
    store_noti_id["expiry_date"] = requested_schedule.tanggal
    store_noti_id["message_id"] = message.id

    persistent_vars["swap_notification_ids"][requested_schedule.get_key()] = store_noti_id
    await save_persistent()