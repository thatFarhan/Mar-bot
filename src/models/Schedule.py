from repository.loader import jadwal

class Schedule:
    def __init__(self, tanggal, tugas, sholat, tempat):
        self.tanggal: str = tanggal
        self.tugas: str = tugas
        self.sholat: str = sholat
        self.tempat: str = tempat

    def get_key(self) -> str:
        return f"{self.tanggal}_{self.tugas}_{self.sholat}_{self.tempat}"
    
    def get_pic_id(self) -> int:
        id_sub = jadwal.presensi_rawatib[self.tanggal][self.tempat][self.sholat][self.tugas]["id_sub"]
        if id_sub != 0:
            return id_sub
        else:
            return jadwal.presensi_rawatib[self.tanggal][self.tempat][self.sholat][self.tugas]["id_anggota"]