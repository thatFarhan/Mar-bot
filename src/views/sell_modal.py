import discord
from config import NAMA_HARI
from mission_util import to_indo_date_format
from events.on_sale_notification import on_sale_noti
from events.update_schedule_message import update_daily_schedule

from database.presensi import update_to_request_sub_by_ids, get_schedule_by_id, update_to_request_swap_by_ids
from database.alasan_absen import insert_many_alasan_absen
from database.anggota import get_anggota_by_guild_and_uid

class RequestModal(discord.ui.Modal):
    def __init__(self, schedules, is_sub, is_week):
        title = "Minta "
        if is_sub:
            title += "Pengganti "
        else:
            title += "Pertukaran "

        if is_week:
            title += "Pekan Ini"
        else:
            title += "Hari Ini"
        super().__init__(title=title)
        self.schedules = schedules
        self.is_sub = is_sub
        self.is_week = is_week

        select_options = []

        for schedule in schedules:
            id_presensi = schedule["id_presensi"]
            tugas = schedule["tugas"]
            sholat = schedule["sholat"]
            nama_masjid = schedule["nama_masjid"]
            tanggal = schedule["tanggal"]
            day_name = NAMA_HARI[tanggal.weekday()]

            day_label = f"({day_name}, {to_indo_date_format(tanggal)}) " if self.is_week else ""

            select_options.append(
                discord.SelectOption(
                    label=f"{day_label}{tugas} Sholat {sholat}", description=nama_masjid, value=id_presensi
                )
            )

        jadwal_select = discord.ui.Select(
            placeholder="Pilih jadwal",
            options=select_options[:25],
            max_values=len(select_options)
        )

        self.add_item(
            discord.ui.Label(
                id=0,
                text="Pilih jadwal",
                component=jadwal_select
            )
        )

        self.add_item(
            discord.ui.Label(
                id=1,
                text="Alasan",
                component=discord.ui.TextInput(
                    style=discord.TextStyle.paragraph
                )
            )
        )

        self.add_item(
            discord.ui.Label(
                id=2,
                text="Mention anggota (opsional)",
                component=discord.ui.UserSelect(
                    placeholder="Pilih anggota",
                    max_values=25,
                    required=False
                )
            )
        )
    
    async def on_submit(self, interaction):
        await interaction.response.defer()
        alasan = self.find_item(1).component.value

        requested_schedules = []
        absent_reasons = []
        id_anggota = await get_anggota_by_guild_and_uid(interaction.guild_id, interaction.user.id)

        for id_presensi in self.find_item(0).component.values:
            requested_schedules.append(id_presensi)
            schedule = await get_schedule_by_id(id_presensi)
            absent_reasons.append((id_presensi, id_anggota, alasan))
            await on_sale_noti(interaction.guild_id, schedule, alasan, self.find_item(2).component.values, is_sub=self.is_sub)


        if self.is_sub:
            await update_to_request_sub_by_ids(requested_schedules)
            content = "Berhasil meminta pengganti untuk jadwal yang telah dipilih"
        else:
            await update_to_request_swap_by_ids(requested_schedules)
            content = "Berhasil meminta pertukaran untuk jadwal yang telah dipilih"

        await insert_many_alasan_absen(absent_reasons)
        await interaction.followup.send(content, ephemeral=True)
        await update_daily_schedule(interaction.guild_id)