import asyncpg
import os
from AyiinXd import ayiin_cmd

DATABASE_URL = os.environ.get("DATABASE_URL")

@ayiin_cmd(pattern="initdb$")
async def _(event):
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS bot_info (
                id INTEGER PRIMARY KEY,
                start_time BIGINT
            );
        """)
        await conn.close()
        await event.edit("**Tabel database berhasil dibuat!**")
    except Exception as e:
        await event.edit(f"**Gagal buat tabel:**\n`{str(e)}`")
