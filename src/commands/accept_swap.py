import discord
from config import NAMA_HARI, bot
from server_config import SUB_REQUESTS_CHANNEL
from mission_util import to_datetime, to_indo_date_format
from repository.updater import update_to_claim
from repository.loader import jadwal, save_presence
from repository.persistent_loader import persistent_vars, save_persistent
from events.update_schedule_message import update_daily_schedule
from models.Schedule import Schedule
from events.purge_transaction import purge_offerers, purge_requestors

async def accept(interaction: discord.Interaction, requested_schedule: Schedule, offered_schedule: Schedule):
    id_penawar = offered_schedule.get_pic_id()
    id_peminta = requested_schedule.get_pic_id()
    uid_peminta = jadwal.anggota[id_peminta]['uid']
    if interaction.user.id != uid_peminta:
        await interaction.response.send_message("Lau sape mpruy? 🫵😂", ephemeral=True)
        return
    
    update_to_claim(requested_schedule, id_penawar)
    update_to_claim(offered_schedule, id_peminta)

    await save_presence()

    embeds = []

    embed_permintaan=discord.Embed(
        title="Jadwal yang Akan Diserahkan", 
        color=discord.Color.green(),
        description=requested_schedule.get_unreasoned_desc("Petugas Sebelumnya:")
    )
    embeds.append(embed_permintaan)

    embed_tawaran=discord.Embed(
        title="Jadwal yang Akan Diterima", 
        color=discord.Color.green(),
        description=offered_schedule.get_unreasoned_desc("Petugas Sebelumnya:")
    )
    embeds.append(embed_tawaran)

    content=f"**✅ Tawaran Diterima**"

    await interaction.response.edit_message(content=content, embeds=embeds, view=None)
    await update_daily_schedule()

    embed_accepted_swap = discord.Embed(
        title="Detail Penukaran Jadwal",
        color=discord.Color.green()
    )

    nama_penawar = jadwal.anggota[id_penawar]['nama']
    embed_accepted_swap.add_field(
        name="Jadwal A",
        value=requested_schedule.get_unreasoned_desc("Petugas Pengganti", nama_penawar),
        inline=False
    )

    embed_accepted_swap.add_field(
        name="🔃",
        value="",
        inline=False
    )

    nama_peminta = jadwal.anggota[id_peminta]['nama']
    embed_accepted_swap.add_field(
        name="Jadwal B",
        value=offered_schedule.get_unreasoned_desc("Petugas Pengganti", nama_peminta),
        inline=False
    )

    request_key = f"{requested_schedule.get_key()}"
    request_message_id = persistent_vars["swap_notification_ids"][request_key]["message_id"]
    channel = bot.get_channel(SUB_REQUESTS_CHANNEL)
    request_message = await channel.fetch_message(request_message_id)
    await request_message.edit(content="**✅ Jadwal Telah Ditukar**", embed=embed_accepted_swap, view=None)

    offer_key = f"{requested_schedule.get_key()}_{offered_schedule.get_key()}"
    offerer_channel_id = persistent_vars["swap_notification_ids"][offer_key]["offerer_channel_id"]
    offerer_message_id = persistent_vars["swap_notification_ids"][offer_key]["offerer_message_id"]
    dm_channel = bot.get_channel(offerer_channel_id)

    try:
        await dm_channel.send(content="✅ Tawaran Antum Diterima!", embed=embed_accepted_swap)
    except Exception:
        # TODO: make the logic for this
        pass

    if dm_channel is None:
        dm_channel = await bot.fetch_channel(offerer_channel_id)

    dm_message = await dm_channel.fetch_message(offerer_message_id)
    await dm_message.delete()

    persistent_vars["swap_notification_ids"].pop(f"{requested_schedule.get_key()}_{offered_schedule.get_key()}", None)
    await purge_requestors(offered_schedule, "🤷 Jadwal yang Ditawarkan Telah Diambil Oleh Anggota Lain")
    await purge_offerers(requested_schedule, "🤷 Tawaran yang Lain Telah Diterima")
    await save_persistent()