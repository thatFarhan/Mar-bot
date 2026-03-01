import aiohttp
from datetime import datetime
from config import SYSTEM_TIMEZONE
from data.loader import load_json, save_json, jadwal

async def get_new_schedule():
    month = datetime.now(SYSTEM_TIMEZONE).month
    year = datetime.now(SYSTEM_TIMEZONE).year
    async with aiohttp.ClientSession() as session:
        async with session.post("https://equran.id/api/v2/shalat", json={"provinsi": "Jawa Barat", "kabkota": "Kota Bandung", "bulan": month, "tahun": year}) as resp:
            result = await resp.json()
            await save_json("src/data/jadwal_sholat.json", result)
            jadwal.data_sholat = load_json("src/data/jadwal_sholat.json")["data"]
            jadwal.jadwal_sholat = jadwal.data_sholat["jadwal"]