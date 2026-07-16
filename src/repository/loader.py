import json
import asyncio
import os
import tempfile
from global_vars import global_vars

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
    
async def save_presence(jadwal_harian, tanggal: str = global_vars.system_date):
    jadwal.presensi_rawatib[tanggal] = jadwal_harian

    await save_json("src/data/presensi_rawatib.json", jadwal.presensi_rawatib)

    if tanggal == global_vars.system_date:
        jadwal.presensi_rawatib = load_json("src/data/presensi_rawatib.json")

async def save_reason():
    await save_json("src/data/alasan_absen.json", jadwal.alasan_absen)
    
class Jadwal():
    def __init__(self):
        self.data_sholat = None
        self.jadwal_sholat = None
        self.jadwal_rawatib = None
        self.anggota = None
        self.presensi_rawatib = None
        self.jadwal_jumat = None
        self.alasan_absen = None

jadwal = Jadwal()

jadwal.data_sholat = load_json("src/data/jadwal_sholat.json")["data"]
jadwal.jadwal_sholat = jadwal.data_sholat["jadwal"]
jadwal.jadwal_rawatib = load_json("src/data/jadwal_rawatib.json")
jadwal.anggota = load_json("src/data/anggota.json")
jadwal.presensi_rawatib = load_json("src/data/presensi_rawatib.json")
jadwal.jadwal_jumat = load_json("src/data/jadwal_jumat.json")
jadwal.alasan_absen = load_json("src/data/alasan_absen.json")