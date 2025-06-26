import os
import asyncpg

async def get_connection():
    DATABASE_URL = os.environ.get("DATABASE_URL")
    return await asyncpg.connect(dsn=DATABASE_URL)

async def init_db():
    conn = await get_connection()
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS sfs_channels (
            id SERIAL PRIMARY KEY,
            channel_username TEXT NOT NULL
        )
    """)
    await conn.close()

async def add_sfs_channels(channels):
    await init_db()  # pastikan tabel dibuat dulu
    conn = await get_connection()
    await conn.execute("DELETE FROM sfs_channels")  # Reset dulu
    await conn.executemany(
        "INSERT INTO sfs_channels (channel_username) VALUES ($1)",
        [(c,) for c in channels]
    )
    await conn.close()

async def get_sfs_channels():
    await init_db()
    conn = await get_connection()
    rows = await conn.fetch("SELECT channel_username FROM sfs_channels")
    await conn.close()
    return [r["channel_username"] for r in rows]

async def delete_sfs_channels():
    await init_db()
    conn = await get_connection()
    await conn.execute("DELETE FROM sfs_channels")
    await conn.close()
