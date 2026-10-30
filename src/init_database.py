import asyncio

from aiomysql import DatabaseError
from pathlib import Path

import aiomysql
from aiomysql import DatabaseError
from migrate_anggota import main as migrate_anggota
from migrate_jadwal_tetap import main as migrate_jadwal_tetap
from migrate_masjid import main as migrate_masjid

async def init_database():

    # 1. Connect to the server itself (no database selected yet)
    try:
        conn = await aiomysql.connect(
            user="root",
            connect_timeout=5,
        )
    except Exception as e:
        raise DatabaseError(f"Could not connect to database server: {e}") from e

    # 2. Create the database if it doesn't exist
    try:
        async with conn.cursor() as cur:
            await cur.execute(
                f"CREATE DATABASE IF NOT EXISTS marbot"
            )
    except Exception as e:
        raise DatabaseError(f"Could not create database: {e}") from e
    finally:
        conn.close()

    # Now create the real pool, bound to the database
    try:
        pool = await aiomysql.create_pool(
            user="root",
            db="marbot",
            autocommit=False,
            cursorclass=aiomysql.DictCursor
        )
    except Exception as e:
        raise DatabaseError(f"Could not open connection pool: {e}") from e

    # 3. Create the tables if they don't exist
    try:
        await _create_tables(pool)
    except Exception as e:
        pool.close()
        await pool.wait_closed()
        raise DatabaseError(f"Could not create tables: {e}") from e

    pool.close()
    await pool.wait_closed()

async def _create_tables(pool: aiomysql.Pool):
    schema = (Path("src/database/schema.sql")).read_text(encoding="utf-8")
    statements = [s.strip() for s in schema.split(";") if s.strip()]

    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            for stmt in statements:
                await cur.execute(stmt)

async def main():
    try:
        await init_database()
    except DatabaseError as e:
        print("Aborting startup: ", e)
        return

    await migrate_masjid()
    await migrate_anggota()
    await migrate_jadwal_tetap()

    print("Migration Complete!")
    return
    

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Shut down by user. Bye!")