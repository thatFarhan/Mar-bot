from dotenv import load_dotenv
from zoneinfo import ZoneInfo
import os
import discord
from discord.ext import commands
from enum import Enum

load_dotenv()
token=os.getenv('DISCORD_TOKEN')
# change these with your server's channel ids
WELCOME_CHANNEL=1474251557284610223
DAILY_SCHEDULE_CHANNEL=1470291576398938186
SUB_REQUESTS_CHANNEL=1470733669273436200
REMINDERS_CHANNEL=1471430354366632088
ADMIN_CHANNEL=1475290246773080075

GUILD_ID=discord.Object(id=os.getenv('GUILD_ID'))

intents=discord.Intents.default()
intents.message_content=True
intents.members=True
intents.guilds=True

# system_day is 4 hours ahead so that the day changes at 20:00
ACTUAL_TIMEZONE=ZoneInfo("Asia/Jakarta")
SYSTEM_TIMEZONE=ZoneInfo("Asia/Magadan")

SHOLAT_TUPLE = ("subuh", "dzuhur", "ashar", "maghrib", "isya")

NAMA_HARI = ("Senin", "Selasa", "Rabu", "Kamis", "Jum'at", "Sabtu", "Ahad")

SHOLAT_TITLE={
    "subuh": "🌅 Subuh", 
    "dzuhur": "☀️ Dzuhur",
    "jum'at": "☀️ Jum'at",
    "ashar": "🌇 Ashar", 
    "maghrib": "🌆 Maghrib", 
    "isya": "🌔 Isya"
}

TEMPAT_TITLE={
    "msu": "🕌 Masjid Syamsul 'Ulum",
    "tult": "🗼 TULT"
}

# options for single actions
class TugasEnum(str, Enum):
    Imam = "Imam"
    Muadzin = "Muadzin"
    Badal = "Badal"
    Hadits = "Hadits"

class SholatEnum(str, Enum):
    Subuh = "subuh"
    Dzuhur = "dzuhur"
    Ashar = "ashar"
    Maghrib = "maghrib"
    Isya = "isya"

class TempatEnum(str, Enum):
    MSU = "msu"
    TULT = "tult"

bot=commands.Bot(command_prefix="/", intents=intents)
mention_everyone = discord.AllowedMentions(everyone=True)