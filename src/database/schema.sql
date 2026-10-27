CREATE TABLE IF NOT EXISTS discord_server (
    id_server BIGINT PRIMARY KEY,
    welcome_channel BIGINT NULL,
    daily_schedule_channel BIGINT NULL,
    sub_requests_channel BIGINT NULL,
    reminders_channel BIGINT NULL,
    admin_channel BIGINT NULL,
    auto_sell_enabled BOOLEAN DEFAULT FALSE,
    id_daily_schedule_message BIGINT NULL
);

CREATE TABLE IF NOT EXISTS anggota (
    id_anggota BIGINT AUTO_INCREMENT PRIMARY KEY,
    id_server BIGINT,
    discord_uid BIGINT NULL,
    nama_panggilan VARCHAR(255),
    nama_lengkap VARCHAR(255),
    FOREIGN KEY (id_server) REFERENCES discord_server(id_server) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS masjid (
    id_masjid BIGINT AUTO_INCREMENT PRIMARY KEY,
    nama_masjid VARCHAR(255),
    alamat_masjid VARCHAR(255),
    region VARCHAR(255),
    is_weekly BOOLEAN DEFAULT TRUE,
    masjid_enabled BOOLEAN DEFAULT FALSE,
    id_server BIGINT,
    FOREIGN KEY (id_server) REFERENCES discord_server(id_server) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS jadwal_tetap (
    id_jadwal_tetap BIGINT AUTO_INCREMENT PRIMARY KEY,
    id_masjid BIGINT,
    hari INT,
    sholat VARCHAR(255),
    tugas VARCHAR(255),
    tugas_order INT,
    id_anggota BIGINT NULL,
    FOREIGN KEY (id_masjid) REFERENCES masjid(id_masjid) ON DELETE CASCADE,
    FOREIGN KEY (id_anggota) REFERENCES anggota(id_anggota) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS presensi (
    id_presensi BIGINT AUTO_INCREMENT PRIMARY KEY,
    tanggal DATE,
    id_jadwal_tetap BIGINT,
    id_sub BIGINT NULL,
    confirmed BOOLEAN DEFAULT FALSE,
    need_sub BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (id_jadwal_tetap) REFERENCES jadwal_tetap(id_jadwal_tetap) ON DELETE SET NULL,
    FOREIGN KEY (id_sub) REFERENCES anggota(id_anggota) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS notifikasi (
    id_notifikasi BIGINT AUTO_INCREMENT PRIMARY KEY,
    type VARCHAR(255),
    expiry_date DATE,
    id_requestor BIGINT,
    requestor_message_id BIGINT,
    requestor_channel_id BIGINT,
    offerer_message_id BIGINT NULL,
    offerer_channel_id BIGINT NULL,
    id_requested_schedule BIGINT,
    id_offered_schedule BIGINT NULL,
    FOREIGN KEY (id_requestor) REFERENCES anggota(id_anggota),
    FOREIGN KEY (id_requested_schedule) REFERENCES presensi(id_presensi),
    FOREIGN KEY (id_offered_schedule) REFERENCES presensi(id_presensi)
);

CREATE TABLE IF NOT EXISTS alasan_absen (
    id_alasan BIGINT AUTO_INCREMENT PRIMARY KEY,
    id_presensi BIGINT,
    id_anggota BIGINT,
    alasan TEXT,
    FOREIGN KEY (id_presensi) REFERENCES presensi(id_presensi),
    FOREIGN KEY (id_anggota) REFERENCES anggota(id_anggota)
);