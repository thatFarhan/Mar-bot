from config import bot
from datetime import date

# INSERT

async def insert_sub_request_noti(sent_date: date, expiry_date: date, requestor_message_id: int, requestor_channel_id: int, id_requested_schedule: int):
    async with bot.db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "INSERT INTO notifikasi (type, sent_date, expiry_date, requestor_message_id, requestor_channel_id, id_requested_schedule) VALUES (%s, %s, %s, %s, %s, %s)",
                ("sub_request", sent_date, expiry_date, requestor_message_id, requestor_channel_id, id_requested_schedule)
            )

async def insert_swap_request_noti(sent_date: date, expiry_date: date, requestor_message_id: int, requestor_channel_id: int, id_requested_schedule: int):
    async with bot.db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "INSERT INTO notifikasi (type, sent_date, expiry_date, requestor_message_id, requestor_channel_id, id_requested_schedule) VALUES (%s, %s, %s, %s, %s, %s)",
                ("swap_request", sent_date, expiry_date, requestor_message_id, requestor_channel_id, id_requested_schedule)
            )

async def insert_swap_offer_noti(sent_date: date, expiry_date: date, requestor_message_id: int, requestor_channel_id: int, offerer_message_id: int, offerer_channel_id: int, id_requested_schedule: int, id_offered_schedule: int):
    async with bot.db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "INSERT INTO notifikasi (type, sent_date, expiry_date, requestor_message_id, requestor_channel_id, offerer_message_id, offerer_channel_id, id_requested_schedule, id_offered_schedule) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                ("swap_offer", sent_date, expiry_date, requestor_message_id, requestor_channel_id, offerer_message_id, offerer_channel_id, id_requested_schedule, id_offered_schedule)
            )

# GET

async def get_sub_request_noti(id_presensi: int):
    async with bot.db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT id_notifikasi, requestor_message_id, requestor_channel_id 
                FROM notifikasi 
                WHERE type = 'sub_request' 
                AND id_requested_schedule = %s
                """,
                (id_presensi)
            )
            return await cur.fetchone()

async def get_swap_request_noti(id_presensi: int):
    async with bot.db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT id_notifikasi, requestor_message_id, requestor_channel_id 
                FROM notifikasi 
                WHERE type = 'swap_request' 
                AND id_requested_schedule = %s
                """,
                (id_presensi)
            )
            return await cur.fetchone()

async def get_swap_offer_noti(id_requested_schedule: int, id_offered_schedule: int):
    async with bot.db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT id_notifikasi, requestor_message_id, requestor_channel_id, offerer_message_id, offerer_channel_id
                FROM notifikasi 
                WHERE type = 'swap_offer' 
                AND id_requested_schedule = %s
                AND id_offered_schedule = %s
                """,
                (id_requested_schedule, id_offered_schedule)
            )
            return await cur.fetchone()

async def get_expired_notis(tanggal: date):
    async with bot.db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT id_notifikasi, requestor_message_id, requestor_channel_id, offerer_message_id, offerer_channel_id
                FROM notifikasi 
                WHERE expiry_date < %s
                """,
                (tanggal)
            )
            return await cur.fetchall()

async def get_related_notis(id_presensi: int):
    async with bot.db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT id_notifikasi, type, requestor_message_id, requestor_channel_id, offerer_message_id, offerer_channel_id, id_requested_schedule, id_offered_schedule
                FROM notifikasi
                WHERE id_requested_schedule = %s
                OR id_offered_schedule = %s
                """,
                (id_presensi, id_presensi)
            )
            return await cur.fetchall()

async def get_offers_from_request(id_requested_schedule: int):
    async with bot.db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT id_notifikasi, offerer_message_id, offerer_channel_id, requestor_message_id, requestor_channel_id
                FROM notifikasi
                WHERE type = 'swap_offer'
                AND id_requested_schedule = %s
                """,
                (id_requested_schedule)
            )
            return await cur.fetchall()

# UPDATE

async def update_request_message_id(id_notifikasi: int, message_id: int):
    async with bot.db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("UPDATE notifikasi SET requestor_message_id = %s WHERE id_notifikasi = %s", (message_id, id_notifikasi))
            return cur.rowcount


# DELETE

async def delete_noti_by_id(id_notifikasi: int):
    async with bot.db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("DELETE FROM notifikasi WHERE id_notifikasi = %s", (id_notifikasi))


async def delete_notis_by_ids(id_notifikasi: list):
    if not id_notifikasi: return 0

    placeholders = ",".join(["%s"] * len(id_notifikasi))
    async with bot.db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                f"DELETE FROM notifikasi WHERE id_notifikasi in ({placeholders})",
                tuple(id_notifikasi)
            )
            return cur.rowcount

async def delete_request_noti_by_message_id(message_id: int):
    async with bot.db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("DELETE FROM notifikasi WHERE requestor_message_id = %s", (message_id))


async def delete_related_notis(id_presensi: int):
    async with bot.db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("DELETE FROM notifikasi WHERE id_requested_schedule = %s OR id_offered_schedule = %s",
                              (id_presensi, id_presensi))

async def delete_expireds(tanggal: date):
    async with bot.db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("DELETE FROM notifikasi WHERE expiry_date < %s", (tanggal))