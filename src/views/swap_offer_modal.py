import discord
from datetime import timedelta
from config import NAMA_HARI
from mission_util import to_datetime
from global_vars import global_vars
from repository.loader import jadwal
from repository.persistent_loader import persistent_vars
from events.update_schedule_message import update_daily_schedule
from events.swap_offer_notification import swap_offer_noti
from models.Schedule import Schedule

class SwapOfferModal(discord.ui.Modal):
    def __init__(self, uid: int, requested_schedule: Schedule):
        super().__init__(title="Tawarkan Penukaran Jadwal")
        self.uid = uid
        self.requested_schedule = requested_schedule

        select_options = []
        for i in range(7):
            iterated_date = to_datetime(global_vars.system_date) + timedelta(i)
            day_name = NAMA_HARI[iterated_date.weekday()]
            str_iterated_date = str(iterated_date.date())
            jadwal_harian = jadwal.presensi_rawatib[str_iterated_date]
            for tempat in jadwal_harian:
                for sholat in jadwal_harian[tempat]:
                    for tugas in jadwal_harian[tempat][sholat]:
                        if tugas == 'Hadits' or tugas == 'Badal': continue

                        key = f"{requested_schedule.get_key()}_{str_iterated_date}_{tugas}_{sholat}_{tempat}"
                        if key in persistent_vars["swap_notification_ids"]: continue
                        
                        petugas = jadwal_harian[tempat][sholat][tugas]
                        detail_petugas = jadwal.anggota[petugas['id_anggota']]
                        detail_pengganti = jadwal.anggota[petugas['id_sub']]
                            
                        if detail_petugas['uid'] != uid and detail_pengganti['uid'] != uid:
                            continue

                        if detail_petugas['uid'] == uid and detail_pengganti['uid'] != 0:
                            continue

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
    
    async def on_submit(self, interaction):
        sold_jadwal = self.find_item(0).component.values
        detail_jadwal = sold_jadwal[0].split("_")
        tanggal = detail_jadwal[0]
        tempat = detail_jadwal[1]
        sholat = detail_jadwal[2]
        tugas = detail_jadwal[3]
        offered_schedule = Schedule(tanggal, tugas, sholat, tempat)
        
        await swap_offer_noti(interaction, self.requested_schedule, offered_schedule)
        await update_daily_schedule()