from config import bot
from database.discord_server import insert_guild

@bot.event
async def on_guild_join(guild):
    await insert_guild(guild.id)