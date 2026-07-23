from repository.loader import jadwal
from global_vars import scheduler, global_vars
from models.Schedule import Schedule
        
def update_to_sell(schedule: Schedule):
    tanggal = schedule.tanggal
    tempat = schedule.tempat
    sholat = schedule.sholat
    tugas = schedule.tugas
    if tugas == 'Hadits': return

    petugas = jadwal.presensi_rawatib[tanggal][tempat][sholat][tugas]
    petugas["confirmed"] = False
    petugas["need_sub"] = True

    if global_vars.system_date == tanggal and scheduler.get_job(job_id=f"emergency_{tugas}_{sholat}_{tempat}"):
        scheduler.remove_job(job_id=f"emergency_{tugas}_{sholat}_{tempat}")

def update_to_confirm(schedule: Schedule):
    tanggal = schedule.tanggal
    tempat = schedule.tempat
    sholat = schedule.sholat
    tugas = schedule.tugas
    petugas = jadwal.presensi_rawatib[tanggal][tempat][sholat][tugas]
    if tanggal == global_vars.system_date:
        petugas["confirmed"] = True
    petugas["need_sub"] = False

    if scheduler.get_job(job_id=f"emergency_{tugas}_{sholat}_{tempat}"):
        scheduler.remove_job(job_id=f"emergency_{tugas}_{sholat}_{tempat}")

def update_to_claim(schedule: Schedule, id: int):
    tanggal = schedule.tanggal
    tempat = schedule.tempat
    sholat = schedule.sholat
    tugas = schedule.tugas
    petugas = jadwal.presensi_rawatib[tanggal][tempat][sholat][tugas]
    if tanggal == global_vars.system_date:
        petugas["confirmed"] = True
    petugas["need_sub"] = False

    if petugas["id_anggota"] == id:
        petugas["id_sub"] = 0
    else:
        petugas["id_sub"] = id

    if global_vars.system_date == tanggal and scheduler.get_job(job_id=f"emergency_{tugas}_{sholat}_{tempat}"):
        scheduler.remove_job(job_id=f"emergency_{tugas}_{sholat}_{tempat}")