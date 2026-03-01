import discord
from data.loader import jadwal
from builders.show_schedule_builder import build_schedule

class DaySelector(discord.ui.Select):
    def __init__(self):
        options=[]
        for day in ("Senin", "Selasa", "Rabu", "Kamis", "Jum'at", "Sabtu", "Ahad"):
            options.append(discord.SelectOption(label=day))

        super().__init__(placeholder="Pilih hari", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        day_name = self.values[0]
        embeds=[]
        for tempat in jadwal.jadwal_rawatib[day_name]:
            schedule=build_schedule(tempat, day_name)
            embeds.append(schedule)

        await interaction.response.edit_message(content=f"## 💫 Jadwal hari {day_name}", embeds=embeds, view=DaySelectorView())

class DaySelectorView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(DaySelector())