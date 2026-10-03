import discord
import datetime
from datetime import timedelta
from repository.loader import jadwal, save_json

class JumatScheduleModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Jadwal Muadzin Jum'at")

        self.add_item(
            discord.ui.Label(
                id=0,
                text="Tanggal Mulai",
                component=discord.ui.TextInput(
                    placeholder="YYYY-MM-DD"
                )
            )
        )

        self.add_item(
            discord.ui.Label(
                id=1,
                text="List Anggota (pisahkan dengan enter)",
                component=discord.ui.TextInput(
                    placeholder="Nama Anggota 1\nNama Anggota 2\n...",
                    style=discord.TextStyle.paragraph
                )
            )
        )

    async def on_submit(self, interaction):
        tanggal_mulai = self.find_item(0).component.value
        list_anggota = self.find_item(1).component.value.splitlines()

        # Validasi format tanggal
        try:
            year, month, day = map(int, tanggal_mulai.split('-'))
            date_obj = datetime.date(year, month, day)
            if date_obj.weekday() != 4:  # 4 adalah indeks untuk hari Jum'at
                await interaction.response.send_message("Tanggal harus bertepatan dengan hari Jum'at", ephemeral=True)
                return
        except ValueError:
            await interaction.response.send_message("Tanggal harus menggunakan format YYYY-MM-DD", ephemeral=True)
            return

        for anggota in list_anggota:
            id_petugas = {
                anggota["nama"].lower(): i 
                for i, anggota in enumerate(jadwal.anggota)
            }
        
            new_pic = anggota.lower()
        
            if new_pic not in id_petugas:
                new_pic = "-"
        
            jadwal.jadwal_jumat[str(date_obj)] = id_petugas[new_pic]
            date_obj += timedelta(days=7)  # Tambahkan 7 hari untuk jadwal berikutnya

        await save_json("src/data/jadwal_jumat.json", jadwal.jadwal_jumat)
        await interaction.response.send_message("Berhasil menyimpan jadwal Muadzin Jum'at", ephemeral=True)