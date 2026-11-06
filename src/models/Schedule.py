from datetime import date
from config import NAMA_HARI
from mission_util import to_indo_date_format

class Schedule:
    def __init__(self, schedule: dict):
        self.id_presensi: int = schedule["id_presensi"]
        self.tanggal: date = schedule["tanggal"]
        self.hari: str = NAMA_HARI[self.tanggal.weekday()]
        self.tugas: str = schedule["tugas"]
        self.sholat: str = schedule["sholat"]
        self.nama_masjid: str = schedule["nama_masjid"]
        nama_reg = schedule["nama_reg"]
        nama_pic = schedule["nama_pic"]
        self.nama_petugas: str = nama_pic if nama_pic is not None else nama_reg
        id_reg = schedule["id_reg"]
        id_pic = schedule["id_pic"]
        self.id_petugas: int = id_pic if id_pic is not None else id_reg
        uid_reg = schedule["uid_reg"]
        uid_pic = schedule["uid_pic"]
        self.uid_petugas: int = uid_pic if uid_pic is not None else uid_reg
        
    def get_desc(self, alasan: str = None) -> str:
        desc = f"""
        Hari: {self.hari}
        Tanggal: {to_indo_date_format(self.tanggal)}
        Tugas: {self.tugas}
        Sholat: {self.sholat}
        Tempat: {self.nama_masjid}
        Petugas Sebelumnya: {self.nama_petugas}
        """

        if alasan:
            desc += f"\n\nAlasan:\n>>> {alasan}"

        return desc