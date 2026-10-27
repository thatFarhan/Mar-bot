from config import bot

# INSERT

async def insert_jadwal_tetap(id_masjid: int, hari: int, sholat: str, tugas: str, tugas_order: int, id_anggota: int):
    async with bot.db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "INSERT INTO jadwal_tetap (id_masjid, hari, sholat, tugas, tugas_order, id_anggota) VALUES (%s, %s, %s, %s, %s, %s)",
                (id_masjid, hari, sholat, tugas, tugas_order, id_anggota)
            )