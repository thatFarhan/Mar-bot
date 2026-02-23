import discord
from data.loader import jadwal
from events.daily_schedule import build_schedule_and_tags
from global_vars import global_vars

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
            schedule_and_tags=build_schedule_and_tags(tempat, day_name, False)
            embeds.append(schedule_and_tags[0])

        await interaction.response.edit_message(content=f"# 💫 Jadwal hari {day_name}", embeds=embeds, view=DaySelectorView())

class DaySelectorView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(DaySelector())