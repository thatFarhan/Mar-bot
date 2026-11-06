import discord

from models.Schedule import Schedule

def build_swap_embeds(sending_schedule: dict, receiving_schedule: dict):
    sending_schedule_obj = Schedule(sending_schedule)
    receiving_schedule_obj = Schedule(receiving_schedule)

    embeds = []
    
    embed_sending=discord.Embed(
        title="Jadwal yang Akan Diserahkan ↗️",
        description=sending_schedule_obj.get_desc()
    )
    embeds.append(embed_sending)
    
    embed_receiving=discord.Embed(
        title="Jadwal yang Akan Diterima ↙️",
        description=receiving_schedule_obj.get_desc()
    )
    embeds.append(embed_receiving)

    return embeds