import discord
from config import bot
from server_config import GUILD_ID
from views.swap_request_modal import SwapRequestModal, SwapRequestWeekModal

@bot.tree.command(name="tukar", description="Merequest penukaran jadwal yang antum pilih di hari ini", guild=GUILD_ID)
async def swap(interaction: discord.Interaction):
    await swaprequestmodal(interaction)

@bot.tree.command(name="tukarpekan", description="Merequest penukaran jadwal yang antum pilih di pekan ini", guild=GUILD_ID)
async def swap(interaction: discord.Interaction):
    await swaprequestweekmodal(interaction)

async def swaprequestmodal(interaction: discord.Interaction):
    try:
        await interaction.response.send_modal(SwapRequestModal(interaction.user.id))
    except discord.errors.HTTPException:
        await interaction.response.send_message(content="Tidak ada jadwal yang bisa direquest penukaran", ephemeral=True)

async def swaprequestweekmodal(interaction: discord.Interaction):
    try:
        await interaction.response.send_modal(SwapRequestWeekModal(interaction.user.id))
    except discord.errors.HTTPException:
        await interaction.response.send_message(content="Tidak ada jadwal yang bisa direquest penukaran", ephemeral=True)