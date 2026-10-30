import asyncio
import sys

from server_config import WELCOME_CHANNEL, DAILY_SCHEDULE_CHANNEL, SUB_REQUESTS_CHANNEL, REMINDERS_CHANNEL, ADMIN_CHANNEL

REGION = "Jawa Barat_Kota Bandung"

INSERT_SERVER = (
    "INSERT INTO discord_server (id_server, welcome_channel, daily_schedule_channel, sub_requests_channel, reminders_channel, admin_channel)"
    "VALUES (%s, %s, %s, %s, %s, %s)"
)

MASJID_ROWS = [
    ("Masjid Syamsul 'Ulum", REGION, True, True),
    ("Masjid TULT", REGION, True, True),
]

INSERT_MASJID = (
    "INSERT INTO masjid (nama_masjid, region, is_weekly, masjid_enabled, id_server) "
    "VALUES (%s, %s, %s, %s, %s)"
)


def get_guild_id() -> int:
    from server_config import GUILD_ID  # discord.Object(id=...)

    return GUILD_ID.id if hasattr(GUILD_ID, "id") else int(GUILD_ID)


async def main():
    import aiomysql

    id_server = get_guild_id()

    conn = await aiomysql.connect(
        user="root",
        db="marbot",
        autocommit=False,
    )
    try:
        async with conn.cursor() as cur:
            await cur.execute(
                INSERT_SERVER,
                (id_server, WELCOME_CHANNEL, DAILY_SCHEDULE_CHANNEL, SUB_REQUESTS_CHANNEL, REMINDERS_CHANNEL, ADMIN_CHANNEL)
            )
            await cur.execute("ALTER TABLE masjid AUTO_INCREMENT = 1")
            await cur.execute("SELECT COUNT(*) FROM masjid")
            (count,) = await cur.fetchone()
            if count:
                print(f"masjid already has {count} rows, nothing to do.")
                return

            await cur.executemany(
                INSERT_MASJID,
                [row + (id_server,) for row in MASJID_ROWS],
            )
        await conn.commit()
        print(f"Inserted {len(MASJID_ROWS)} masjid rows (id_server={id_server}).")
    except Exception:
        await conn.rollback()
        raise
    finally:
        conn.close()