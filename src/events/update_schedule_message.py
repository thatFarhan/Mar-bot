from config import bot
from builders.daily_schedule_builder import build_schedule_and_tags
from global_vars import global_vars

from database.discord_server import get_daily_schedule_message_id, get_channel
from database.masjid import get_enabled_masjids_from_server
from database.presensi import get_daily_schedule_for_masjid

async def update_daily_schedule(id_server: int):
    embeds=[]
    masjids = await get_enabled_masjids_from_server(id_server)
    for masjid in masjids:
        jadwal_harian = await get_daily_schedule_for_masjid(global_vars.system_date, masjid["id_masjid"])
        schedule_and_tags = build_schedule_and_tags(jadwal_harian)
    
        if not schedule_and_tags:
            continue
    
        embeds.append(schedule_and_tags["embed"])

    daily_schedule_channel=bot.get_channel(await get_channel("daily_schedule_channel", id_server))
    message = await daily_schedule_channel.fetch_message(await get_daily_schedule_message_id(id_server))

    await message.edit(embeds=embeds)

async def remove_buttons_from_daily_schedule(schedule_channel_id: int, schedule_message_id: int):
    daily_schedule_channel=bot.get_channel(schedule_channel_id)
    try:
        message = await daily_schedule_channel.fetch_message(schedule_message_id)
    except Exception:
        return

    await message.edit(view=None)