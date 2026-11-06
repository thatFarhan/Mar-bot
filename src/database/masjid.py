from config import bot

# INSERT

async def insert_masjid(nama_masjid: str, is_weekly: bool, masjid_enabled: bool, id_server: int):
    async with bot.db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "INSERT INTO masjid (nama_masjid, is_weekly, masjid_enabled, id_server) VALUES (%s, %s, %s, %s)",
                (nama_masjid, is_weekly, masjid_enabled, id_server)
            )

# GET

async def get_all_id_masjid_and_is_weekly():
    async with bot.db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT id_masjid, is_weekly FROM masjid WHERE masjid_enabled")
            return await cur.fetchall()

async def get_enabled_masjids_from_server(id_server: int):
    async with bot.db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT id_masjid, nama_masjid FROM masjid WHERE id_server = %s AND masjid_enabled", (id_server))
            return await cur.fetchall()