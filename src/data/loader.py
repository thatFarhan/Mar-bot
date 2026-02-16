import json

def load_json(filename):
    with open(filename) as f:
        return json.load(f)
    
class Jadwal():
    def __init__(self):
        self.jadwal_sholat_bulanini = None
        self.jadwal_petugas = None
        self.jadwal_hariini = None
        self.nama_asli = None

jadwal = Jadwal()

jadwal.jadwal_sholat_bulanini = load_json("jadwal_sholat.json")["data"]["jadwal"]
jadwal.jadwal_petugas = load_json("jadwal_petugas.json")
jadwal.jadwal_hariini = load_json("jadwal_hariini.json")
jadwal.nama_asli = load_json("nama_asli.json")