import json
import asyncio
import os
import tempfile
from datetime import datetime
from config import SYSTEM_TIMEZONE

lock = asyncio.Lock()

def load_json(filename: str):
    with open(filename) as f:
        return json.load(f)
    
async def save_json(filename: str, new_data: dict):
    async with lock:
        dir_name = os.path.dirname(filename) or "."

        with tempfile.NamedTemporaryFile("w", delete=False, dir=dir_name) as tmp:
            json.dump(new_data, tmp, indent=4)
            temp_name = tmp.name

        os.replace(temp_name, filename)
    
async def save_presence(jadwal_hariini):
    system_date = str(datetime.now(SYSTEM_TIMEZONE).date())
    jadwal.presensi_rawatib[system_date] = jadwal_hariini

    await save_json("src/data/presensi_rawatib.json", jadwal.presensi_rawatib)

    jadwal.presensi_rawatib = load_json("src/data/presensi_rawatib.json")
    jadwal.jadwal_hariini = load_json("src/data/presensi_rawatib.json")[system_date]
    
class Jadwal():
    def __init__(self):
        self.data_sholat = None
        self.jadwal_sholat = None
        self.jadwal_rawatib = None
        self.anggota = None
        self.presensi_rawatib = None
        self.jadwal_hariini = None
        self.jadwal_jumat = None

jadwal = Jadwal()

jadwal.data_sholat = load_json("src/data/jadwal_sholat.json")["data"]
jadwal.jadwal_sholat = jadwal.data_sholat["jadwal"]
jadwal.jadwal_rawatib = load_json("src/data/jadwal_rawatib.json")
jadwal.anggota = load_json("src/data/anggota.json")
jadwal.presensi_rawatib = load_json("src/data/presensi_rawatib.json")
jadwal.jadwal_jumat = load_json("src/data/jadwal_jumat.json")