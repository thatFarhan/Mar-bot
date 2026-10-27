from config import bot
from enum import Enum

class ChannelTypeEnum(str, Enum):
    Welcome = "welcome_channel"
    Jadwal = "daily_schedule_channel"
    Pengingat = "reminders_channel"
    Pengganti = "sub_requests_channel"
    Admin = "admin_channel"

# INSERT

async def insert_guild(guild_id: int):
    async with bot.db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("INSERT IGNORE INTO discord_server (id_server) VALUES (%s)", (guild_id))

# UPDATE

async def update_channel(channel_type: str, guild_id: int, channel_id: int):
    await insert_guild(guild_id)
    async with bot.db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(f"UPDATE discord_server SET `{channel_type}` = %s WHERE id_server = %s", (channel_id, guild_id))

async def update_bot_config(guild_id: int, auto_sell_enabled: bool):
    await insert_guild(guild_id)
    async with bot.db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(f"UPDATE discord_server SET auto_sell_enabled = %s WHERE id_server = %s", (auto_sell_enabled, guild_id))

async def update_daily_schedule_message_id(guild_id: int, message_id: int):
    await insert_guild(guild_id)
    async with bot.db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(f"UPDATE discord_server SET id_daily_schedule_message = %s WHERE id_server = %s", (message_id, guild_id))

# GET

async def get_all_servers():
    async with bot.db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT id_server FROM discord_server")
            return await cur.fetchall()

async def get_channel(channel_type: str, guild_id: int):
    async with bot.db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(f"SELECT {channel_type} FROM discord_server WHERE id_server = %s", (guild_id))
            return await cur.fetchone()

async def get_bot_config(guild_id: int):
    async with bot.db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT auto_sell_enabled FROM discord_server WHERE id_server = %s", (guild_id))
            return await cur.fetchone()

async def get_daily_schedule_message_id(guild_id: int):
    async with bot.db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT id_daily_schedule_message FROM discord_server WHERE id_server = %s", (guild_id))
            return await cur.fetchone()



