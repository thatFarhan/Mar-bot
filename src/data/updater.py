import json
from data.loader import jadwal
from global_vars import scheduler

def update_to_sell(tugas: str, sholat: str, tempat: str):
    if tugas == 'Pembaca Hadits': return

    petugas=jadwal.jadwal_hariini[tempat][sholat][tugas]
    petugas["confirmed"] = False
    petugas["need_sub"] = True
    petugas["id_sub"] = 0

    if scheduler.get_job(job_id=f"emergency_{tugas}_{sholat}_{tempat}"):
        scheduler.remove_job(job_id=f"emergency_{tugas}_{sholat}_{tempat}")
        
def update_to_confirm(tugas: str, sholat: str, tempat: str):
    petugas=jadwal.jadwal_hariini[tempat][sholat][tugas]
    petugas["confirmed"] = True
    petugas["need_sub"] = False
    petugas["id_sub"] = 0

    if scheduler.get_job(job_id=f"emergency_{tugas}_{sholat}_{tempat}"):
        scheduler.remove_job(job_id=f"emergency_{tugas}_{sholat}_{tempat}")

def update_to_claim(tugas: str, sholat: str, tempat: str, id: int):
    petugas=jadwal.jadwal_hariini[tempat][sholat][tugas]
    petugas["confirmed"] = True
    petugas["need_sub"] = False
    petugas["id_sub"] = id

    if scheduler.get_job(job_id=f"emergency_{tugas}_{sholat}_{tempat}"):
        scheduler.remove_job(job_id=f"emergency_{tugas}_{sholat}_{tempat}")