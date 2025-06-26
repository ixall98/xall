import asyncpg

# Koneksi PostgreSQL
async def get_connection():
    return await asyncpg.connect(dsn="DATABASE_URL_KAMU")

# Tambah channel
async def add_sfs_channels(channels: list[str]):
    conn = await get_connection()
    await conn.execute("DELETE FROM sfs_channels")  # Reset dulu
    await conn.executemany(
        "INSERT INTO sfs_channels (channel_username) VALUES ($1)", 
        [(ch,) for ch in channels]
    )
    await conn.close()

# Ambil semua channel
async def get_sfs_channels():
    conn = await get_connection()
    rows = await conn.fetch("SELECT channel_username FROM sfs_channels")
    await conn.close()
    return [r['channel_username'] for r in rows]

# Hapus semua
async def delete_sfs_channels():
    conn = await get_connection()
    await conn.execute("DELETE FROM sfs_channels")
    await conn.close()
