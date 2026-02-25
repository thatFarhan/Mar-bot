import discord
from data.loader import jadwal
from global_vars import global_vars
from config import TEMPAT_TITLE, SHOLAT_TITLE

class DaySelector(discord.ui.Select):
    def __init__(self):
        options=[]
        for day in ("Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"):
            options.append(discord.SelectOption(label=day))

        super().__init__(placeholder="Pilih hari", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        day_name = self.values[0]
        embeds=[]
        for tempat in jadwal.jadwal_rawatib[day_name]:
            schedule=build_schedule(tempat, day_name)
            embeds.append(schedule)

        await interaction.response.edit_message(content=f"# 💫 Jadwal hari {day_name}", embeds=embeds, view=DaySelectorView())

class DaySelectorView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(DaySelector())

def build_schedule(tempat: str, system_day_name: str):
    schedule=discord.Embed(
            title=TEMPAT_TITLE[tempat],
            color=discord.Color.green()
        )

    for sholat in jadwal.jadwal_rawatib[system_day_name][tempat]:
        field_values=[]
        for tugas in jadwal.jadwal_rawatib[system_day_name][tempat][sholat]:
            id_anggota = jadwal.jadwal_rawatib[system_day_name][tempat][sholat][tugas]['id_anggota']
            anggota = jadwal.anggota[id_anggota]
            field_values.append(f"{tugas}: **{anggota['nama']}**")

        schedule.add_field(
            name=SHOLAT_TITLE[sholat],
            value="\n".join(field_values),
            inline=True
        )
    
    return schedule