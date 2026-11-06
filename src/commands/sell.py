import discord
from config import bot
from server_config import GUILD_ID
from events.on_sale_notification import on_sale_noti
from views.sell_modal import RequestModal
from global_vars import global_vars

from database.presensi import get_all_my_unsold_schedule_today, get_all_my_unsold_schedule_thisweek, update_to_request_sub_by_ids, get_schedule_by_id
from database.discord_server import get_bot_config

@bot.tree.command(name="ganti", description="Meminta pengganti untuk jadwal yang Anda pilih di pekan ini", guild=GUILD_ID)
async def sellweek(interaction: discord.Interaction):
    await sellweekmodal(interaction)

async def sellmodal(interaction: discord.Interaction):
    schedules = await get_all_my_unsold_schedule_today(global_vars.system_date, interaction.guild_id, interaction.user.id)

    if schedules:
        await interaction.response.send_modal(RequestModal(schedules, is_sub=True, is_week=False))
    else:
        await sellweekmodal(interaction)

async def sellweekmodal(interaction: discord.Interaction):
    schedules = await get_all_my_unsold_schedule_thisweek(global_vars.system_date, interaction.guild_id, interaction.user.id)

    if schedules:
        await interaction.response.send_modal(RequestModal(schedules, is_sub=True, is_week=True))
    else:
        await interaction.response.send_message(content="Tidak ada jadwal yang bisa diminta pengganti pekan ini", ephemeral=True)

# failed to confirm on time
async def emergency_sell(id_server: int, id_presensi: int):
    bot_config = await get_bot_config(id_server)
    auto_sell_time = bot_config["auto_sell_time"]
    if auto_sell_time <= 0: return

    schedule = await get_schedule_by_id(id_presensi)
    confirmed = schedule["confirmed"]
    need_sub = schedule["need_sub"]
    swap_requested = schedule["swap_requested"]
    if confirmed or need_sub or swap_requested: return

    await on_sale_noti(id_server, schedule, "Gagal konfirmasi tepat waktu")
    await update_to_request_sub_by_ids([id_presensi])

# TODO: Figure out force commands