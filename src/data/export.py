from datetime import datetime, timedelta
import discord
import xlsxwriter
from xlsxwriter.color import Color
from config import SHOLAT_TUPLE, bot, ADMIN_CHANNEL, SYSTEM_TIMEZONE
from global_vars import global_vars, scheduler
from data.loader import jadwal

async def export_json(target: discord.Webhook):
    json_file = open("src/data/presensi_rawatib.json", "rb")
    await target.send(
        content="## 📃 File json presensi keseluruhan",
        file=discord.File(json_file)
    )
    json_file.close

def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += 7
    return d + timedelta(days=days_ahead)

def export_next_monday():
    MONDAY = 0
    EXPORT_RANGE = 8
    datetime_object = datetime.strptime(global_vars.system_date, "%Y-%m-%d")
    run_date = next_weekday(datetime_object, MONDAY)
    target = bot.get_channel(ADMIN_CHANNEL)
    scheduler.add_job(func=export_to_excel, args=[target, EXPORT_RANGE], trigger="date", run_date=run_date, id="weekly_export", replace_existing=True, misfire_grace_time=60)

async def export_to_excel(target: discord.Webhook, export_range):
    if not target: return
    workbook = xlsxwriter.Workbook("WeekReport.xlsx")

    formats = {
        "green": workbook.add_format({"bg_color": Color("#B6D7A8"), "border": 1}),
        "blue": workbook.add_format({"bg_color": Color("#A4C2F4"), "border": 1}),
        "red": workbook.add_format({"bg_color": Color("#EA9999"), "border": 1}),
        "grey": workbook.add_format({"bg_color": Color("#CCCCCC"), "border": 1}),
        "blackout": workbook.add_format({"bg_color": Color("#000000"), "border": 1}),
        "bold_middle": workbook.add_format({
            "bold": True,
            "align": "center",
            "valign": "vcenter",
            "border": 1
        }),
        "text_wrap": workbook.add_format({"text_wrap": True, "border": 1}),
        "align_top": workbook.add_format({"valign": "top", "border": 1})
    }

    export_presensi("msu", workbook, formats, export_range)
    export_presensi("tult", workbook, formats, export_range)
    export_alasan_absen(workbook, formats, export_range)

    workbook.close()
    export_next_monday()

    week_number = (datetime.now(SYSTEM_TIMEZONE) - timedelta(days=1)).strftime("%W") # -1 hari karena dikirim hari senin minggu depannya

    report_file = open("ExcelReport.xlsx", "rb")

    if export_range == 8:
        content=f"## 📋 Rekapitulasi Presensi Minggu-{week_number}"
        filename=f"Laporan_Minggu-{week_number}.xlsx"
    else:
        content=f"## 📋 Rekapitulasi Presensi {export_range - 1} Hari ke Belakang"
        filename=f"Laporan_{global_vars.system_date}.xlsx"

    await target.send(
        content=content,
        file=discord.File(report_file, filename=filename)
    )

    report_file.close()

def export_presensi(tempat: str, workbook: xlsxwriter.Workbook, formats: dict, export_range):
    JUMLAH_TUGAS_SHOLAT = {
        "Subuh": 3, 
        "Dzuhur": 4, 
        "Ashar": 4, 
        "Maghrib": 3, 
        "Isya": 3
    }

    TUGAS = ("Muadzin", "Imam", "Badal", "Hadits")

    HEADER_ROW = 0
    SHOLAT_COL = 0
    TUGAS_COL = 1

    sheet_presensi = workbook.add_worksheet(tempat.upper())

    sholat_row = 1
    tugas_row = 1

    sheet_presensi.write(HEADER_ROW, SHOLAT_COL, "Sholat", formats["bold_middle"])
    sheet_presensi.write(HEADER_ROW, TUGAS_COL, "Tugas", formats["bold_middle"])
    sheet_presensi.set_column(SHOLAT_COL, TUGAS_COL, width=12)

    for sholat in JUMLAH_TUGAS_SHOLAT:
        if sholat.lower() not in jadwal.presensi_rawatib[global_vars.system_date][tempat]: continue
        sheet_presensi.merge_range(sholat_row, SHOLAT_COL, sholat_row + JUMLAH_TUGAS_SHOLAT[sholat] - 1, 0, sholat, formats["bold_middle"])
        sholat_row += JUMLAH_TUGAS_SHOLAT[sholat]

        for i in range(JUMLAH_TUGAS_SHOLAT[sholat]):
            sheet_presensi.write(tugas_row, TUGAS_COL, TUGAS[i], formats["bold_middle"])
            tugas_row += 1

    petugas_col = 2

    datetime_object = datetime.strptime(global_vars.system_date, "%Y-%m-%d")
    for i in range(1, export_range):
        tanggal = str(datetime.date(datetime_object - timedelta(days=i)))
        if tanggal not in jadwal.presensi_rawatib: continue
        if tempat not in jadwal.presensi_rawatib[tanggal]: continue

        sheet_presensi.set_column(petugas_col, petugas_col, width=12)
        sheet_presensi.write(HEADER_ROW, petugas_col, tanggal, formats["bold_middle"])
        petugas_row = 0
        for sholat in SHOLAT_TUPLE:
            if sholat not in jadwal.presensi_rawatib[tanggal][tempat]:
                continue

            for i in range(JUMLAH_TUGAS_SHOLAT[sholat.capitalize()]):
                petugas_row += 1
                tugas = TUGAS[i]

                if tugas not in jadwal.presensi_rawatib[tanggal][tempat][sholat]:
                    sheet_presensi.write(petugas_row, petugas_col, None, formats["blackout"])
                    continue

                id_anggota = jadwal.presensi_rawatib[tanggal][tempat][sholat][tugas]['id_anggota']

                if id_anggota == 0: 
                    sheet_presensi.write(petugas_row, petugas_col, None, formats["blackout"])
                    continue

                confirmed = jadwal.presensi_rawatib[tanggal][tempat][sholat][tugas]['confirmed']
                id_sub = jadwal.presensi_rawatib[tanggal][tempat][sholat][tugas]['id_sub']

                anggota = jadwal.anggota[id_anggota]
                    
                if confirmed:
                    if id_sub == 0:
                        color_format = formats["green"]
                    else:
                        color_format = formats["blue"]
                        anggota = jadwal.anggota[id_sub]
                elif anggota['uid'] == 0:
                    color_format = formats["grey"]
                else:
                    color_format = formats["red"]

                sheet_presensi.write(petugas_row, petugas_col, anggota['nama'], color_format)
            
        petugas_col += 1

def export_alasan_absen(workbook: xlsxwriter.Workbook, formats: dict, export_range):
    HEADER_ROW = 0
    TANGGAL_COL = 0
    NAMA_COL = 1
    ALASAN_COL = 2

    sheet_absen = workbook.add_worksheet("Alasan Absen")

    sheet_absen.write(HEADER_ROW, TANGGAL_COL, "Tanggal", formats["bold_middle"])
    sheet_absen.write(HEADER_ROW, NAMA_COL, "Nama", formats["bold_middle"])
    sheet_absen.write(HEADER_ROW, ALASAN_COL, "Alasan", formats["bold_middle"])

    sheet_absen.set_column(TANGGAL_COL, NAMA_COL, width=12)
    sheet_absen.set_column(ALASAN_COL, ALASAN_COL, width=50)


    datetime_object = datetime.strptime(global_vars.system_date, "%Y-%m-%d")
    start_row = 1
    for i in range(1, export_range):
        tanggal = str(datetime.date(datetime_object - timedelta(days=i)))
        if tanggal not in jadwal.alasan_absen: continue

        current_row = int(start_row)
        for id_anggota in jadwal.alasan_absen[tanggal]:
            nama_anggota = jadwal.anggota[int(id_anggota)]["nama"]
            alasan_absen = jadwal.alasan_absen[tanggal][id_anggota]
            sheet_absen.write(current_row, NAMA_COL, nama_anggota, formats["align_top"])
            sheet_absen.write(current_row, ALASAN_COL, alasan_absen, formats["text_wrap"])

            current_row += 1

        if start_row == current_row - 1:
            sheet_absen.write(start_row, TANGGAL_COL, tanggal, formats["bold_middle"])
        else:
            sheet_absen.merge_range(start_row, TANGGAL_COL, current_row - 1, TANGGAL_COL, tanggal, formats["bold_middle"])
        start_row = current_row