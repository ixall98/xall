import time
import asyncpg
import os
from AyiinXd.ayiin import ayiin_cmd

DATABASE_URL = os.environ.get("DATABASE_URL")

async def get_start_time():
    conn = await asyncpg.connect(DATABASE_URL)
    row = await conn.fetchrow("SELECT start_time FROM bot_info WHERE id=1")
    await conn.close()
    return row['start_time'] if row else None

async def set_start_time():
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute("INSERT INTO bot_info(id, start_time) VALUES(1, $1) ON CONFLICT(id) DO NOTHING", int(time.time()))
    await conn.close()

@ayiin_cmd(pattern="cekdurasi$")
async def _(event):
    await set_start_time()
    start_time = await get_start_time()
    if not start_time:
        return await event.edit("Gagal ambil data durasi.")

    now = int(time.time())
    durasi_max = 30 * 24 * 60 * 60  # 30 hari
    sisa = durasi_max - (now - start_time)

    days = sisa // 86400
    hours = (sisa % 86400) // 3600
    minutes = (sisa % 3600) // 60
    seconds = sisa % 60

    await event.edit(f"**Sisa Durasi Userbot:**\n`{days} hari, {hours} jam, {minutes} menit, {seconds} detik`")
