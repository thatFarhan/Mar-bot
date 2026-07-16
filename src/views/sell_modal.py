import discord
from datetime import timedelta
from config import NAMA_HARI
from mission_util import to_datetime
from global_vars import global_vars
from repository.loader import jadwal, save_presence, save_reason
from repository.persistent_loader import persistent_vars
from repository.updater import update_to_sell, update_to_sell_week
from events.on_sale_notification import on_sale_noti
from events.update_schedule_message import update_daily_schedule

class SellModal(discord.ui.Modal):
    def __init__(self, uid: int):
        super().__init__(title="Request Pengganti Hari Ini")
        self.uid = uid

        select_options = []
        jadwal_harian = jadwal.presensi_rawatib[global_vars.system_date]
        for tempat in jadwal_harian:
            for sholat in jadwal_harian[tempat]:
                for tugas in jadwal_harian[tempat][sholat]:
                    if tugas == 'Hadits': continue
                    
                    petugas = jadwal_harian[tempat][sholat][tugas]
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
        alasan_dict = {str(id_requestor): alasan}

        jadwal.alasan_absen[global_vars.system_date] = alasan_dict

        for sold_jadwal in self.find_item(0).component.values:
            detail_jadwal = sold_jadwal.split("_")
            tempat = detail_jadwal[0]
            sholat = detail_jadwal[1]
            tugas = detail_jadwal[2]

            update_to_sell(tugas, sholat, tempat)
            emergency = persistent_vars["reminder_sent"][sholat]
            await save_reason()
            await on_sale_noti(tugas, sholat, tempat, emergency=emergency, id_requestor=id_requestor)

        await save_presence(jadwal.presensi_rawatib[global_vars.system_date])
        await interaction.response.send_message("Berhasil meminta pengganti untuk jadwal yang telah di pilih", ephemeral=True)
        await update_daily_schedule()

class SellWeekModal(discord.ui.Modal):
    def __init__(self, uid: int):
        super().__init__(title="Request Pengganti Pekan Ini")
        self.uid = uid

        select_options = []
        for i in range(7):
            iterated_date = to_datetime(global_vars.system_date) + timedelta(i)
            day_name = NAMA_HARI[iterated_date.weekday()]
            str_iterated_date = str(iterated_date.date())
            jadwal_harian = jadwal.presensi_rawatib[str_iterated_date]
            for tempat in jadwal_harian:
                for sholat in jadwal_harian[tempat]:
                    for tugas in jadwal_harian[tempat][sholat]:
                        if tugas == 'Hadits': continue
                        
                        petugas = jadwal_harian[tempat][sholat][tugas]
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

                        select_options.append(discord.SelectOption(label=f"({day_name}) {tugas.capitalize()} Sholat {sholat.capitalize()} di {tempat.upper()}", value=f"{str_iterated_date}_{tempat}_{sholat}_{tugas}"))

        select_options = select_options[:25]
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
        alasan_dict = {str(id_requestor): alasan}

        sold_dates = set()

        for sold_jadwal in self.find_item(0).component.values:
            detail_jadwal = sold_jadwal.split("_")
            tanggal = detail_jadwal[0]
            tempat = detail_jadwal[1]
            sholat = detail_jadwal[2]
            tugas = detail_jadwal[3]

            update_to_sell_week(tanggal, tugas, sholat, tempat)
            jadwal.alasan_absen[tanggal] = alasan_dict
            sold_dates.add(tanggal)

            if tanggal == global_vars.system_date:
                emergency = persistent_vars["reminder_sent"][sholat]
            else:
                emergency = False
                
            await save_reason()
            await on_sale_noti(tugas, sholat, tempat, emergency=emergency, tanggal=tanggal, id_requestor=id_requestor)

        for date in sold_dates:
            await save_presence(jadwal.presensi_rawatib[date])
        await interaction.response.send_message("Berhasil meminta pengganti untuk jadwal yang telah di pilih", ephemeral=True)
        await update_daily_schedule()