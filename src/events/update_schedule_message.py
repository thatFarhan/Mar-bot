from config import bot, DAILY_SCHEDULE_CHANNEL
from data.loader import jadwal
from data.persistent_loader import persistent_vars
from builders.daily_schedule_builder import build_schedule_and_tags

async def update_daily_schedule():
    if persistent_vars["current_daily_schedule_id"] == 0:
        return
    
    embeds=[]
    for tempat in jadwal.jadwal_hariini:
        schedule_and_tags = build_schedule_and_tags(tempat)
        if schedule_and_tags:
            schedule = schedule_and_tags[0]
            embeds.append(schedule)

    daily_schedule_channel=bot.get_channel(DAILY_SCHEDULE_CHANNEL)
    message = await daily_schedule_channel.fetch_message(persistent_vars["current_daily_schedule_id"])

    await message.edit(embeds=embeds)