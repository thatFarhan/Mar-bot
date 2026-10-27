from config import bot
from datetime import date

# INSERT

async def insert_sale_noti(expiry_date: date, id_requestor: int, requestor_message_id: int, requestor_channel_id: int, id_requested_schedule: int):
    async with bot.db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "INSERT INTO notifikasi (type, expiry_date, id_requestor, requestor_message_id, requestor_channel_id, id_requested_schedule) VALUES (%s, %s, %s, %s, %s, %s)",
                ("on_sale", expiry_date, id_requestor, requestor_message_id, requestor_channel_id, id_requested_schedule)
            )

async def insert_swap_request_noti(expiry_date: date, id_requestor: int, requestor_message_id: int, requestor_channel_id: int, id_requested_schedule: int):
    async with bot.db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "INSERT INTO notifikasi (type, expiry_date, id_requestor, requestor_message_id, requestor_channel_id, id_requested_schedule) VALUES (%s, %s, %s, %s, %s, %s)",
                ("swap_request", expiry_date, id_requestor, requestor_message_id, requestor_channel_id, id_requested_schedule)
            )

async def insert_swap_offer_noti(expiry_date: date, requestor_message_id: int, requestor_channel_id: int, offerer_message_id: int, offerer_channel_id: int, id_requested_schedule: int, id_offered_schedule: int):
    async with bot.db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "INSERT INTO notifikasi (type, expiry_date, requestor_message_id, requestor_channel_id, offerer_message_id, offerer_channel_id, id_requested_schedule, id_offered_schedule) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                ("swap_offer", expiry_date, requestor_message_id, requestor_channel_id, offerer_message_id, offerer_channel_id, id_requested_schedule, id_offered_schedule)
            )