from AyiinUbot import CMD_HANDLER as cmd
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from asyncio import sleep
from datetime import datetime, timedelta
from collections import defaultdict
import sqlite3

from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.tl.functions.channels import JoinChannelRequest

scheduler = BackgroundScheduler()
scheduler.start()

conn = sqlite3.connect("spamjadwal.db")
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS listspam (
    nama TEXT PRIMARY KEY,
    teks TEXT,
    is_forward INTEGER
)
""")
c.execute("""
CREATE TABLE IF NOT EXISTS grupspam (
    nama TEXT,
    grup TEXT
)
""")
conn.commit()

active_jobs = {}

@ayiin_cmd(pattern="setlist (.*?)\n(.+)", allow_sudo=True)
async def set_list(event):
    nama, teks = event.pattern_match.group(1), event.pattern_match.group(2)
    c.execute("REPLACE INTO listspam VALUES (?, ?, 0)", (nama, teks))
    conn.commit()
    await event.edit(f"List spam `{nama}` disimpan dengan teks biasa.")

@ayiin_cmd(pattern="setlistfw (\S+) (https?://\S+)", allow_sudo=True)
async def set_listfw(event):
    nama, link = event.pattern_match.group(1), event.pattern_match.group(2)
    c.execute("REPLACE INTO listspam VALUES (?, ?, 1)", (nama, link))
    conn.commit()
    await event.edit(f"List spam `{nama}` disimpan sebagai forward dari link.")

@ayiin_cmd(pattern="setgc (\S+) (.+)", allow_sudo=True)
async def set_gc(event):
    nama, grups = event.pattern_match.group(1), event.pattern_match.group(2).split()
    for g in grups:
        c.execute("INSERT INTO grupspam VALUES (?, ?)", (nama, g))
    conn.commit()
    await event.edit(f"Berhasil tambah grup ke list `{nama}`.")

@ayiin_cmd(pattern="delgc (\S+) (\S+)", allow_sudo=True)
async def del_gc(event):
    nama, grup = event.pattern_match.group(1), event.pattern_match.group(2)
    c.execute("DELETE FROM grupspam WHERE nama = ? AND grup = ?", (nama, grup))
    conn.commit()
    await event.edit(f"Grup `{grup}` dihapus dari list `{nama}`.")

@ayiin_cmd(pattern="dellist (\S+)", allow_sudo=True)
async def del_list(event):
    nama = event.pattern_match.group(1)
    c.execute("DELETE FROM listspam WHERE nama = ?", (nama,))
    c.execute("DELETE FROM grupspam WHERE nama = ?", (nama,))
    conn.commit()
    await event.edit(f"List `{nama}` berhasil dihapus.")

async def kirim_spam(client, nama):
    c.execute("SELECT teks, is_forward FROM listspam WHERE nama = ?", (nama,))
    row = c.fetchone()
    if not row:
        return
    teks, is_forward = row
    c.execute("SELECT grup FROM grupspam WHERE nama = ?", (nama,))
    grups = [r[0] for r in c.fetchall()]
    for g in grups:
        try:
            if is_forward:
                await client.send_message(g, teks, forward=True)
            else:
                await client.send_message(g, teks, link_preview=False)
        except Exception as e:
            print(f"Gagal kirim ke {g}: {e}")

@ayiin_cmd(pattern="spamtime (\d{1,2}:\d{2}) (\S+)", allow_sudo=True)
async def spam_time(event):
    jam, nama = event.pattern_match.group(1), event.pattern_match.group(2)
    now = datetime.now()
    target = datetime.strptime(jam, "%H:%M").replace(year=now.year, month=now.month, day=now.day)
    if target < now:
        target += timedelta(days=1)
    job = scheduler.add_job(kirim_spam, trigger=CronTrigger(hour=target.hour, minute=target.minute), args=[event.client, nama])
    active_jobs[nama] = job
    await event.edit(f"Spam `{nama}` dijadwalkan jam {jam}.")

@ayiin_cmd(pattern="spamhari (\w+),(\d{1,2}:\d{2}) (\S+)", allow_sudo=True)
async def spam_hari(event):
    hari, jam, nama = event.pattern_match.group(1).lower(), event.pattern_match.group(2), event.pattern_match.group(3)
    hari_map = {'senin': 0, 'selasa': 1, 'rabu': 2, 'kamis': 3, 'jumat': 4, 'sabtu': 5, 'minggu': 6}
    if hari not in hari_map:
        return await event.edit("Format hari salah. Gunakan: Senin,Selasa,dst")
    hour, minute = map(int, jam.split(":"))
    job = scheduler.add_job(kirim_spam, trigger=CronTrigger(day_of_week=hari_map[hari], hour=hour, minute=minute), args=[event.client, nama])
    active_jobs[nama] = job
    await event.edit(f"Spam `{nama}` dijadwalkan tiap {hari.capitalize()} jam {jam}.")

@ayiin_cmd(pattern="spaminterval (\d+) (\S+)", allow_sudo=True)
async def spam_interval(event):
    menit, nama = int(event.pattern_match.group(1)), event.pattern_match.group(2)
    job = scheduler.add_job(kirim_spam, trigger=IntervalTrigger(minutes=menit), args=[event.client, nama])
    active_jobs[nama] = job
    await event.edit(f"Spam `{nama}` dijadwalkan tiap {menit} menit.")

@ayiin_cmd(pattern="viewspam", allow_sudo=True)
async def view_spam(event):
    if not active_jobs:
        return await event.edit("Tidak ada spam aktif.")
    teks = "Spam aktif:\n" + "\n".join(f"- {k}" for k in active_jobs)
    await event.edit(teks)

@ayiin_cmd(pattern="stoplist (\S+)", allow_sudo=True)
async def stop_spam(event):
    nama = event.pattern_match.group(1)
    job = active_jobs.get(nama)
    if job:
        job.remove()
        del active_jobs[nama]
        await event.edit(f"Spam `{nama}` dihentikan.")
    else:
        await event.edit("Tidak ada spam aktif dengan nama itu.")


CMD_HELP.update({
    "spam_jadwal": f"**Plugin :** `spam_jadwal`\
\n\n  ➥ `.setspamtime <jam>`\
\n     Untuk menjadwalkan spam pada jam tertentu.\
\n     **Contoh:** `.setspamtime 14:00`\
\n\n  ➥ `.setspamday <hari> <jam>`\
\n     Untuk menjadwalkan spam di hari dan jam tertentu.\
\n     **Contoh:** `.setspamday senin 09:00`\
\n\n  ➥ `.setspaminterval <start-jam> <end-jam> <interval-menit>`\
\n     Untuk spam berkala dalam rentang jam tertentu.\
\n     **Contoh:** `.setspaminterval 08:00 12:00 30`\
\n\n  ➥ `.stoplist <nama_list>`\
\n     Untuk menghentikan spam terjadwal dari list tertentu.\
\n\n  ➥ `.viewspam`\
\n     Melihat semua jadwal spam yang aktif.\
\n\n**Note:**\
\n• Semua mode support spam teks & forward.\
\n• Jangan lupa set grup target & isi teks/link spam seperti biasa."
})
