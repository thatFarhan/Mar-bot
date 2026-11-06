import discord
from config import NAMA_HARI
from mission_util import to_indo_date_format
from events.update_schedule_message import update_daily_schedule
from events.swap_offer_notification import swap_offer_noti

from database.presensi import update_to_confirm_by_ids
from events.purge_transaction import purge_related_notifications

class TakeRespModal(discord.ui.Modal):
    def __init__(self, schedules: list, requested_schedule: dict = None):
        if requested_schedule:
            title = "Tawarkan Penukaran Jadwal"
        else:
            title = "Konfirmasi Jadwal"
        super().__init__(title=title)
        self.schedules = schedules
        self.requested_schedule = requested_schedule

        select_options = []

        for schedule in schedules:
            id_presensi = schedule["id_presensi"]
            tugas = schedule["tugas"]
            sholat = schedule["sholat"]
            nama_masjid = schedule["nama_masjid"]
            tanggal = schedule["tanggal"]
            day_name = NAMA_HARI[tanggal.weekday()]
            
            day_label = f"({day_name}, {to_indo_date_format(tanggal)}) " if self.requested_schedule else ""
        
            select_options.append(
                discord.SelectOption(
                    label=f"{day_label}{tugas} Sholat {sholat}", description=nama_masjid, value=id_presensi
                )
            )

        jadwal_select = discord.ui.Select(
            placeholder="Pilih jadwal",
            options=select_options[:25],
            max_values=len(select_options) if not requested_schedule else 1
        )

        self.add_item(
            discord.ui.Label(
                id=0,
                text="Pilih jadwal",
                component=jadwal_select
            )
        )

    async def on_submit(self, interaction):
        chosen_schedules = []
        for id_presensi in self.find_item(0).component.values:
            chosen_schedules.append(id_presensi)

        if not self.requested_schedule:
            await update_to_confirm_by_ids(chosen_schedules)
            await interaction.response.send_message("Berhasil mengonfirmasi jadwal yang telah dipilih", ephemeral=True)
            await update_daily_schedule(interaction.guild_id)
            for id_presensi in chosen_schedules:
                await purge_related_notifications(id_presensi)
        else:
            await swap_offer_noti(interaction, self.requested_schedule, chosen_schedules[0])