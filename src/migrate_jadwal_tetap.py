import asyncio
import json
import sys
from pathlib import Path

HARI = {
    "senin": 0,
    "selasa": 1,
    "rabu": 2,
    "kamis": 3,
    "jumat": 4,
    "sabtu": 5,
    "ahad": 6,
}

MASJID = {"msu": 1, "tult": 2}

TUGAS_ORDER = {"muadzin": 0, "imam": 1, "badal": 2, "hadits": 3}


def norm(text: str) -> str:
    """Lowercase and strip apostrophes so "Jum'at" matches "jumat"."""
    return text.strip().lower().replace("'", "").replace("\u2019", "")


def parse(path: Path) -> list[tuple]:
    """Return rows as (id_masjid, hari, sholat, tugas, tugas_order, id_anggota)."""
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = []

    for hari_name, masjid_dict in data.items():
        if norm(hari_name) not in HARI:
            raise ValueError(f"Unknown day: {hari_name!r}")
        hari = HARI[norm(hari_name)]

        for masjid_name, sholat_dict in masjid_dict.items():
            if norm(masjid_name) not in MASJID:
                raise ValueError(f"Unknown masjid: {masjid_name!r}")
            id_masjid = MASJID[norm(masjid_name)]

            for sholat, tugas_dict in sholat_dict.items():
                for tugas, info in tugas_dict.items():
                    if norm(tugas) not in TUGAS_ORDER:
                        raise ValueError(f"Unknown tugas: {tugas!r}")

                    # 0 is a placeholder for "nobody assigned" in the JSON. A real
                    # foreign key can't point at id 0, so store it as NULL.
                    id_anggota = info.get("id_anggota") or None

                    rows.append((
                        id_masjid,
                        hari,
                        sholat.strip().capitalize(),
                        tugas.strip().capitalize(),
                        TUGAS_ORDER[norm(tugas)],
                        id_anggota,
                    ))
    return rows

INSERT = (
    "INSERT INTO jadwal_tetap "
    "(id_masjid, hari, sholat, tugas, tugas_order, id_anggota) "
    "VALUES (%s, %s, %s, %s, %s, %s)"
)


async def migrate(rows: list[tuple]):
    import aiomysql

    conn = await aiomysql.connect(
        user="root",
        db="marbot",
        autocommit=False,  # one transaction: all rows or nothing
    )
    try:
        async with conn.cursor() as cur:
            await cur.execute("SELECT id_masjid FROM masjid")
            known_masjid = {r[0] for r in await cur.fetchall()}
            missing = {r[0] for r in rows} - known_masjid
            if missing:
                raise RuntimeError(
                    f"masjid table has no row for id_masjid {sorted(missing)}. "
                    "Insert them first."
                )

            await cur.execute("SELECT id_anggota FROM anggota")
            known_anggota = {r[0] for r in await cur.fetchall()}
            used = {r[5] for r in rows if r[5] is not None}
            missing = used - known_anggota
            if missing:
                raise RuntimeError(
                    f"anggota table has no row for id_anggota {sorted(missing)}. "
                    "Insert the members first."
                )

            await cur.executemany(INSERT, rows)

        await conn.commit()
        print(f"Inserted {len(rows)} rows into jadwal_tetap.")
    except Exception:
        await conn.rollback()
        raise
    finally:
        conn.close()


async def main():
    rows = parse(Path("src/data/jadwal_rawatib.json"))
    unassigned = sum(1 for r in rows if r[5] is None)
    print(f"Parsed {len(rows)} rows ({unassigned} with no member assigned).")


    try:
        await migrate(rows)
    except Exception as e:
        print(f"Migration failed: {e}", file=sys.stderr)
        sys.exit(1)
