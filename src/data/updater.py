import json
from data.loader import jadwal
from global_vars import scheduler

def update_to_sell(tugas: str, sholat: str, tempat: str):
    if tugas == 'Pembaca Hadits': return

    petugas=jadwal.jadwal_hariini[tempat][sholat][tugas]
    petugas["confirmed"] = False
    petugas["need_sub"] = True
    petugas["nama_sub"] = None
    petugas["uid_sub"] = None

    if scheduler.get_job(job_id=f"emergency_{tugas}_{sholat}_{tempat}"):
        scheduler.remove_job(job_id=f"emergency_{tugas}_{sholat}_{tempat}")
        
def update_to_confirm(tugas: str, sholat: str, tempat: str):
    petugas=jadwal.jadwal_hariini[tempat][sholat][tugas]
    petugas["confirmed"] = True
    petugas["need_sub"] = False
    petugas["nama_sub"] = None
    petugas["uid_sub"] = None

    if scheduler.get_job(job_id=f"emergency_{tugas}_{sholat}_{tempat}"):
        scheduler.remove_job(job_id=f"emergency_{tugas}_{sholat}_{tempat}")

def update_to_claim(tugas: str, sholat: str, tempat: str, uid: int):
    petugas=jadwal.jadwal_hariini[tempat][sholat][tugas]
    petugas["confirmed"] = True
    petugas["need_sub"] = False
    petugas["nama_sub"] = jadwal.nama_asli[str(uid)]
    petugas["uid_sub"] = uid

    if scheduler.get_job(job_id=f"emergency_{tugas}_{sholat}_{tempat}"):
        scheduler.remove_job(job_id=f"emergency_{tugas}_{sholat}_{tempat}")