import discord
from data.loader import jadwal, save_presence, save_reason
from data.persistent_loader import persistent_vars
from data.updater import update_to_sell
from events.on_sale_notification import on_sale_noti
from events.update_schedule_message import update_daily_schedule

class SellModal(discord.ui.Modal):
    def __init__(self, uid: int):
        super().__init__(title="Request Pengganti")
        self.uid = uid

        select_options = []
        for tempat in jadwal.jadwal_hariini:
            for sholat in jadwal.jadwal_hariini[tempat]:
                for tugas in jadwal.jadwal_hariini[tempat][sholat]:
                    if tugas == 'Hadits': continue
                    
                    petugas = jadwal.jadwal_hariini[tempat][sholat][tugas]
                    detail_petugas = jadwal.anggota[petugas['id_anggota']]
                    detail_pengganti = jadwal.anggota[petugas['id_sub']]
                        
                    if petugas["need_sub"]:
                        continue
                        
                    if detail_petugas['uid'] != uid and detail_pengganti['uid'] != uid:
                        continue

                    if detail_petugas['uid'] == uid and detail_pengganti['uid'] != 0:
                        continue

                    if detail_petugas['uid'] == uid:
                        global id_requestor
                        id_requestor = petugas['id_anggota']
                    elif detail_pengganti['uid'] == uid:
                        id_requestor = petugas['id_sub']

                    select_options.append(discord.SelectOption(label=f"{tugas.capitalize()} Sholat {sholat.capitalize()} di {tempat.upper()}", value=f"{tempat}_{sholat}_{tugas}"))

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

        self.add_item(
            discord.ui.Label(
                id=1,
                text="Alasan",
                component=discord.ui.TextInput(
                    style=discord.TextStyle.paragraph
                )
            )
        )
    
    async def on_submit(self, interaction):
        alasan = self.find_item(1).component.value

        if jadwal.alasan_absen_hariini is None:
            jadwal.alasan_absen_hariini = {}

        jadwal.alasan_absen_hariini[str(id_requestor)] = alasan

        for sold_jadwal in self.find_item(0).component.values:
            detail_jadwal = sold_jadwal.split("_")
            tempat = detail_jadwal[0]
            sholat = detail_jadwal[1]
            tugas = detail_jadwal[2]

            update_to_sell(tugas, sholat, tempat)
            emergency = persistent_vars["reminder_sent"][sholat]
            await on_sale_noti(tugas, sholat, tempat, emergency=emergency, alasan=alasan)

        await save_reason()
        await save_presence(jadwal.jadwal_hariini)
        await interaction.response.send_message("Berhasil meminta pengganti untuk jadwal yang telah di pilih", ephemeral=True)
        await update_daily_schedule()