from config import bot

# INSERT

async def insert_alasan_absen(id_presensi: int, id_anggota: int, alasan: str):
    async with bot.db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO alasan_absen (id_presensi, id_anggota, alasan) VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE alasan = VALUES(alasan)
                """,
                (id_presensi, id_anggota, alasan)
            )

async def insert_many_alasan_absen(rows: list):
    async with bot.db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.executemany(
                """
                INSERT INTO alasan_absen (id_presensi, id_anggota, alasan) VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE alasan = VALUES(alasan)
                """,
                rows
            )

# GET

async def get_alasan_absen(id_presensi: int, id_anggota: int):
    async with bot.db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "SELECT alasan FROM alasan_absen WHERE id_presensi = %s AND id_anggota = %s",
                (id_presensi, id_anggota)
            )
            return await cur.fetchone()