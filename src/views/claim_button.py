import discord
import json
from data.loader import jadwal, save_presence
from data.updater import update_to_claim, update_to_confirm
from global_vars import global_vars

class ClaimButton(discord.ui.View):
    def __init__(self, tugas: str, sholat: str, tempat: str, embed_desc: str):
        super().__init__()
        self.tugas = tugas
        self.sholat = sholat
        self.tempat = tempat
        self.embed_desc = embed_desc

    @discord.ui.button(label="Klaim Jadwal", style=discord.ButtonStyle.primary)
    async def button_claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        tugas = self.tugas
        sholat = self.sholat
        tempat = self.tempat
        embed_desc = self.embed_desc

        petugas = jadwal.jadwal_hariini[tempat][sholat][tugas]
        detail_petugas = jadwal.anggota[petugas['id_anggota']]

        if detail_petugas['uid'] == interaction.user.id:
            update_to_confirm(tugas, sholat, tempat)
            nama_pengklaim = detail_petugas['nama']
        else:
            for id in range(1, len(jadwal.anggota)):
                if interaction.user.id == jadwal.anggota[id]['uid']:
                    nama_pengklaim = jadwal.anggota[id]['nama']
                    update_to_claim(tugas, sholat, tempat, id)
                    break
            # for else = will run when for is completed without break
            else:
                await interaction.response.send_message("Akun antum belum teregistrasi sebagai akun anggota", ephemeral=True)
                return

        save_presence(jadwal.jadwal_hariini)

        embed = discord.Embed(
            title="Detail Jadwal",
            color=discord.Color.green(),
            description=embed_desc
        )
        content=f"**✅ Jadwal telah diklaim oleh {nama_pengklaim} ✅**"

        global_vars.notification_ids.pop(f"{tugas}_{sholat}_{tempat}", None)
        
        await interaction.response.edit_message(content=content, embed=embed, view=None)