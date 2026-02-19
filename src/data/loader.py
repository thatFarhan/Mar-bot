import json
from datetime import date

def load_json(filename):
    with open(filename) as f:
        return json.load(f)
    
def save_presence(jadwal_hariini):
    jadwal.presensi_rawatib[str(date.today())] = jadwal_hariini

    with open('src/data/presensi_rawatib.json', 'w') as file:
        json.dump(jadwal.presensi_rawatib, file, indent=2)

    jadwal.presensi_rawatib = load_json("src/data/presensi_rawatib.json")
    jadwal.jadwal_hariini = load_json("src/data/presensi_rawatib.json")[str(date.today())]
    
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