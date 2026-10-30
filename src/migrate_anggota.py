import asyncio
import json
import sys
from pathlib import Path
from server_config import GUILD_ID


def parse(path: Path, id_server: int | None) -> list[tuple]:
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = []

    for index, item in enumerate(data):
        if index == 0 and item["nama"].strip() == "-":
            continue

        # uid 0 means "not linked to a Discord account yet"
        discord_uid = item.get("uid") or None

        rows.append((
            index,
            id_server,
            discord_uid,
            item["nama"].strip(),
            item["nama_lengkap"].strip(),
        ))
    return rows

INSERT = (
    "INSERT INTO anggota "
    "(id_anggota, id_server, discord_uid, nama_panggilan, nama_lengkap) "
    "VALUES (%s, %s, %s, %s, %s)"
)


def warn_duplicates(rows: list[tuple]):
    seen = {}
    for r in rows:
        uid = r[2]
        if uid is None:
            continue
        if uid in seen:
            print(
                f"WARNING: discord_uid {uid} is used by both "
                f"'{seen[uid]}' and '{r[3]}'. Is one of them a copy-paste error?",
                file=sys.stderr,
            )
        else:
            seen[uid] = r[3]


async def migrate(rows: list[tuple], id_server: int):
    import aiomysql

    conn = await aiomysql.connect(
        user="root",
        db="marbot",
        autocommit=False,  # one transaction: all rows or nothing
    )
    try:
        async with conn.cursor() as cur:

            await cur.execute(
                "SELECT 1 FROM discord_server WHERE id_server = %s", (id_server,)
            )
            if not await cur.fetchone():
                raise RuntimeError(
                    f"discord_server has no row for id_server {id_server}. "
                    "Insert it first (e.g. let the bot join the server once)."
                )

            await cur.executemany(INSERT, rows)

        await conn.commit()
        print(f"Inserted {len(rows)} rows into anggota (id_server={id_server}).")
    except Exception:
        await conn.rollback()
        raise
    finally:
        conn.close()


async def main():
    id_server = GUILD_ID.id

    rows = parse(Path("src/data/anggota.json"), id_server)
    linked = sum(1 for r in rows if r[2] is not None)
    print(f"Parsed {len(rows)} members ({linked} with a Discord uid), id_server={id_server}.")
    warn_duplicates(rows)

    await migrate(rows, id_server)
