from config import bot

# INSERT

async def insert_jadwal_tetap(id_masjid: int, hari: int, sholat: str, tugas: str, tugas_order: int, id_anggota: int):
    async with bot.db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "INSERT INTO jadwal_tetap (id_masjid, hari, sholat, tugas, tugas_order, id_anggota) VALUES (%s, %s, %s, %s, %s, %s)",
                (id_masjid, hari, sholat, tugas, tugas_order, id_anggota)
            )

# GET

async def get_id_jadwal_tetap_on_day(hari: int, id_masjid: int):
    async with bot.db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "SELECT id_jadwal_tetap FROM jadwal_tetap WHERE hari = %s AND id_masjid = %s",
                (hari, id_masjid)
            )
            rows = await cur.fetchall()
            return [row["id_jadwal_tetap"] for row in rows]