from config import bot
from datetime import date

# INSERT

async def insert_presensi(tanggal: date, id_jadwal_tetap: int):
    async with bot.db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "INSERT INTO presensi (tanggal, id_jadwal_tetap) VALUES (%s, %s)",
                (tanggal, id_jadwal_tetap)
            )

async def insert_many_presensi(rows: list):
    async with bot.db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.executemany(
                "INSERT INTO presensi (tanggal, id_jadwal_tetap) VALUES (%s, %s)",
                rows,
            )

# GET

async def tanggal_and_masjid_exists_in_presensi(tanggal: date, id_masjid: int):
    async with bot.db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT COUNT(*) AS total
                FROM presensi 
                JOIN jadwal_tetap ON presensi.id_jadwal_tetap = jadwal_tetap.id_jadwal_tetap 
                JOIN masjid ON jadwal_tetap.id_masjid = masjid.id_masjid
                WHERE presensi.tanggal = %s AND jadwal_tetap.id_masjid = %s AND masjid.masjid_enabled
                """,
                (tanggal, id_masjid)
            )
            row = await cur.fetchone()
            return row["total"] > 0