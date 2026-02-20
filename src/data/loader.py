import json
from datetime import datetime
from config import SYSTEM_TIMEZONE

def load_json(filename):
    with open(filename) as f:
        return json.load(f)
    
def save_json(filename, new_data):
    with open(filename, 'w') as f:
        json.dump(new_data, f, indent=4)
    
def save_presence(jadwal_hariini):
    system_date = str(datetime.now(SYSTEM_TIMEZONE).date())
    jadwal.presensi_rawatib[system_date] = jadwal_hariini

    save_json("src/data/presensi_rawatib.json", jadwal.presensi_rawatib)

    jadwal.presensi_rawatib = load_json("src/data/presensi_rawatib.json")
    jadwal.jadwal_hariini = load_json("src/data/presensi_rawatib.json")[system_date]
    
class Jadwal():
    def __init__(self):
        self.jadwal_sholat_bulanini = None
        self.jadwal_rawatib = None
        self.anggota = None
        self.presensi_rawatib = None
        self.jadwal_hariini = None

jadwal = Jadwal()

jadwal.jadwal_sholat_bulanini = load_json("src/data/jadwal_sholat/february.json")["data"]["jadwal"]
jadwal.jadwal_rawatib = load_json("src/data/jadwal_rawatib.json")
jadwal.anggota = load_json("src/data/anggota.json")
jadwal.presensi_rawatib = load_json("src/data/presensi_rawatib.json")