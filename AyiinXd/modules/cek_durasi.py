import time
import os
import asyncpg
from AyiinXd import CMD_HANDLER as cmd
from AyiinXd import CMD_HELP, DB_URI
from AyiinXd.ayiin import ayiin_cmd

LISENSI_DEFAULT = os.environ.get("DURASI_UBOT", "30hari").lower()
DATABASE_URL = DB_URI


@ayiin_cmd(pattern="cekdurasi$")
async def _(event):
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Cek apakah tabel ada
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS bot_info (
                id INTEGER PRIMARY KEY,
                start_time BIGINT,
                jenis TEXT
            );
        """)

        # Cek apakah ada data lisensi, jika belum insert data default
        row = await conn.fetchrow("SELECT start_time, jenis FROM bot_info WHERE id=1")
        
        if not row:
            # Insert data default lisensi (bisa 30 hari, 7 hari, atau lifetime)
            await conn.execute("""
                INSERT INTO bot_info (id, start_time, jenis)
                VALUES (1, $1, $2)
            """, int(time.time()), LISENSI_DEFAULT)
            await event.edit(f"**Tabel database dibuat dan lisensi otomatis di-set ke** `{LISENSI_DEFAULT}`")
            await conn.close()
            return

        # Ambil data dari database
        jenis = row['jenis']
        start_time = row['start_time']
        now = int(time.time())

        if jenis == "lifetime":
            await event.edit("**Durasi:** `Lifetime`\n`Durasi tidak terbatas.`")
        else:
            durasi_max = 7 * 86400 if jenis == "7hari" else 30 * 86400
            sisa = durasi_max - (now - start_time)

            if sisa <= 0:
                await event.edit("**Durasi userbot kamu sudah habis.**")
            else:
                days = sisa // 86400
                hours = (sisa % 86400) // 3600
                minutes = (sisa % 3600) // 60
                seconds = sisa % 60

                await event.edit(f"**Durasi:** `{jenis}`\n**Sisa Durasi:** `{days} hari, {hours} jam, {minutes} menit, {seconds} detik}`")

        await conn.close()
    except Exception as e:
        await event.edit(f"**Terjadi kesalahan:**\n`{str(e)}`")


CMD_HELP.update({
    "cek_durasi": f"**Plugin :** `cek_durasi`\
    \n\n  »  **Perintah :** `{cmd}cekdurasi`\
    \n  »  **Fungsi :** Cek sisa waktu durasi userbot.\
"
})
