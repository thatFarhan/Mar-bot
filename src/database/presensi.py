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

# UPDATE

async def update_to_confirm_all(tanggal: date, id_server: int, uid_anggota: int):
    async with bot.db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                UPDATE presensi pr
                INNER JOIN jadwal_tetap jt ON pr.id_jadwal_tetap = jt.id_jadwal_tetap
                SET pr.confirmed = TRUE, pr.id_pic = jt.id_anggota
                WHERE id_presensi IN (
                    SELECT id_presensi
                    FROM presensi p
                    JOIN jadwal_tetap j ON p.id_jadwal_tetap = j.id_jadwal_tetap
                    JOIN masjid m ON j.id_masjid = m.id_masjid
                    LEFT JOIN anggota reg ON j.id_anggota = reg.id_anggota
                    LEFT JOIN anggota pic ON p.id_pic = pic.id_anggota
                    WHERE p.tanggal = %s
                    AND p.need_sub = FALSE
                    AND p.swap_requested = FALSE
                    AND m.id_server = %s
                    AND (pic.discord_uid = %s OR reg.discord_uid = %s AND p.id_pic IS NULL)
                )
                """,
                (tanggal, id_server, uid_anggota, uid_anggota)
            )
            return cur.rowcount


async def update_to_confirm_by_ids(id_presensi: list):
    if not id_presensi: return 0
    
    placeholders = ",".join(["%s"] * len(id_presensi))
    async with bot.db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                f"""
                UPDATE presensi pr
                INNER JOIN jadwal_tetap jt ON pr.id_jadwal_tetap = jt.id_jadwal_tetap
                SET pr.id_pic = jt.id_anggota,
                pr.confirmed = TRUE, 
                pr.need_sub = FALSE,
                pr.swap_requested = FALSE
                WHERE id_presensi IN ({placeholders})
                """,
                tuple(id_presensi)
            )
            return cur.rowcount

async def update_to_confirm_from_reminder(tanggal: date, id_server: int, sholat: str, uid_anggota: int):
    async with bot.db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                UPDATE presensi pr
                INNER JOIN jadwal_tetap jt ON pr.id_jadwal_tetap = jt.id_jadwal_tetap
                SET pr.confirmed = TRUE, pr.need_sub = FALSE, pr.swap_requested = FALSE, pr.id_pic = jt.id_anggota
                WHERE id_presensi IN (
                    SELECT p.id_presensi
                    FROM presensi p
                    JOIN jadwal_tetap j ON p.id_jadwal_tetap = j.id_jadwal_tetap
                    JOIN masjid m ON j.id_masjid = m.id_masjid
                    LEFT JOIN anggota reg ON j.id_anggota = reg.id_anggota
                    LEFT JOIN anggota pic ON p.id_pic = pic.id_anggota
                    WHERE p.tanggal = %s
                    AND p.need_sub = FALSE
                    AND p.swap_requested = FALSE
                    AND m.id_server = %s
                    AND j.sholat = %s
                    AND (pic.discord_uid = %s OR reg.discord_uid = %s AND p.id_pic IS NULL)
                )
                """,
                (tanggal, id_server, sholat, uid_anggota, uid_anggota)
            )
            return cur.rowcount

async def update_to_claim_by_id(id_presensi: int, id_pic: int, is_today: bool):
    async with bot.db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                UPDATE presensi SET confirmed = %s, need_sub = FALSE, swap_requested = FALSE, id_pic = %s
                WHERE id_presensi = %s
                """,
                (is_today, id_pic, id_presensi)
            )
            return cur.rowcount

async def update_to_request_sub_by_ids(id_presensi: list):
    if not id_presensi: return 0

    placeholders = ",".join(["%s"] * len(id_presensi))
    async with bot.db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                f"""
                UPDATE presensi SET confirmed = FALSE, need_sub = TRUE
                WHERE id_presensi IN ({placeholders})
                """,
                tuple(id_presensi)
            )
            return cur.rowcount

async def update_to_request_swap_by_ids(id_presensi: list):
    if not id_presensi: return 0

    placeholders = ",".join(["%s"] * len(id_presensi))
    async with bot.db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                f"""
                UPDATE presensi SET confirmed = FALSE, swap_requested = TRUE
                WHERE id_presensi IN ({placeholders})
                """,
                tuple(id_presensi)
            )
            return cur.rowcount

async def update_to_unswap(id_presensi: int):
    async with bot.db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("UPDATE presensi SET swap_requested = FALSE WHERE id_presensi = %s", (id_presensi))
            return cur.rowcount

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


async def get_daily_schedule_for_masjid(tanggal: date, id_masjid: int):
    async with bot.db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT p.id_presensi, p.confirmed, p.need_sub, p.swap_requested, m.nama_masjid, j.sholat, j.tugas, 
                reg.nama_panggilan AS nama_reg,
                reg.discord_uid AS uid_reg,
                pic.nama_panggilan AS nama_pic,
                pic.discord_uid AS uid_pic
                FROM presensi p
                JOIN jadwal_tetap j ON p.id_jadwal_tetap = j.id_jadwal_tetap
                JOIN masjid m ON j.id_masjid = m.id_masjid
                LEFT JOIN anggota reg ON j.id_anggota = reg.id_anggota
                LEFT JOIN anggota pic ON p.id_pic = pic.id_anggota
                WHERE p.tanggal = %s AND j.id_masjid = %s
                ORDER BY j.tugas_order ASC;
                """,
                (tanggal, id_masjid)
            )
            return await cur.fetchall()

# for confirming
async def get_all_my_unconfirmed_schedule_today(tanggal: date, id_server: int, uid_anggota: int):
    async with bot.db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT p.id_presensi, p.tanggal, j.sholat, j.tugas, m.nama_masjid
                FROM presensi p
                JOIN jadwal_tetap j ON p.id_jadwal_tetap = j.id_jadwal_tetap
                JOIN masjid m ON j.id_masjid = m.id_masjid
                LEFT JOIN anggota reg ON j.id_anggota = reg.id_anggota
                LEFT JOIN anggota pic ON p.id_pic = pic.id_anggota
                WHERE p.tanggal = %s 
                AND p.confirmed = FALSE
                AND m.id_server = %s
                AND (pic.discord_uid = %s OR reg.discord_uid = %s AND p.id_pic IS NULL)
                ORDER BY j.id_masjid ASC,
                CASE j.sholat
                    WHEN 'Subuh' THEN 1
                    WHEN 'Dzuhur' THEN 2
                    WHEN 'Ashar' THEN 3
                    WHEN 'Maghrib' THEN 4
                    ELSE 5
                END ASC,
                j.tugas_order ASC
                """,
                (tanggal, id_server, uid_anggota, uid_anggota)
            )
            return await cur.fetchall()

# for requesting a sub; need sub schedules shouldn't reappear
async def get_all_my_unsold_schedule_today(tanggal: date, id_server: int, uid_anggota: int):
    async with bot.db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT p.id_presensi, p.tanggal, j.sholat, j.tugas, m.nama_masjid
                FROM presensi p
                JOIN jadwal_tetap j ON p.id_jadwal_tetap = j.id_jadwal_tetap
                JOIN masjid m ON j.id_masjid = m.id_masjid
                LEFT JOIN anggota reg ON j.id_anggota = reg.id_anggota
                LEFT JOIN anggota pic ON p.id_pic = pic.id_anggota
                WHERE p.tanggal = %s 
                AND p.need_sub = FALSE
                AND m.id_server = %s
                AND (pic.discord_uid = %s OR reg.discord_uid = %s AND p.id_pic IS NULL)
                ORDER BY j.id_masjid ASC,
                CASE j.sholat
                    WHEN 'Subuh' THEN 1
                    WHEN 'Dzuhur' THEN 2
                    WHEN 'Ashar' THEN 3
                    WHEN 'Maghrib' THEN 4
                    ELSE 5
                END ASC,
                j.tugas_order ASC
                """,
                (tanggal, id_server, uid_anggota, uid_anggota)
            )
            return await cur.fetchall()

# for requesting a swap; swap requested schedules shouldn't reappear
async def get_all_my_unswapped_schedule_today(tanggal: date, id_server: int, uid_anggota: int):
    async with bot.db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT p.id_presensi, p.tanggal, j.sholat, j.tugas, m.nama_masjid
                FROM presensi p
                JOIN jadwal_tetap j ON p.id_jadwal_tetap = j.id_jadwal_tetap
                JOIN masjid m ON j.id_masjid = m.id_masjid
                LEFT JOIN anggota reg ON j.id_anggota = reg.id_anggota
                LEFT JOIN anggota pic ON p.id_pic = pic.id_anggota
                WHERE p.tanggal = %s 
                AND p.swap_requested = FALSE
                AND m.id_server = %s
                AND (pic.discord_uid = %s OR reg.discord_uid = %s AND p.id_pic IS NULL)
                ORDER BY j.id_masjid ASC,
                CASE j.sholat
                    WHEN 'Subuh' THEN 1
                    WHEN 'Dzuhur' THEN 2
                    WHEN 'Ashar' THEN 3
                    WHEN 'Maghrib' THEN 4
                    ELSE 5
                END ASC,
                j.tugas_order ASC
                """,
                (tanggal, id_server, uid_anggota, uid_anggota)
            )
            return await cur.fetchall()

# for offering swaps
async def get_all_my_schedule_thisweek(tanggal: date, id_server: int, uid_anggota: int):
    async with bot.db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT p.id_presensi, p.tanggal, j.sholat, j.tugas, m.nama_masjid
                FROM presensi p
                JOIN jadwal_tetap j ON p.id_jadwal_tetap = j.id_jadwal_tetap
                JOIN masjid m ON j.id_masjid = m.id_masjid
                LEFT JOIN anggota reg ON j.id_anggota = reg.id_anggota
                LEFT JOIN anggota pic ON p.id_pic = pic.id_anggota
                WHERE p.tanggal >= %s
                AND p.tanggal <= %s + INTERVAL 6 DAY
                AND m.id_server = %s
                AND (pic.discord_uid = %s OR reg.discord_uid = %s AND p.id_pic IS NULL)
                ORDER BY p.tanggal ASC, 
                j.id_masjid ASC, 
                CASE j.sholat
                    WHEN 'Subuh' THEN 1
                    WHEN 'Dzuhur' THEN 2
                    WHEN 'Ashar' THEN 3
                    WHEN 'Maghrib' THEN 4
                    ELSE 5
                END ASC,
                j.tugas_order ASC
                """,
                (tanggal, tanggal, id_server, uid_anggota, uid_anggota)
            )
            return await cur.fetchall()

# for requesting a swap; swap requested schedules shouldn't reappear
async def get_all_my_unswapped_schedule_thisweek(tanggal: date, id_server: int, uid_anggota: int):
    async with bot.db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT p.id_presensi, p.tanggal, j.sholat, j.tugas, m.nama_masjid
                FROM presensi p
                JOIN jadwal_tetap j ON p.id_jadwal_tetap = j.id_jadwal_tetap
                JOIN masjid m ON j.id_masjid = m.id_masjid
                LEFT JOIN anggota reg ON j.id_anggota = reg.id_anggota
                LEFT JOIN anggota pic ON p.id_pic = pic.id_anggota
                WHERE p.tanggal >= %s
                AND p.tanggal <= %s + INTERVAL 6 DAY
                AND p.swap_requested = FALSE
                AND m.id_server = %s
                AND (pic.discord_uid = %s OR reg.discord_uid = %s AND p.id_pic IS NULL)
                ORDER BY p.tanggal ASC, 
                j.id_masjid ASC, 
                CASE j.sholat
                    WHEN 'Subuh' THEN 1
                    WHEN 'Dzuhur' THEN 2
                    WHEN 'Ashar' THEN 3
                    WHEN 'Maghrib' THEN 4
                    ELSE 5
                END ASC,
                j.tugas_order ASC
                """,
                (tanggal, tanggal, id_server, uid_anggota, uid_anggota)
            )
            return await cur.fetchall()

# for requesting a sub; need sub schedules shouldn't reappear
async def get_all_my_unsold_schedule_thisweek(tanggal: date, id_server: int, uid_anggota: int):
    async with bot.db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT p.id_presensi, p.tanggal, j.sholat, j.tugas, m.nama_masjid
                FROM presensi p
                JOIN jadwal_tetap j ON p.id_jadwal_tetap = j.id_jadwal_tetap
                JOIN masjid m ON j.id_masjid = m.id_masjid
                LEFT JOIN anggota reg ON j.id_anggota = reg.id_anggota
                LEFT JOIN anggota pic ON p.id_pic = pic.id_anggota
                WHERE p.tanggal >= %s
                AND p.tanggal <= %s + INTERVAL 6 DAY
                AND p.need_sub = FALSE
                AND m.id_server = %s
                AND (pic.discord_uid = %s OR reg.discord_uid = %s AND p.id_pic IS NULL)
                ORDER BY p.tanggal ASC, 
                j.id_masjid ASC, 
                CASE j.sholat
                    WHEN 'Subuh' THEN 1
                    WHEN 'Dzuhur' THEN 2
                    WHEN 'Ashar' THEN 3
                    WHEN 'Maghrib' THEN 4
                    ELSE 5
                END ASC,
                j.tugas_order ASC
                """,
                (tanggal, tanggal, id_server, uid_anggota, uid_anggota)
            )
            return await cur.fetchall()


async def get_schedule_by_id(id_presensi: int):
    async with bot.db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT p.id_presensi, p.tanggal, j.sholat, j.tugas, m.nama_masjid, p.confirmed, p.need_sub, p.swap_requested,
                reg.id_anggota AS id_reg,
                reg.nama_panggilan AS nama_reg,
                reg.discord_uid AS uid_reg,
                pic.id_anggota AS id_pic,
                pic.nama_panggilan AS nama_pic,
                pic.discord_uid AS uid_pic
                FROM presensi p
                JOIN jadwal_tetap j ON p.id_jadwal_tetap = j.id_jadwal_tetap
                JOIN masjid m ON j.id_masjid = m.id_masjid
                LEFT JOIN anggota reg ON j.id_anggota = reg.id_anggota
                LEFT JOIN anggota pic ON p.id_pic = pic.id_anggota
                WHERE id_presensi = %s
                """,
                (id_presensi)
            )
            return await cur.fetchone()

async def get_reminder(tanggal: date, sholat: str, id_server: int):
    async with bot.db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT p.id_presensi, p.confirmed, p.need_sub, p.swap_requested, m.nama_masjid, j.sholat, j.tugas, 
                reg.nama_panggilan AS nama_reg,
                reg.discord_uid AS uid_reg,
                pic.nama_panggilan AS nama_pic,
                pic.discord_uid AS uid_pic
                FROM presensi p
                JOIN jadwal_tetap j ON p.id_jadwal_tetap = j.id_jadwal_tetap
                JOIN masjid m ON j.id_masjid = m.id_masjid
                LEFT JOIN anggota reg ON j.id_anggota = reg.id_anggota
                LEFT JOIN anggota pic ON p.id_pic = pic.id_anggota
                WHERE p.tanggal = %s
                AND m.id_server = %s
                AND j.sholat = %s
                ORDER BY j.id_masjid ASC,
                j.tugas_order ASC;
                """,
                (tanggal, id_server, sholat)
            )
            return await cur.fetchall()