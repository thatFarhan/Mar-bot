from config import bot
from server_config import SUB_REQUESTS_CHANNEL
from repository.persistent_loader import persistent_vars, save_persistent
from repository.loader import global_vars
from models.Schedule import Schedule
from mission_util import to_datetime

async def purge_requestors(offered_schedule: Schedule, content: str):
    for key in dict(persistent_vars["swap_notification_ids"]):
        noti_detail = key.split("_")
        if len(noti_detail) < 5: continue

        noti_tanggal = noti_detail[4]
        noti_tugas = noti_detail[5]
        noti_sholat = noti_detail[6]
        noti_tempat = noti_detail[7]

        if f"{noti_tanggal}_{noti_tugas}_{noti_sholat}_{noti_tempat}" != offered_schedule.get_key(): continue

        requestor_channel_id = persistent_vars["swap_notification_ids"][key]["requestor_channel_id"]
        requestor_message_id = persistent_vars["swap_notification_ids"][key]["requestor_message_id"]
        dm_channel = bot.get_channel(requestor_channel_id)

        if dm_channel is None:
            dm_channel = await bot.fetch_channel(requestor_channel_id)

        try:
            dm_message = await dm_channel.fetch_message(requestor_message_id)
            await dm_message.edit(content=f"**{content}**", view=None)
        except Exception:
            # TODO: make the logic for this
            pass

        persistent_vars["swap_notification_ids"].pop(key, None)

async def purge_offerers(requested_schedule: Schedule, content: str):
    for key in dict(persistent_vars["swap_notification_ids"]):
        noti_detail = key.split("_")
        if len(noti_detail) < 5: continue

        noti_tanggal = noti_detail[0]
        noti_tugas = noti_detail[1]
        noti_sholat = noti_detail[2]
        noti_tempat = noti_detail[3]

        if f"{noti_tanggal}_{noti_tugas}_{noti_sholat}_{noti_tempat}" != requested_schedule.get_key(): continue

        requestor_channel_id = persistent_vars["swap_notification_ids"][key]["requestor_channel_id"]
        requestor_message_id = persistent_vars["swap_notification_ids"][key]["requestor_message_id"]
        offerer_channel_id = persistent_vars["swap_notification_ids"][key]["offerer_channel_id"]
        offerer_message_id = persistent_vars["swap_notification_ids"][key]["offerer_message_id"]
        requestor_dm_channel = bot.get_channel(requestor_channel_id)
        offerer_dm_channel = bot.get_channel(offerer_channel_id)

        if requestor_dm_channel is None:
            requestor_dm_channel = await bot.fetch_channel(requestor_channel_id)

        if offerer_dm_channel is None:
            offerer_dm_channel = await bot.fetch_channel(offerer_channel_id)

        try:
            dm_message = await requestor_dm_channel.fetch_message(requestor_message_id)
            await dm_message.edit(content=f"**{content}**", view=None)
        except Exception:
            # TODO: make the logic for this
            pass

        try:
            dm_message = await offerer_dm_channel.fetch_message(offerer_message_id)
            await dm_message.edit(content=f"**{content}**", view=None)
        except Exception:
            # TODO: make the logic for this
            pass

        persistent_vars["swap_notification_ids"].pop(key, None)

async def purge_expireds():
    for noti_key in list(persistent_vars["notification_ids"].keys()):
        noti_date = noti_key.split("_")[0]
        try:
            noti_datetime = to_datetime(noti_date)
            global_datetime = to_datetime(global_vars.system_date)

            if noti_datetime >= global_datetime: continue
            
            channel = bot.get_channel(SUB_REQUESTS_CHANNEL)
            noti_id = persistent_vars["notification_ids"][noti_key]
            try:
                message = await channel.fetch_message(noti_id)
                await message.edit(content="⌛ **Jadwal Kadaluarsa**", view=None)
            except Exception:
                pass
            persistent_vars["notification_ids"].pop(noti_key, None)
        except Exception:
            continue

    for noti_key in list(persistent_vars["swap_notification_ids"].keys()):
        noti_detail = noti_key.split("_")
        noti_date = persistent_vars["swap_notification_ids"][noti_key]["expiry_date"]

        try:
            noti_datetime = to_datetime(noti_date)
            global_datetime = to_datetime(global_vars.system_date)

            if noti_datetime >= global_datetime: continue

            if len(noti_detail) == 4:
                channel = bot.get_channel(SUB_REQUESTS_CHANNEL)
                noti_id = persistent_vars["swap_notification_ids"][noti_key]["message_id"]
                try:
                    message = await channel.fetch_message(noti_id)
                    await message.edit(content="⌛ **Jadwal Kadaluarsa**", view=None)
                except Exception:
                    pass
            else:
                requestor_channel_id = persistent_vars["swap_notification_ids"][noti_key]["requestor_channel_id"]
                requestor_message_id = persistent_vars["swap_notification_ids"][noti_key]["requestor_message_id"]
                offerer_channel_id = persistent_vars["swap_notification_ids"][noti_key]["offerer_channel_id"]
                offerer_message_id = persistent_vars["swap_notification_ids"][noti_key]["offerer_message_id"]
                requestor_dm_channel = bot.get_channel(requestor_channel_id)
                offerer_dm_channel = bot.get_channel(offerer_channel_id)

                if requestor_dm_channel is None:
                    requestor_dm_channel = await bot.fetch_channel(requestor_channel_id)

                if offerer_dm_channel is None:
                    offerer_dm_channel = await bot.fetch_channel(offerer_channel_id)

                try:
                    dm_message = await requestor_dm_channel.fetch_message(requestor_message_id)
                    await dm_message.edit(content=f"⌛ **Jadwal Kadaluarsa**", view=None)
                except Exception:
                    # TODO: make the logic for this
                    pass

                try:
                    dm_message = await offerer_dm_channel.fetch_message(offerer_message_id)
                    await dm_message.edit(content=f"⌛ **Jadwal Kadaluarsa**", view=None)
                except Exception:
                    # TODO: make the logic for this
                    pass

            persistent_vars["swap_notification_ids"].pop(noti_key, None)

        except Exception:
            continue