from repository.loader import jadwal
from config import NAMA_BULAN, NAMA_HARI
from mission_util import to_datetime, to_indo_date_format

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
        
    def get_reasoned_desc(self, title_petugas: str, replacement_petugas: str = None) -> str:
        hari = NAMA_HARI[to_datetime(self.tanggal).weekday()]
        if replacement_petugas:
            nama_petugas = replacement_petugas
        else:
            nama_petugas = jadwal.anggota[self.get_pic_id()]['nama']
        alasan_harian = jadwal.alasan_absen.get(self.tanggal)
        alasan = alasan_harian.get(str(self.get_pic_id()))
        return f"Hari: {hari}\nTanggal: {to_indo_date_format(self.tanggal)}\nTugas: {self.tugas}\nSholat: {self.sholat.capitalize()}\nTempat: {self.tempat.upper()}\n{title_petugas}: {nama_petugas}\n\nAlasan:\n>>> {alasan}"
    
    def get_unreasoned_desc(self, title_petugas: str, replacement_petugas: str = None) -> str:
        hari = NAMA_HARI[to_datetime(self.tanggal).weekday()]
        if replacement_petugas:
            nama_petugas = replacement_petugas
        else:
            nama_petugas = jadwal.anggota[self.get_pic_id()]['nama']
        return f"Hari: {hari}\nTanggal: {to_indo_date_format(self.tanggal)}\nTugas: {self.tugas}\nSholat: {self.sholat.capitalize()}\nTempat: {self.tempat.upper()}\n{title_petugas}: {nama_petugas}"