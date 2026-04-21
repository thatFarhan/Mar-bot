import discord
from repository.loader import jadwal, save_presence
from repository.updater import update_to_confirm
from events.update_schedule_message import update_daily_schedule

class ConfirmModal(discord.ui.Modal):
    def __init__(self, select_options: list):
        super().__init__(title="Konfirmasi Jadwal")
        self.select_options = select_options

        jadwal_select = discord.ui.Select(
            placeholder="Pilih jadwal",
            options=select_options,
            max_values=len(select_options)
        )

        self.add_item(
            discord.ui.Label(
                id=0,
                text="Pilih jadwal",
                component=jadwal_select
            )
        )

    async def on_submit(self, interaction):
        for confirmed_jadwal in self.find_item(0).component.values:
            detail_jadwal = confirmed_jadwal.split("_")
            tempat = detail_jadwal[0]
            sholat = detail_jadwal[1]
            tugas = detail_jadwal[2]

            update_to_confirm(tugas, sholat, tempat)

        await save_presence(jadwal.jadwal_hariini)
        await interaction.response.send_message("Berhasil mengonfirmasi jadwal yang telah di pilih", ephemeral=True)
        await update_daily_schedule()