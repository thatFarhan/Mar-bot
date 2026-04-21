import discord
from repository.loader import jadwal, save_json
from builders.edit_schedule_builder import build_schedule

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

class EditButton(discord.ui.Button):
    def __init__(self, day_name: str, sholat_chosen: str, tempat_chosen: str):
        self.day_name = day_name
        self.sholat_chosen = sholat_chosen
        self.tempat_chosen = tempat_chosen

        super().__init__(label="Edit cluster", style=discord.ButtonStyle.primary)

    async def callback(self, interaction):
        await interaction.response.send_modal(EditModal(self.day_name, self.sholat_chosen, self.tempat_chosen))

class EditModal(discord.ui.Modal):
    def __init__(self, day_name: str, sholat_chosen: str, tempat_chosen: str):
        self.day_name = day_name
        self.sholat_chosen = sholat_chosen
        self.tempat_chosen = tempat_chosen

        super().__init__(title=f"{day_name} {sholat_chosen.capitalize()} {tempat_chosen.upper()}")

        for i, tugas in enumerate(jadwal.jadwal_rawatib[day_name][tempat_chosen][sholat_chosen]):
            petugas = jadwal.jadwal_rawatib[day_name][tempat_chosen][sholat_chosen][tugas]
            detail_petugas = jadwal.anggota[petugas["id_anggota"]]
            self.add_item(
                discord.ui.Label(
                    text=tugas,
                    id=i,
                    component=discord.ui.TextInput(
                        required=False,
                        default=detail_petugas["nama"]
                    )
                )
            )

    async def on_submit(self, interaction: discord.Interaction):
        id_petugas = {
            anggota["nama"].lower(): i 
            for i, anggota in enumerate(jadwal.anggota)
        }
        
        for child in self.children:
            tugas = child.text

            new_pic = child.component.value.lower()

            if new_pic not in id_petugas:
                new_pic = "kosong"

            jadwal.jadwal_rawatib[f'{self.day_name}'][self.tempat_chosen][self.sholat_chosen][tugas]['id_anggota'] = id_petugas[new_pic]

        await save_json("src/data/jadwal_rawatib.json", jadwal.jadwal_rawatib)
        await edit_schedule_message(interaction, self.day_name, self.sholat_chosen, self.tempat_chosen)

async def edit_schedule_message(interaction: discord.Interaction, day_name: str, sholat_chosen: str, tempat_chosen: str):
    embeds=[]
    for tempat in jadwal.jadwal_rawatib[day_name]:
        embeds.append(build_schedule(tempat, day_name, sholat_chosen, tempat_chosen))

    content=f"# `📝 Edit jadwal hari {day_name}`"
    await interaction.response.edit_message(content=content, embeds=embeds, view=EditScheduleView(day_name, sholat_chosen, tempat_chosen))

class EditScheduleView(discord.ui.View):
    def __init__(self, day_name: str = "Senin", sholat_chosen: str = "subuh", tempat_chosen: str = "msu"):
        super().__init__(timeout=None)
        self.day_name = day_name
        self.sholat_chosen = sholat_chosen
        self.tempat_chosen = tempat_chosen

        self.add_item(DaySelector(self.sholat_chosen, self.tempat_chosen))
        self.add_item(ClusterSelector(self.day_name))
        self.add_item(EditButton(self.day_name, self.sholat_chosen, self.tempat_chosen))