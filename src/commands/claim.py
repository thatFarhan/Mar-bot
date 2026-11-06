import discord
from global_vars import global_vars
from events.update_schedule_message import update_daily_schedule
from events.purge_transaction import purge_related_notifications

from database.anggota import get_anggota_by_guild_and_uid
from database.presensi import update_to_claim_by_id, get_schedule_by_id, update_to_confirm_by_ids
from database.notifikasi import delete_request_noti_by_message_id

# TODO: Figure out force commands

async def claim(interaction: discord.Interaction, id_presensi: int):
    id_anggota = await get_anggota_by_guild_and_uid(interaction.guild_id, interaction.user.id)

    if not id_anggota:
        await interaction.response.send_message("Akun Anda belum teregistrasi sebagai akun anggota", ephemeral=True)
        return

    schedule = await get_schedule_by_id(id_presensi)

    if schedule["id_reg"] == id_anggota or schedule["id_pic"] == id_anggota:
        await update_to_confirm_by_ids([id_presensi])
    else:
        is_today = schedule["tanggal"] == global_vars.system_date
        await update_to_claim_by_id(id_presensi, id_anggota, is_today)

    content=f"**✅ Jadwal Telah Diklaim oleh <@{interaction.user.id}>**"
    await interaction.response.edit_message(content=content, view=None)

    await delete_request_noti_by_message_id(interaction.message.id)
    await purge_related_notifications(id_presensi)
    
    await update_daily_schedule(interaction.guild_id)