import discord

from events.reminder import set_reminders

from database.discord_server import update_bot_config

class BotConfigModal(discord.ui.Modal):
    def __init__(self, bot_config):
        super().__init__(title="Konfigurasi Mar-bot")
        reminder_send_time = bot_config["reminder_send_time"]
        auto_sell_time = bot_config["auto_sell_time"]

        self.add_item(
            discord.ui.Label(
                id=0,
                text="⏰ Waktu sebelum reminder dikirim",
                description="Berapa menit sebelum waktu adzan, reminder sholat akan dikirim.",
                component=discord.ui.TextInput(
                    default=reminder_send_time if reminder_send_time else "0",
                    placeholder="1-60, 0 berarti non-aktif"
                )
            )
        )

        self.add_item(
            discord.ui.Label(
                id=1,
                text="👥 Waktu meminta pengganti otomatis",
                description="Berapa menit setelah reminder dikirim, jadwal akan diminta pengganti secara otomatis. 0 -> off",
                component=discord.ui.TextInput(
                    default=auto_sell_time if auto_sell_time else "0",
                    placeholder="1-[nilai diatas], 0 berarti non-aktif"
                )
            )
        )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            reminder_send_time = int(self.find_item(0).component.value)
            auto_sell_time = int(self.find_item(1).component.value)
        except ValueError:
            await interaction.response.send_message("Input tidak valid. Silahkan coba lagi", ephemeral=True);
            return

        if reminder_send_time < 0 or reminder_send_time > 60 or auto_sell_time < 0 or auto_sell_time > reminder_send_time:
            await interaction.response.send_message("Input tidak valid. Silahkan coba lagi", ephemeral=True);
            return
        
        await update_bot_config(interaction.guild_id, reminder_send_time, auto_sell_time)

        if not reminder_send_time:
            reminder_send_time = "Non-aktif"
        else:
            reminder_send_time = str(reminder_send_time) + " menit"

        if not auto_sell_time:
            auto_sell_time = "Non-aktif"
        else:
            auto_sell_time = str(auto_sell_time) + " menit"

        await interaction.response.send_message(
            f"Berhasil mengubah konfigurasi Mar-bot\n\n**Waktu sebelum reminder dikirim:** {reminder_send_time}\n**Waktu meminta pengganti otomatis:** {auto_sell_time}", 
            ephemeral=True
        );
        await set_reminders(interaction.guild_id)
        