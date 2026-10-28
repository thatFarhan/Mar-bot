import discord

from database.anggota import update_discord_uid, delete_anggota, update_to_remove_uid_using_id
from views.edit_member_modal import EditMemberModal

PREV, NEXT = "prev", "next"  # real name values are numeric IDs, so no collision


def paginate(rows):
    n = len(rows)
    if n <= 25:  # fits in one dropdown, no navigation needed
        return [rows]

    pages = [rows[:24]]          # first page: only "Next" is added, so 24 names
    i = 24
    while n - i > 24:            # more than a last page can hold, so a middle page is needed
        pages.append(rows[i:i + 23])  # middle page: both "Previous" and "Next", so 23 names
        i += 23
    pages.append(rows[i:])       # last page: only "Previous" is added, so up to 24 names
    return pages


class NameSelect(discord.ui.Select):
    def __init__(self, picker: "NamePicker"):
        self.picker = picker
        page, total = picker.page, len(picker.pages)

        options = []
        if page > 0:
            options.append(discord.SelectOption(
                label="Sebelumnya", emoji="◀️", description=f"Ke halaman {page}",  value=PREV))

        options += [
            discord.SelectOption(label=row["nama_lengkap"][:100], description=row["nama_panggilan"][:100], value=str(row["id_anggota"]))
            for row in picker.pages[page]
        ]

        if page < total - 1:
            options.append(discord.SelectOption(
                label="Selanjutnya", emoji="▶️", description=f"Ke halaman {page + 2}", value=NEXT))

        super().__init__(placeholder=f"Pilih nama (halaman {page + 1}/{total})" if total > 1 else "Pilih nama Anda",
                         options=options)

    async def callback(self, interaction: discord.Interaction):
        value = self.values[0]

        if value == PREV:
            self.picker.page -= 1
            self.picker.build()
            await interaction.response.edit_message(view=self.picker)
            return
        if value == NEXT:
            self.picker.page += 1
            self.picker.build()
            await interaction.response.edit_message(view=self.picker)
            return

        # A real name was chosen: ask for confirmation instead of saving right away
        id_anggota = int(value)
        nama_lengkap = next(option.label for option in self.options if option.value == value)
        nama_panggilan = next(option.description for option in self.options if option.value == value)

        if self.picker.followup_view:
            await interaction.response.edit_message(
                content=f"Anda memilih:\n**{nama_lengkap}**",
                view=self.picker.followup_view(self.picker, id_anggota, nama_lengkap, nama_panggilan),
            )
        else:
            await interaction.response.send_modal(EditMemberModal(id_anggota, nama_lengkap, nama_panggilan))


class NamePicker(discord.ui.View):
    def __init__(self, rows, followup_view = None):
        super().__init__()
        self.pages = paginate(rows)
        self.page = 0
        self.followup_view = followup_view
        self.build()

    def build(self):
        self.clear_items()  # rebuilding also resets the select's visible choice
        self.add_item(NameSelect(self))


class ConfirmRegisterView(discord.ui.View):
    def __init__(self, picker: NamePicker, id_anggota: int, nama_lengkap: str, nama_panggilan: str):
        super().__init__()
        self.picker = picker
        self.id_anggota = id_anggota
        self.nama_lengkap = nama_lengkap
        self.nama_panggilan = nama_panggilan

    @discord.ui.button(label="Ya, Benar", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        ok = await update_discord_uid(id_anggota = self.id_anggota, discord_uid = interaction.user.id)
        if ok:
            await interaction.response.edit_message(content=f"Berhasil registrasi atas nama **{self.nama_lengkap}**. Terima kasih 🙏", view=None)
            role = []
            role.append(discord.utils.get(interaction.guild.roles, name="Registered"))
            try:
                await interaction.user.edit(nick=self.nama_panggilan, roles=role)
            except Exception:
                return
        else:
            await interaction.response.edit_message(content=f"Maaf, nama ini sudah diambil orang lain.", view=None)
        
        self.stop()

    @discord.ui.button(label="Batal", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Go back to the same page of the dropdown
        self.picker.build()
        await interaction.response.edit_message(content="## 📝 Pendaftaran Anggota", view=self.picker)
        self.stop()

class ForceRegisterUserSelect(discord.ui.UserSelect):
    def __init__(self, id_anggota: int, nama_lengkap: str, nama_panggilan: str):
        super().__init__(placeholder="Pilih anggota server")
        self.id_anggota = id_anggota
        self.nama_lengkap = nama_lengkap
        self.nama_panggilan = nama_panggilan

    async def callback(self, interaction: discord.Interaction):
        ok = await update_discord_uid(id_anggota = self.id_anggota, discord_uid = self.values[0].id)
        if ok:
            await interaction.response.edit_message(content=f"Berhasil registrasi atas nama **{self.nama_lengkap}**. Terima kasih 🙏", view=None)
            role = []
            role.append(discord.utils.get(interaction.guild.roles, name="Registered"))
            try:
                await self.values[0].edit(nick=self.nama_panggilan, roles=role)
            except Exception:
                return
        else:
            await interaction.response.edit_message(content=f"Maaf, nama ini sudah diambil orang lain.", view=None)

class CancelButton(discord.ui.Button):
    def __init__(self, picker):
        self.picker = picker
        super().__init__(label="Batal", style=discord.ButtonStyle.red)

    async def callback(self, interaction):
        self.picker.build()
        await interaction.response.edit_message(content="## 📝 Force Pendaftaran Anggota", view=self.picker)

class ForceRegisterView(discord.ui.View):
    def __init__(self, picker: NamePicker, id_anggota, nama_lengkap, nama_panggilan):
        super().__init__()
        self.add_item(ForceRegisterUserSelect(id_anggota, nama_lengkap, nama_panggilan))
        self.add_item(CancelButton(picker))

class ConfirmDeletionView(discord.ui.View):
    def __init__(self, picker: NamePicker, id_anggota: int, nama_lengkap: str, nama_panggilan: str):
        super().__init__()
        self.picker = picker
        self.id_anggota = id_anggota
        self.nama_lengkap = nama_lengkap
        self.nama_panggilan = nama_panggilan

    @discord.ui.button(label="Ya, Hapus", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        ok = await delete_anggota(self.id_anggota)
        if ok:
            await interaction.response.edit_message(content=f"Berhasil menghapus **{self.nama_lengkap}**.", view=None)
        else:
            await interaction.response.edit_message(content=f"Gagal menghapus **{self.nama_lengkap}**.", view=None)
        
        self.stop()

    @discord.ui.button(label="Batal", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Go back to the same page of the dropdown
        self.picker.build()
        await interaction.response.edit_message(content="## 🗑️ Penghapusan Anggota", view=self.picker)
        self.stop()

class ConfirmUnregisterView(discord.ui.View):
    def __init__(self, picker: NamePicker, id_anggota: int, nama_lengkap: str, nama_panggilan: str):
        super().__init__()
        self.picker = picker
        self.id_anggota = id_anggota
        self.nama_lengkap = nama_lengkap
        self.nama_panggilan = nama_panggilan

    @discord.ui.button(label="Ya, Unregister", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        ok = await update_to_remove_uid_using_id(self.id_anggota)
        if ok:
            await interaction.response.edit_message(content=f"Berhasil membatalkan pendaftaran **{self.nama_lengkap}**.", view=None)
        else:
            await interaction.response.edit_message(content=f"Gagal membatalkan pendaftaran **{self.nama_lengkap}**.", view=None)
        
        self.stop()

    @discord.ui.button(label="Batal", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Go back to the same page of the dropdown
        self.picker.build()
        await interaction.response.edit_message(content="## 📝 Batalkan Pendaftaran Anggota", view=self.picker)
        self.stop()