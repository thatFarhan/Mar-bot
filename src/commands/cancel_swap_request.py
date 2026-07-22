import discord
from config import NAMA_HARI
from mission_util import to_datetime
from repository.loader import jadwal
from repository.persistent_loader import save_persistent
from models.Schedule import Schedule
from events.purge_transaction import purge_offerers

async def cancel_swap_request(interaction: discord.Interaction, requested_schedule: Schedule):
    id_peminta = requested_schedule.get_pic_id()
    uid_peminta = jadwal.anggota[id_peminta]['uid']

    if interaction.user.id != uid_peminta:
        await interaction.response.send_message("Lau sape mpruy? 🫵😂", ephemeral=True)
        return
    
    hari = NAMA_HARI[to_datetime(requested_schedule.tanggal).weekday()]

    id_anggota = requested_schedule.get_pic_id()
        
    nama_petugas_sebelumnya = jadwal.anggota[id_anggota]['nama']
    alasan_harian = jadwal.alasan_absen.get(requested_schedule.tanggal)
    alasan = alasan_harian.get(str(id_anggota))
    embed_desc=f"Hari: {hari}\nTugas: {requested_schedule.tugas}\nSholat: {requested_schedule.sholat.capitalize()}\nTempat: {requested_schedule.tempat.upper()}\nPetugas Sebelumnya: {nama_petugas_sebelumnya}\n\nAlasan:\n>>> {alasan}"

    embed=discord.Embed(
        title="Detail Jadwal", 
        color=discord.Color.red(),
        description=embed_desc
    )

    content=f"❌ **Permintaan Dibatalkan**"

    await interaction.response.edit_message(content=content, embed=embed, view=None)

    await purge_offerers(requested_schedule, "❌ Permintaan Dibatalkan")
    await save_persistent()