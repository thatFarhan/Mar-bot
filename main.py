import discord
from discord.ext import commands, tasks
from discord import app_commands
from datetime import datetime, time, timedelta
import logging
from dotenv import load_dotenv
import os
import json
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from enum import Enum
from zoneinfo import ZoneInfo

load_dotenv()
token=os.getenv('DISCORD_TOKEN')
# change these with your server's channel ids
DAILY_SCHEDULE_CHANNEL=1470291576398938186
SUB_REQUESTS_CHANNEL=1470733669273436200
REMINDERS_CHANNEL=1471430354366632088
GUILD_ID=discord.Object(id=os.getenv('GUILD_ID'))

handler=logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents=discord.Intents.default()
intents.message_content=True
intents.members=True

# system_date is 4 hours ahead so that the day changes at 20:00
actual_timezone=ZoneInfo("Asia/Jakarta")
system_timezone=ZoneInfo("Asia/Magadan")

# -1 because it's used for accessing arrays
actual_date=datetime.now(actual_timezone).date().day-1
system_date=datetime.now(system_timezone).date().day-1

# APScheduler
scheduler = AsyncIOScheduler(timezone=actual_timezone)

SHOLAT_TITLE={
    "subuh": "🌅 Subuh", 
    "dzuhur": "☀️ Dzuhur", 
    "ashar": "🌇 Ashar", 
    "maghrib": "🌆 Maghrib", 
    "isya": "🌔 Isya"
}

TEMPAT_TITLE={
    "msu": "🕌 Masjid Syamsul 'Ulum",
    "tult": "🗼 TULT"
}

# get jadwal sholat from json
with open('jadwal_sholat.json') as file:
    jadwal_sholat_bulanini=json.load(file)["data"]["jadwal"]

# get jadwal petugas from json
with open('jadwal_petugas.json') as file:
    jadwal_petugas=json.load(file)

# get petugas hari ini from json
with open('jadwal_hariini.json') as file:
    jadwal_hariini=json.load(file)

# get real names from json
with open('nama_asli.json') as file:
    nama_asli=json.load(file)

# var day name
system_day_name=jadwal_sholat_bulanini[system_date]['hari']

bot=commands.Bot(command_prefix="/", intents=intents)
mention_everyone = discord.AllowedMentions(everyone=True)

@bot.event
async def on_ready():
    print("Mar-bot siap bertugas pada", datetime.now(actual_timezone))

    try:
        guild=GUILD_ID
        synced=await bot.tree.sync(guild=guild)
        print(f"Synced {len(synced)} commands to guild {guild.id}")
    except Exception as e:
        print(f"Error syncing commands: {e}")

    new_system_day.start()
    new_actual_day.start()

    if not scheduler.running:
        scheduler.start()

    set_reminders()

# new day for system / 20:00 actual time
@tasks.loop(time=time(hour=20, tzinfo=actual_timezone))
async def new_system_day():
    # update system date
    global system_date
    system_date=datetime.now(system_timezone).date().day-1

    # send daily
    channel=bot.get_channel(DAILY_SCHEDULE_CHANNEL)
    await send_daily_schedule(channel)

    write_todays_pic()
    set_reminders()

# new day for actual
@tasks.loop(time=time(hour=0, tzinfo=actual_timezone))
async def new_actual_day():
    # update actual date
    global actual_date
    actual_date=datetime.now(actual_timezone).date().day-1

# make today's schedule into a json file
def write_todays_pic():
    petugas_hariini = jadwal_petugas[system_day_name]

    for tempat in petugas_hariini:
        for sholat in petugas_hariini[tempat]:
            for tugas in petugas_hariini[tempat][sholat]:
                # additional attributes
                petugas=petugas_hariini[tempat][sholat][tugas]
                petugas['confirmed'] = False
                petugas['need_sub'] = False
                petugas['nama_sub'] = None
                petugas['uid_sub'] = None

    with open('jadwal_hariini.json', 'w') as file:
        json.dump(jadwal_petugas[system_day_name], file, indent=2)
        print(f"Jadwal hari {system_day_name} telah dibuat menjadi json derulo")

    with open('jadwal_hariini.json') as file:
        global jadwal_hariini
        jadwal_hariini=json.load(file)

# schedule embed builder
def build_schedule_and_tags(tempat: str, system_day_name: str):
    jadwal=discord.Embed(
            title=TEMPAT_TITLE[tempat],
            color=discord.Color.green()
        )

    tags=set()
    for sholat in jadwal_petugas[f'{system_day_name}'][tempat]:
        field_values=[]
        for tugas in jadwal_petugas[f'{system_day_name}'][tempat][sholat]:
            field_values.append(f"**{tugas}:** {jadwal_petugas[system_day_name][tempat][sholat][tugas]['nama']}")
            tags.add(f"<@{jadwal_petugas[system_day_name][tempat][sholat][tugas]['uid']}>")

        jadwal.add_field(
            name=f"{SHOLAT_TITLE[sholat]} ({jadwal_sholat_bulanini[system_date][sholat]})",
            value="\n".join(field_values),
            inline=True
        )
    
    return [jadwal, tags]

async def send_daily_schedule(target):
    if target:
        # update global day name
        global system_day_name
        system_day_name=jadwal_sholat_bulanini[system_date]['hari']

        embeds=[]
        tags=set()
        for tempat in jadwal_petugas[system_day_name]:
            schedule_and_tags=build_schedule_and_tags(tempat, system_day_name)
            embeds.append(schedule_and_tags[0])
            for tag in schedule_and_tags[1]:
                tags.add(tag)

        await target.send(
            content=f"# 💫 Jadwal hari {system_day_name}\n## 🌃 Lailatukumus Sa'idah Ikhwan~\nBerikut adalah jadwal petugas untuk esok hari. Mohon untuk konfirmasi kehadiran jika bisa berhadir atau request pengganti jika tidak.\nJazaakumullaahu Khoiron, Baarakallahu Fiikum 🙏\n\n{' '.join(tags)}\n\n",
            embeds=embeds,
            view=ConfirmationButtons()
        )
    else:
        print("Send schedule failed")

class ConfirmationButtons(discord.ui.View):
    @discord.ui.button(label="Konfirmasi Semua", style=discord.ButtonStyle.green)
    async def button_confirmall(self, interaction: discord.Interaction, button: discord.ui.Button):
        await confirm_all(interaction)

    @discord.ui.button(label="Request Pengganti Semua", style=discord.ButtonStyle.red)
    async def button_sellall(self, interaction: discord.Interaction, button: discord.ui.Button):
        await sell_all(interaction)

# resend daily schedule
@bot.tree.command(name="resend", description="[ADMIN] Mengirim ulang jadwal harian", guild=GUILD_ID)
@app_commands.checks.has_role("Marbot Mar-bot")
async def resend(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    await send_daily_schedule(interaction.followup)

@bot.tree.command(name="rewrite", description="[ADMIN] Menulis ulang file json jadwal hari ini", guild=GUILD_ID)
@app_commands.checks.has_role("Marbot Mar-bot")
async def rewrite(interaction: discord.Interaction):
    write_todays_pic()
    await interaction.response.send_message("jadwal_hariini.json telah ditulis ulang", ephemeral=True)

# options for single actions
class TugasEnum(str, Enum):
    Imam = "Imam"
    Muadzin = "Muadzin"

class SholatEnum(str, Enum):
    Subuh = "subuh"
    Dzuhur = "dzuhur"
    Ashar = "ashar"
    Maghrib = "maghrib"
    Isya = "isya"

class TempatEnum(str, Enum):
    MSU = "msu"
    TULT = "tult"

# confirm presence
# single
@bot.tree.command(name="confirm", description="Mengonfirmasi presensi suatu jadwal antum di hari ini", guild=GUILD_ID)
@app_commands.describe(tugas="Tugas yang mana?", sholat="Sholat apa?", tempat="Dimana?")
async def confirm(interaction: discord.Interaction, tugas: TugasEnum, sholat: SholatEnum, tempat: TempatEnum):
    if sholat.value not in jadwal_hariini[tempat.value] or tugas.value not in jadwal_hariini[tempat.value][sholat.value]:
        await interaction.response.send_message(f"Jadwal {tugas.name} Sholat {sholat.name} di {tempat.name} tidak ada", ephemeral=True)
        return
    
    petugas = jadwal_hariini[tempat.value][sholat.value][tugas.value]
    if petugas['uid'] == interaction.user.id and not petugas['confirmed']:
        update_to_confirm(tugas.value, sholat.value, tempat.value)
        with open('jadwal_hariini.json', 'w') as file:
            json.dump(jadwal_hariini, file, indent=2)

        await interaction.response.send_message(f"Berhasil mengonfirmasi jadwal {tugas.name} Sholat {sholat.name} di {tempat.name}, Syukran Jazilan 🙏", ephemeral=True)
    else:
        await interaction.response.send_message(f"Jadwal sudah dikonfirmasi atau antum tidak memiliki jadwal {tugas.name} Sholat {sholat.name} di {tempat.name} pada hari ini", ephemeral=True)

# all
@bot.tree.command(name="confirmall", description="Mengonfirmasi presensi untuk seluruh jadwal antum hari ini", guild=GUILD_ID)
async def confirmall(interaction: discord.Interaction):
    await confirm_all(interaction)

async def confirm_all(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    confirmed_anything = False
    for tempat in jadwal_hariini:
        for sholat in jadwal_hariini[tempat]:
            for tugas in jadwal_hariini[tempat][sholat]:
                petugas = jadwal_hariini[tempat][sholat][tugas]
                if petugas['uid'] == interaction.user.id and not petugas['confirmed']:
                    update_to_confirm(tugas, sholat, tempat)
                    confirmed_anything = True
        
    if confirmed_anything:
        with open('jadwal_hariini.json', 'w') as file:
            json.dump(jadwal_hariini, file, indent=2)
        await interaction.followup.send(content="Berhasil mengonfirmasi seluruh jadwal antum hari ini, Syukran Jazilan 🙏", ephemeral=True)
    else:
        await interaction.followup.send(content="Jadwal sudah dikonfirmasi atau antum tidak memiliki jadwal hari ini", ephemeral=True)

def update_to_confirm(tugas: str, sholat: str, tempat: str):
    petugas=jadwal_hariini[tempat][sholat][tugas]
    petugas.update({"confirmed": True})
    petugas.update({"need_sub": False})
    petugas.update({"nama_sub": None})
    petugas.update({"uid_sub": None})

    if scheduler.get_job(job_id=f"emergency_{tugas}_{sholat}_{tempat}"):
        scheduler.remove_job(job_id=f"emergency_{tugas}_{sholat}_{tempat}")

# sell schedule
@bot.tree.command(name="sell", description="Merequest pengganti untuk suatu jadwal antum di hari ini", guild=GUILD_ID)
@app_commands.describe(tugas="Tugas yang mana?", sholat="Sholat apa?", tempat="Dimana?")
async def sell(interaction: discord.Interaction, tugas: TugasEnum, sholat: SholatEnum, tempat: TempatEnum):
    if sholat.value not in jadwal_hariini[tempat.value] or tugas.value not in jadwal_hariini[tempat.value][sholat.value]:
        await interaction.response.send_message(f"Jadwal {tugas.name} Sholat {sholat.name} di {tempat.name} tidak ada", ephemeral=True)
        return

    petugas = jadwal_hariini[tempat.value][sholat.value][tugas.value]
    if (petugas['uid'] == interaction.user.id or petugas['uid_sub'] == interaction.user.id) and not petugas['need_sub']:
        update_to_sell(tugas, sholat, tempat)
        await on_sale_noti(tugas.value, sholat.value, tempat.value)
        with open('jadwal_hariini.json', 'w') as file:
            json.dump(jadwal_hariini, file, indent=2)

        await interaction.response.send_message(f"Berhasil meminta pengganti untuk {tugas.name} Sholat {sholat.name} di {tempat.name}", ephemeral=True)
    else:
        await interaction.response.send_message(f"Antum tidak memiliki jadwal {tugas.name} Sholat {sholat.name} di {tempat.name} pada hari ini", ephemeral=True)

@bot.tree.command(name="sellall", description="Merequest pengganti untuk seluruh jadwal antum di hari ini", guild=GUILD_ID)
async def sellall(interaction: discord.Interaction):
    await sell_all(interaction)

async def sell_all(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    sold_anything = False
    for tempat in jadwal_hariini:
        for sholat in jadwal_hariini[tempat]:
            for tugas in jadwal_hariini[tempat][sholat]:
                
                petugas = jadwal_hariini[tempat][sholat][tugas]
                if (petugas['uid'] == interaction.user.id or petugas['uid_sub'] == interaction.user.id) and not petugas['need_sub']:
                    update_to_sell(tugas, sholat, tempat)
                    await on_sale_noti(tugas, sholat, tempat)
                    sold_anything = True
        
    if sold_anything:
        with open('jadwal_hariini.json', 'w') as file:
            json.dump(jadwal_hariini, file, indent=2)

        await interaction.followup.send(content="Berhasil meminta pengganti untuk seluruh jadwal antum hari ini", ephemeral=True)
    else:
        await interaction.followup.send(content="Antum tidak memiliki jadwal hari ini", ephemeral=True)

def update_to_sell(tugas: str, sholat: str, tempat: str):
    if tugas == 'Pembaca Hadits': return

    petugas=jadwal_hariini[tempat][sholat][tugas]
    petugas.update({"confirmed": False})
    petugas.update({"need_sub": True})
    petugas.update({"nama_sub": None})
    petugas.update({"uid_sub": None})

    if scheduler.get_job(job_id=f"emergency_{tugas}_{sholat}_{tempat}"):
        scheduler.remove_job(job_id=f"emergency_{tugas}_{sholat}_{tempat}")

# send schedule on sale notification to second channel
async def on_sale_noti(tugas, sholat, tempat, emergency=False):
    if tugas == 'Pembaca Hadits': return

    target=bot.get_channel(SUB_REQUESTS_CHANNEL)
    embed_desc=f"Hari: {system_day_name}\nTugas: {tugas}\nSholat: {sholat.capitalize()}\nWaktu Sholat: {jadwal_sholat_bulanini[system_date][sholat]}\nTempat: {tempat.upper()}\nPetugas Default: {jadwal_hariini[tempat][sholat][tugas]['nama']}"

    embed=discord.Embed(
        title="Detail Jadwal", 
        color=discord.Color.red() if emergency else discord.Color.gold(),
        description=embed_desc
    )

    tags = ""
    if tugas == "Muadzin" or emergency:
        tags = "@everyone"
    else:
        tags = f"Badal: <@{jadwal_hariini[tempat][sholat]['Badal']['uid']}>"

    if emergency:
        content=f"## 🚨 PERHATIAN (PENGGANTI) 🚨\n**{tugas} Sholat {sholat.capitalize()} di {tempat.upper()} Perlu Pengganti!**\n{tags}"
    else:
        content=f"**📢 {tugas} Sholat {sholat.capitalize()} di {tempat.upper()} Perlu Pengganti! 📢**\n{tags}"

    await target.send(content=content, embed=embed, view=ClaimButton(tugas, sholat, tempat, embed_desc), allowed_mentions=mention_everyone)

class ClaimButton(discord.ui.View):
    def __init__(self, tugas: str, sholat: str, tempat: str, embed_desc: str):
        super().__init__()
        self.tugas = tugas
        self.sholat = sholat
        self.tempat = tempat
        self.embed_desc = embed_desc

    @discord.ui.button(label="Klaim Jadwal", style=discord.ButtonStyle.primary)
    async def button_claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        tugas = self.tugas
        sholat = self.sholat
        tempat = self.tempat
        embed_desc = self.embed_desc

        petugas = jadwal_hariini[tempat][sholat][tugas]

        if petugas['uid'] == interaction.user.id:
            update_to_confirm(tugas, sholat, tempat)
        else:
            update_to_claim(tugas, sholat, tempat, interaction.user.id)

        with open('jadwal_hariini.json', 'w') as file:
            json.dump(jadwal_hariini, file, indent=2)

        embed = discord.Embed(
            title=f"Detail Jadwal",
            color=discord.Color.green(),
            description=embed_desc
        )
        content=f"**✅ Jadwal telah diklaim oleh {nama_asli[str(interaction.user.id)]} ✅**"
        await interaction.response.edit_message(content=content, embed=embed, view=None)

def update_to_claim(tugas: str, sholat: str, tempat: str, uid: int):
    petugas=jadwal_hariini[tempat][sholat][tugas]
    petugas.update({"confirmed": True})
    petugas.update({"need_sub": False})
    petugas.update({"nama_sub": nama_asli[str(uid)]})
    petugas.update({"uid_sub": uid})

    if scheduler.get_job(job_id=f"emergency_{tugas}_{sholat}_{tempat}"):
        scheduler.remove_job(job_id=f"emergency_{tugas}_{sholat}_{tempat}")

# show prayer schedule
@bot.tree.command(name="jadwalsholat", description="Menampilkan jadwal sholat untuk bulan ini pada tanggal tertentu", guild=GUILD_ID)
async def jadwalsholat(interaction: discord.Interaction, tanggal: str):
    if tanggal == "today":
        target_date=actual_date

    elif tanggal == "tomorrow":
        target_date=actual_date + 1

    else:
        try:
            target_date=int(tanggal) - 1
        except ValueError:
            await interaction.response.send_message("Parameter harus berupa angka atau 'Hari ini' / 'Besok'", ephemeral=True)
            return
        
    if target_date > len(jadwal_sholat_bulanini) - 1:
        await interaction.response.send_message("Tanggal tidak bisa melebihi tanggal terakhir bulan ini", ephemeral=True)
        return
    
    if target_date < 0:
        await interaction.response.send_message("Tanggal harus lebih dari 1", ephemeral=True)
        return

    embed=discord.Embed(
        title=f"🕌 Jadwal Sholat {jadwal_sholat_bulanini[target_date]['hari']}, {jadwal_sholat_bulanini[target_date]['tanggal_lengkap']}",
        color=discord.Color.green()
    )

    for sholat in SHOLAT_TITLE:
        embed.add_field(
            name=SHOLAT_TITLE[sholat],
            value=jadwal_sholat_bulanini[target_date][sholat],
            inline=True
        )

    await interaction.response.send_message(embed=embed)

@jadwalsholat.autocomplete("tanggal")
async def hari_autocomplete(interaction: discord.Interaction, tanggal: str):
    choices=[
        app_commands.Choice(name="Hari ini", value="today"),
        app_commands.Choice(name="Besok", value="tomorrow")
    ]

    return choices

@bot.tree.command(name="testscheduled", description="[ADMIN] Tes scheduled message",guild=GUILD_ID)
@app_commands.checks.has_role("Marbot Mar-bot")
async def testschedule(interaction: discord.Interaction):
    await interaction.response.send_message(content="test", ephemeral=True)
    await send_reminder('maghrib')
    for schedule in scheduler.get_jobs():
        print(schedule)

async def send_reminder(sholat: str):
    embed=discord.Embed(
        title=f"{SHOLAT_TITLE[sholat]} ({jadwal_sholat_bulanini[system_date][sholat]})",
        color=discord.Color.green()
    )

    tags_need_confirmation=set()

    tags=set()
    for tempat in jadwal_hariini:
        if sholat not in jadwal_hariini[tempat]:
            continue

        list_petugas=[]
        for tugas in jadwal_hariini[tempat][sholat]:
            petugas=jadwal_hariini[tempat][sholat][tugas]
            if petugas['uid_sub'] is not None:
                list_petugas.append(f"**{tugas}:** {petugas['nama_sub']}")
                tags.add(f"<@{petugas['uid_sub']}>")
            else:
                list_petugas.append(f"**{tugas}:** {petugas['nama']}")
                tags.add(f"<@{petugas['uid']}>")
                if not petugas['confirmed'] and not petugas['need_sub']:
                    tags_need_confirmation.add(f"<@{petugas['uid']}>")

                    # auto sell after 10 minutes if there's no confirmation
                    run_date=datetime.now(actual_timezone) + timedelta(minutes=10)

                    scheduler.add_job(func=emergency_sell, args=[tugas, sholat, tempat], trigger='date', run_date=run_date, id=f"emergency_{tugas}_{sholat}_{tempat}", replace_existing=True)
                elif petugas['need_sub']:
                    await on_sale_noti(tugas, sholat, tempat, True)

        embed.add_field(
            name=TEMPAT_TITLE[tempat],
            value="\n".join(list_petugas),
            inline=True
        )

    content=f"# ⏰ 30 Menit Menjelang Sholat {sholat.capitalize()} ⏰\nDiingatkan kembali kepada para petugas, harap untuk hadir sesuai dengan plotingannya masing-masing.\nJazaakumullaahu Khoiron, Baarakallahu Fiikum 🙏\n\n{' '.join(tags)}"

    reminders_channel=bot.get_channel(REMINDERS_CHANNEL)
    await reminders_channel.send(content=content, embed=embed)
    if tags_need_confirmation:
        unix_timestamp=int(run_date.timestamp())
        await reminders_channel.send(
            content=f"**⚠️ PERHATIAN (KONFIRMASI) ⚠️**\n\nNama di bawah ini belum melakukan konfirmasi. harap untuk melakukan konfirmasi <t:{unix_timestamp}:R>\n{' '.join(tags_need_confirmation)}",
            view=QuickConfirmationButtons(sholat)
        )

class QuickConfirmationButtons(discord.ui.View):
    def __init__(self, sholat: str):
        super().__init__()
        self.sholat = sholat

    @discord.ui.button(label="Konfirmasi", style=discord.ButtonStyle.green)
    async def button_confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        await quick_confirm(interaction, self.sholat)

    @discord.ui.button(label="Request Pengganti", style=discord.ButtonStyle.red)
    async def button_sell(self, interaction: discord.Interaction, button: discord.ui.Button):
        await quick_sell(interaction, self.sholat)

async def quick_confirm(interaction: discord.Interaction, sholat: str):
    await interaction.response.defer(ephemeral=True)
    confirmed_anything=False
    for tempat in jadwal_hariini:

        if sholat not in jadwal_hariini[tempat]:
            continue

        for tugas in jadwal_hariini[tempat][sholat]:
            petugas=jadwal_hariini[tempat][sholat][tugas]

            if petugas['uid'] != interaction.user.id or petugas['confirmed']:
                continue

            update_to_confirm(tugas, sholat, tempat)
            confirmed_anything=True

    if confirmed_anything:
        with open('jadwal_hariini.json', 'w') as file:
            json.dump(jadwal_hariini, file, indent=2)

        await interaction.followup.send(f"Berhasil mengonfirmasi jadwal {tugas} Sholat {sholat.capitalize()} di {tempat.upper()}, Syukran Jazilan 🙏", ephemeral=True)
    else:
        await interaction.followup.send(f"Antum tidak memiliki jadwal untuk Sholat {sholat.capitalize()} hari ini", ephemeral=True)

async def quick_sell(interaction: discord.Interaction, sholat: str):
    await interaction.response.defer(ephemeral=True)
    sold_anything=False
    for tempat in jadwal_hariini:

        if sholat not in jadwal_hariini[tempat]:
            continue

        for tugas in jadwal_hariini[tempat][sholat]:
            petugas=jadwal_hariini[tempat][sholat][tugas]

            if tugas == 'Pembaca Hadits': continue

            if (petugas['uid'] == interaction.user.id or petugas['uid_sub'] == interaction.user.id) and not petugas['need_sub']:
                update_to_sell(tugas, sholat, tempat)
                await on_sale_noti(tugas, sholat, tempat, True)
                sold_anything=True

    if sold_anything:
        with open('jadwal_hariini.json', 'w') as file:
            json.dump(jadwal_hariini, file, indent=2)

        await interaction.followup.send(f"Berhasil meminta pengganti untuk {tugas} Sholat {sholat.capitalize()} di {tempat.upper()}", ephemeral=True)
    else:
        await interaction.followup.send(f"Antum tidak memiliki jadwal untuk Sholat {sholat.capitalize()} hari ini", ephemeral=True)

# failed to confirm on time
async def emergency_sell(tugas: str, sholat: str, tempat: str):
    petugas=jadwal_hariini[tempat][sholat][tugas]
    update_to_sell(tugas, sholat, tempat)
    await on_sale_noti(tugas, sholat, tempat, True)
    with open('jadwal_hariini.json', 'w') as file:
        json.dump(jadwal_hariini, file, indent=2)

def set_reminders():
    for sholat in ('subuh', 'dzuhur', 'ashar', 'maghrib', 'isya'):
        date=jadwal_sholat_bulanini[system_date]['tanggal_lengkap'].split('-')
        time=jadwal_sholat_bulanini[system_date][sholat].split(':')

        year, month, day = int(date[0]), int(date[1]), int(date[2])
        hour, minute = int(time[0]), int(time[1])

        run_date=datetime(year=year, month=month, day=day, hour=hour, minute=minute) - timedelta(minutes=30)

        scheduler.add_job(func=send_reminder, args=[sholat], trigger='date', run_date=run_date, id=f"reminder_{sholat}", replace_existing=True)
    
    for schedule in scheduler.get_jobs():
        print(schedule)
    
bot.run(token, log_handler=handler, log_level=logging.DEBUG)