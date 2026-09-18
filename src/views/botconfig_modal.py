import discord
from repository.persistent_loader import persistent_vars, save_persistent

class BotConfigModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Konfigurasi Mar-bot")

        self.add_item(
            discord.ui.Label(
                id=0,
                text="💰 Auto-sell",
                description="Meminta pengganti secara otomatis setelah 10 menit tidak di konfirmasi",
                component=discord.ui.Checkbox(
                    default=persistent_vars["bot_config"]["autosell"]
                )
            )
        )

    async def on_submit(self, interaction: discord.Interaction):
        autosell = self.find_item(0).component.value
        persistent_vars["bot_config"]["autosell"] = autosell
        await save_persistent()
        await interaction.response.send_message("Berhasil mengubah konfigurasi Mar-bot", ephemeral=True);