import time
import os
import asyncpg
from datetime import datetime
from AyiinXd import CMD_HANDLER as cmd
from AyiinXd import CMD_HELP, DB_URI
from AyiinXd.ayiin import ayiin_cmd

DURASI_UBOT = os.getenv("DURASI_UBOT", "30hari").lower()
DATABASE_URL = DB_URI

# Konversi durasi ke detik
def konversi_ke_detik(durasi: str) -> int:
    if durasi == "lifetime":
        return -1  # penanda lifetime
    jumlah = ''.join(filter(str.isdigit, durasi))
    satuan = ''.join(filter(str.isalpha, durasi))

    if not jumlah or not satuan:
        return 0

    jumlah = int(jumlah)
    konversi = {
        "menit": 60,
        "jam": 3600,
        "hari": 86400,
        "minggu": 7 * 86400,
        "bulan": 30 * 86400,
        "tahun": 365 * 86400,
    }
    return jumlah * konversi.get(satuan, 0)

@ayiin_cmd(pattern="cekdurasi$")
async def _(event):
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS bot_info (
                id INTEGER PRIMARY KEY,
                start_time BIGINT,
                jenis TEXT
            );
        """)
        row = await conn.fetchrow("SELECT start_time, jenis FROM bot_info WHERE id=1")
        now = int(time.time())

        if not row:
            await conn.execute("""
                INSERT INTO bot_info (id, start_time, jenis)
                VALUES (1, $1, $2)
            """, now, DURASI_UBOT)
            await event.edit(f"**Tabel database dibuat dan durasi otomatis di-set ke** `{DURASI_UBOT}`")
            await conn.close()
            return

        jenis = row['jenis']
        start_time = row['start_time']

        if jenis == "lifetime":
            await event.edit("**Durasi:** `Lifetime`\n**Sisa Durasi:** `Tidak terbatas`\n**Habis Tanggal:** `-`")
        else:
            total_durasi = konversi_ke_detik(jenis)
            sisa = total_durasi - (now - start_time)

            if sisa <= 0:
                await event.edit("**Durasi kamu sudah habis. Silakan hubungi @jPipis untuk perpanjangan userbot.**")
            else:
                habis_timestamp = start_time + total_durasi
                habis_tanggal = datetime.fromtimestamp(habis_timestamp).strftime("%d %B %Y")

                days = sisa // 86400
                hours = (sisa % 86400) // 3600
                minutes = (sisa % 3600) // 60
                seconds = sisa % 60

                await event.edit(
    f"**Informasi Userbot kamu:**\n"
    f"**Durasi:** `{jenis}`\n"
    f"**Sisa Durasi:** `{days} hari, {hours} jam, {minutes} menit, {seconds} detik`\n"
    f"**Habis Tanggal:** `{habis_tanggal}`"
    )
        await conn.close()
    except Exception as e:
        await event.edit(f"**Terjadi kesalahan:**\n`{str(e)}`")

CMD_HELP.update({
    "cek_durasi": f"**Plugin :** `cek_durasi`\
    \n\n  »  **Perintah :** `{cmd}cekdurasi`\
    \n  »  **Fungsi :** Untuk mengecek durasi userbot.\
"
})
