import discord
from events.update_schedule_message import update_daily_schedule

from database.presensi import update_to_claim_by_ids
from database.anggota import get_anggota_by_guild_and_uid
from events.purge_transaction import purge_related_notifications

class ForceClaimModal(discord.ui.Modal):
    def __init__(self, schedules: list):
        super().__init__(title="Force Klaim Jadwal")
        self.schedules = schedules

        split_schedules = []
        SELECT_MAX_OPTIONS = 25
        for i in range(0, len(schedules), SELECT_MAX_OPTIONS):
            split_schedules.append(schedules[i:i + SELECT_MAX_OPTIONS])


        for i in range(4):
            if len(split_schedules) <= i: break

            select_options = []

            for schedule in split_schedules[i]:
                id_presensi = schedule["id_presensi"]
                tugas = schedule["tugas"]
                sholat = schedule["sholat"]
                nama_masjid = schedule["nama_masjid"]
                nama_reg = schedule["nama_reg"]
                nama_pic = schedule["nama_pic"]
                nama_petugas: str = nama_pic if nama_pic is not None else nama_reg
            
                select_options.append(
                    discord.SelectOption(
                        label=f"({nama_petugas}) {tugas} Sholat {sholat}", description=nama_masjid, value=id_presensi
                    )
                )

            jadwal_select = discord.ui.Select(
                placeholder="Pilih jadwal",
                options=select_options,
                max_values=len(select_options),
                required=False
            )

            self.add_item(
                discord.ui.Label(
                    id=i,
                    text=f"📅 Pilih jadwal ({i + 1})",
                    component=jadwal_select
                )
            )

        self.add_item(
            discord.ui.Label(
                id=4,
                text="👥 Pilih pengganti",
                component=discord.ui.UserSelect(
                    placeholder="Pilih anggota",
                    required=True
                )
            )
        )

    async def on_submit(self, interaction):
        chosen_schedules = []

        for i in range(4):
            item = self.find_item(i)
            if not item:
                break
            for id_presensi in item.component.values:
                chosen_schedules.append(id_presensi)

        uid_pic = self.find_item(4).component.values[0].id

        id_anggota = await get_anggota_by_guild_and_uid(interaction.guild_id, uid_pic)
        
        if not id_anggota:
            await interaction.response.send_message("Akun belum terdaftar sebagai anggota", ephemeral=True)
            return

        if not chosen_schedules:
            await interaction.response.send_message("Tidak ada jadwal yang terpilih.", ephemeral=True)
            return

        await update_to_claim_by_ids(chosen_schedules, id_anggota)
        await interaction.response.send_message("Berhasil mengklaim jadwal untuk anggota yang dipilih.", ephemeral=True)
        await update_daily_schedule(interaction.guild_id)
        for id_presensi in chosen_schedules:
            await purge_related_notifications(id_presensi)