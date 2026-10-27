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