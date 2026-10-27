from config import bot

# INSERT

async def insert_masjid(nama_masjid: str, alamat_masjid: str, region: str, is_weekly: bool, masjid_enabled: bool, id_server: int):
    async with bot.db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "INSERT INTO masjid (nama_masjid, alamat_masjid, region, is_weekly, masjid_enabled, id_server) VALUES (%s, %s, %s, %s, %s, %s)",
                (nama_masjid, alamat_masjid, region, is_weekly, masjid_enabled, id_server)
            )