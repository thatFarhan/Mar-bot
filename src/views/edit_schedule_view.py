import discord
from data.loader import jadwal, save_json
from views.schedule_embed_builder import build_schedule

class DaySelector(discord.ui.Select):
    def __init__(self, sholat_chosen: str, tempat_chosen: str):
        self.sholat_chosen = sholat_chosen
        self.tempat_chosen = tempat_chosen

        day_options=[]
        for day in ("Senin", "Selasa", "Rabu", "Kamis", "Jum'at", "Sabtu", "Ahad"):
            day_options.append(discord.SelectOption(label=day))

        super().__init__(placeholder="Pilih hari", options=day_options)

    async def callback(self, interaction: discord.Interaction):
        day_name = self.values[0]
        if self.tempat_chosen not in jadwal.jadwal_rawatib[day_name]:
            self.tempat_chosen = "msu"

        if self.sholat_chosen not in jadwal.jadwal_rawatib[day_name][self.tempat_chosen]:
            self.sholat_chosen = "subuh"

        await edit_schedule_message(interaction, day_name=day_name, sholat_chosen=self.sholat_chosen, tempat_chosen=self.tempat_chosen)

class ClusterSelector(discord.ui.Select):
    def __init__(self, day_name: str):
        self.day_name = day_name

        cluster_options=[]
        for tempat in jadwal.jadwal_rawatib[self.day_name]:
            for sholat in jadwal.jadwal_rawatib[self.day_name][tempat]:
                cluster_options.append(discord.SelectOption(label=f"{tempat.upper()} / {sholat.capitalize()}", value=f"{tempat}/{sholat}"))

        super().__init__(placeholder="Pilih cluster", options=cluster_options)

    async def callback(self, interaction: discord.Interaction):
        cluster_chosen = self.values[0].split("/")
        new_tempat = cluster_chosen[0]
        new_sholat = cluster_chosen[1]
        await edit_schedule_message(interaction, day_name=self.day_name, sholat_chosen=new_sholat, tempat_chosen=new_tempat)

class MemberSelector(discord.ui.Select):
    def __init__(self, day_name: str, sholat_chosen: str, tempat_chosen: str):
        self.day_name = day_name
        self.sholat_chosen = sholat_chosen
        self.tempat_chosen = tempat_chosen

        minmax_values = 0
        for tugas in jadwal.jadwal_rawatib[f'{day_name}'][tempat_chosen][sholat_chosen]:
            minmax_values += 1

        member_options=[]
        for i in range(1, len(jadwal.anggota)):
            if jadwal.anggota[i]['nama'] != "":
                member_options.append(discord.SelectOption(label=jadwal.anggota[i]['nama'], value=i))

        super().__init__(placeholder=f"Pilih {minmax_values} anggota", options=member_options, min_values=minmax_values, max_values=minmax_values)

    async def callback(self, interaction: discord.Interaction):
        i = 0
        for tugas in dict(jadwal.jadwal_rawatib[f'{self.day_name}'][self.tempat_chosen][self.sholat_chosen]):
            jadwal.jadwal_rawatib[f'{self.day_name}'][self.tempat_chosen][self.sholat_chosen][tugas]['id_anggota'] = int(self.values[i])
            i += 1

        save_json("src/data/jadwal_rawatib.json", jadwal.jadwal_rawatib)
        await edit_schedule_message(interaction, day_name=self.day_name, sholat_chosen=self.sholat_chosen, tempat_chosen=self.tempat_chosen)

async def edit_schedule_message(interaction: discord.Interaction, day_name: str, sholat_chosen: str, tempat_chosen: str):
    embeds=[]
    for tempat in jadwal.jadwal_rawatib[day_name]:
        embeds.append(build_schedule(tempat, day_name, sholat_chosen, tempat_chosen))

    content=f"# `📝 Edit jadwal hari {day_name}`"
    await interaction.response.edit_message(content=content, embeds=embeds, view=EditScheduleView(day_name, sholat_chosen, tempat_chosen))

class EditScheduleView(discord.ui.View):
    def __init__(self, day_name: str = "Senin", sholat_chosen: str = "subuh", tempat_chosen: str = "msu"):
        super().__init__()
        self.day_name = day_name
        self.sholat_chosen = sholat_chosen
        self.tempat_chosen = tempat_chosen

        self.add_item(DaySelector(self.sholat_chosen, self.tempat_chosen))
        self.add_item(ClusterSelector(self.day_name))
        self.add_item(MemberSelector(self.day_name, self.sholat_chosen, self.tempat_chosen))