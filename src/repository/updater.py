from repository.loader import jadwal
from global_vars import scheduler, global_vars

def update_to_sell(tugas: str, sholat: str, tempat: str):
    if tugas == 'Hadits': return

    petugas = jadwal.presensi_rawatib[global_vars.system_date][tempat][sholat][tugas]
    petugas["confirmed"] = False
    petugas["need_sub"] = True
    petugas["id_sub"] = 0

    if scheduler.get_job(job_id=f"emergency_{tugas}_{sholat}_{tempat}"):
        scheduler.remove_job(job_id=f"emergency_{tugas}_{sholat}_{tempat}")
        
def update_to_sell_week(tanggal: str, tugas: str, sholat: str, tempat: str):
    if tugas == 'Hadits': return

    petugas = jadwal.presensi_rawatib[tanggal][tempat][sholat][tugas]
    petugas["confirmed"] = False
    petugas["need_sub"] = True
    petugas["id_sub"] = 0

    if global_vars.system_date == tanggal and scheduler.get_job(job_id=f"emergency_{tugas}_{sholat}_{tempat}"):
        scheduler.remove_job(job_id=f"emergency_{tugas}_{sholat}_{tempat}")

def update_to_confirm(tanggal: str, tugas: str, sholat: str, tempat: str):
    petugas = jadwal.presensi_rawatib[tanggal][tempat][sholat][tugas]
    if tanggal == global_vars.system_date:
        petugas["confirmed"] = True
    else:
        petugas["confirmed"] = False
    petugas["need_sub"] = False

    if scheduler.get_job(job_id=f"emergency_{tugas}_{sholat}_{tempat}"):
        scheduler.remove_job(job_id=f"emergency_{tugas}_{sholat}_{tempat}")

def update_to_claim(tanggal: str, tugas: str, sholat: str, tempat: str, id: int):
    petugas = jadwal.presensi_rawatib[tanggal][tempat][sholat][tugas]
    if tanggal == global_vars.system_date:
        petugas["confirmed"] = True
    else:
        petugas["confirmed"] = False
    petugas["need_sub"] = False
    petugas["id_sub"] = id

    if global_vars.system_date == tanggal and scheduler.get_job(job_id=f"emergency_{tugas}_{sholat}_{tempat}"):
        scheduler.remove_job(job_id=f"emergency_{tugas}_{sholat}_{tempat}")