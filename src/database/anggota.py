from config import bot

# INSERT

async def insert_anggota(guild_id: int, nama_panggilan: str, nama_lengkap: str, discord_uid: int = None):
    async with bot.db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "INSERT INTO anggota (id_server, discord_uid, nama_panggilan, nama_lengkap) VALUES (%s, %s, %s, %s)", 
                (guild_id, discord_uid, nama_panggilan, nama_lengkap)
            )

# UPDATE

async def update_discord_uid(id_anggota: int, discord_uid: int):
    async with bot.db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("UPDATE anggota SET discord_uid = %s WHERE id_anggota = %s", (discord_uid, id_anggota))

async def update_name(id_anggota: int, nama_panggilan: str, nama_lengkap: str):
    async with bot.db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("UPDATE anggota SET nama_panggilan = %s, nama_lengkap = %s WHERE id_anggota = %s", (nama_panggilan, nama_lengkap, id_anggota))

# GET

async def get_all_unregistered_anggota_from_server(guild_id: int):
    async with bot.db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "SELECT id_anggota, nama_lengkap FROM anggota WHERE id_server = %s AND discord_uid IS NULL ORDER BY nama_lengkap",
                (guild_id)
            )
            return await cur.fetchall()