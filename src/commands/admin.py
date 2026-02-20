from discord import app_commands
from config import bot, GUILD_ID, TugasEnum, SholatEnum, TempatEnum, SUB_REQUESTS_CHANNEL
from events.daily_schedule import send_daily_schedule, write_todays_pic
from global_vars import scheduler, global_vars
from events.reminder import send_reminder, reset_reminder_sent
from data.loader import jadwal, save_presence
from data.updater import update_to_sell, update_to_confirm, update_to_claim
from events.on_sale_notification import on_sale_noti
import discord

@bot.tree.command(name="dailyschedule", description="[ADMIN] Mengirim ulang jadwal harian", guild=GUILD_ID)
@app_commands.checks.has_role("Marbot Mar-bot")
async def dailyschedule(interaction: discord.Interaction):
    await interaction.response.defer()
    await send_daily_schedule(interaction.followup)

@bot.tree.command(name="rewritejson", description="[ADMIN] Menulis ulang file json jadwal hari ini", guild=GUILD_ID)
@app_commands.checks.has_role("Marbot Mar-bot")
async def rewritejson(interaction: discord.Interaction):
    write_todays_pic()
    await interaction.response.send_message("presensi_rawatib.json telah ditulis ulang", ephemeral=True)

@bot.tree.command(name="testreminder", description="[ADMIN] Tes reminder",guild=GUILD_ID)
@app_commands.checks.has_role("Marbot Mar-bot")
async def testreminder(interaction: discord.Interaction):
    await interaction.response.send_message(content="test", ephemeral=True)
    await send_reminder('maghrib')
    for schedule in scheduler.get_jobs():
        print(schedule)

@bot.tree.command(name="resetremindersent", description="[ADMIN] Reset tracker reminder yang telah dikirim", guild=GUILD_ID)
@app_commands.checks.has_role("Marbot Mar-bot")
async def resetremindersent(interaction: discord.Interaction):
    reset_reminder_sent()
    await interaction.response.send_message(content="Tracker reminder telah di reset", ephemeral=True)

@bot.tree.command(name="forcesell", description="[ADMIN] Merequest pengganti untuk suatu jadwal", guild=GUILD_ID)
@app_commands.checks.has_role("Marbot Mar-bot")
async def forcesell(interaction: discord.Interaction, tugas: TugasEnum, sholat: SholatEnum, tempat: TempatEnum):
    if sholat.value not in jadwal.jadwal_hariini[tempat.value] or tugas.value not in jadwal.jadwal_hariini[tempat.value][sholat.value]:
        await interaction.response.send_message(f"Jadwal {tugas.name} Sholat {sholat.name} di {tempat.name} tidak ada", ephemeral=True)
        return

    update_to_sell(tugas, sholat, tempat)
    emergency = global_vars.reminder_sent[sholat.value]
    await on_sale_noti(tugas.value, sholat.value, tempat.value, emergency=emergency)
    save_presence(jadwal.jadwal_hariini)

    await interaction.response.send_message(f"Berhasil meminta pengganti untuk {tugas.name} Sholat {sholat.name} di {tempat.name}", ephemeral=True)

@bot.tree.command(name="forceconfirm", description="[ADMIN] Mengonfirmasi presensi suatu jadwal", guild=GUILD_ID)
@app_commands.checks.has_role("Marbot Mar-bot")
async def forceconfirm(interaction: discord.Interaction, tugas: TugasEnum, sholat: SholatEnum, tempat: TempatEnum):
    if sholat.value not in jadwal.jadwal_hariini[tempat.value] or tugas.value not in jadwal.jadwal_hariini[tempat.value][sholat.value]:
        await interaction.response.send_message(f"Jadwal {tugas.name} Sholat {sholat.name} di {tempat.name} tidak ada", ephemeral=True)
        return
    
    update_to_confirm(tugas.value, sholat.value, tempat.value)
    save_presence(jadwal.jadwal_hariini)

    await interaction.response.send_message(f"Berhasil mengonfirmasi jadwal {tugas.name} Sholat {sholat.name} di {tempat.name}, Syukran Jazilan 🙏", ephemeral=True)

@bot.tree.command(name="forceclaim", description="[ADMIN] Mengklaim suatu jadwal yang perlu pengganti untuk seseorang", guild=GUILD_ID)
@app_commands.checks.has_role("Marbot Mar-bot")
async def forceclaim(interaction: discord.Interaction, tugas: TugasEnum, sholat: SholatEnum, tempat: TempatEnum, pengganti: discord.Member):
    await interaction.response.defer(ephemeral=True)

    if sholat.value not in jadwal.jadwal_hariini[tempat.value] or tugas.value not in jadwal.jadwal_hariini[tempat.value][sholat.value]:
        await interaction.response.send_message(f"Jadwal {tugas.name} Sholat {sholat.name} di {tempat.name} tidak ada", ephemeral=True)
        return

    petugas = jadwal.jadwal_hariini[tempat.value][sholat.value][tugas.value]
    detail_petugas = jadwal.anggota[petugas['id_anggota']]

    if petugas["confirmed"]:
        await interaction.followup.send("Jadwal tersebut sudah diklaim")
        return
    
    if not petugas["need_sub"]:
        await interaction.followup.send("Jadwal tersebut belum di-sell")
        return

    if detail_petugas['uid'] == pengganti.id:
        update_to_confirm(tugas.value, sholat.value, tempat.value)
        nama_pengklaim = detail_petugas['nama']
    else:
        for id in range(1, len(jadwal.anggota)):
            if pengganti.id == jadwal.anggota[id]['uid']:
                nama_pengklaim = jadwal.anggota[id]['nama']
                update_to_claim(tugas, sholat, tempat, id)
                break
        # for else = will run when for is completed without break
        else:
            await interaction.followup.send("Akun tercantum belum teregistrasi sebagai akun anggota", ephemeral=True)
            return

    save_presence(jadwal.jadwal_hariini)

    key = f"{tugas.value}_{sholat.value}_{tempat.value}"

    if key not in global_vars.notification_ids:
        await interaction.followup.send(f"Berhasil mengklaim untuk {nama_pengklaim}, namun notifikasi request pengganti tidak ditemukan")
        return
    
    noti_id = global_vars.notification_ids[key]

    channel = bot.get_channel(SUB_REQUESTS_CHANNEL)
    message = await channel.fetch_message(noti_id)

    nama_petugas_default = jadwal.anggota[jadwal.jadwal_hariini[tempat.value][sholat.value][tugas.value]['id_anggota']]['nama']
    waktu_sholat = jadwal.jadwal_sholat_bulanini[global_vars.system_date][sholat.value]
    embed_desc=f"Hari: {global_vars.system_day_name}\nTugas: {tugas.value}\nSholat: {sholat.value.capitalize()}\nWaktu Sholat: {waktu_sholat}\nTempat: {tempat.value.upper()}\nPetugas Default: {nama_petugas_default}"

    embed = discord.Embed(
        title="Detail Jadwal",
        color=discord.Color.green(),
        description=embed_desc
    )

    content=f"**✅ Jadwal telah diklaim oleh {nama_pengklaim} ✅**"

    await message.edit(content=content, embed=embed, view=None)

    await interaction.followup.send(f"Berhasil mengklaim untuk {nama_pengklaim}")

    global_vars.notification_ids.pop(f"{tugas.value}_{sholat.value}_{tempat.value}", None)