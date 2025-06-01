# modules/spamjadwal.py

import asyncio
import re
from datetime import datetime, time as dtime
from telethon.errors.rpcerrorlist import FloodWaitError
from AyiinXd.ayiin import ayiin_cmd
from AyiinXd import CMD_HANDLER as cmd
from AyiinXd.modules.sql_helper import spamjadwal_sql as db

ACTIVE_SPAM = {}  # key: namalist, value: list of asyncio.Tasks

def parse_time(tstr):
    try:
        h, m = map(int, tstr.split(":"))
        return dtime(hour=h, minute=m)
    except:
        return None

async def stop_all_tasks(namalist):
    tasks = ACTIVE_SPAM.get(namalist, [])
    for task in tasks:
        task.cancel()
    ACTIVE_SPAM.pop(namalist, None)

@ayiin_cmd(pattern=r"sgrup (.+)")
async def sgrup(event):
    args = event.pattern_match.group(1)
    parts = args.split()
    if len(parts) < 2:
        return await event.edit(f"Format salah.\nContoh: `{cmd}sgrup namalist @grup1 @grup2`")
    namalist = parts[0]
    grups = parts[1:]
    added = []
    for g in grups:
        if not g.startswith("@"):
            continue
        db.add_grup(namalist, g)
        added.append(g)
    await event.edit(f"Berhasil tambah grup ke list `{namalist}`:\n" + "\n".join(added))

@ayiin_cmd(pattern=r"dgrup (.+)")
async def dgrup(event):
    args = event.pattern_match.group(1)
    parts = args.split()
    if len(parts) < 2:
        return await event.edit(f"Format salah.\nContoh: `{cmd}dgrup namalist @grup1 @grup2`")
    namalist = parts[0]
    grups = parts[1:]
    removed = []
    for g in grups:
        if not g.startswith("@"):
            continue
        db.remove_grup(namalist, g)
        removed.append(g)
    await event.edit(f"Berhasil hapus grup dari list `{namalist}`:\n" + "\n".join(removed))

@ayiin_cmd(pattern="nspam$")
async def nspam(event):
    all_lists = db.get_all_lists()
    if not all_lists:
        return await event.edit("Belum ada list spam yang diset.")
    res = {}
    for row in all_lists:
        res.setdefault(row.namalist, []).append(row.grup)
    teks = ""
    for namalist, grups in res.items():
        teks += f"List `{namalist}`:\n"
        teks += "\n".join(grups) + "\n\n"
    await event.edit(teks)

@ayiin_cmd(pattern=r"rlist (.+)")
async def rlist(event):
    namalist = event.pattern_match.group(1).strip()
    if not namalist:
        return await event.edit(f"Format salah.\nContoh: `{cmd}rlist namalist`")
    await stop_all_tasks(namalist)
    db.delete_list(namalist)
    await event.edit(f"List `{namalist}` dan grupnya sudah dihapus dan spam dihentikan jika aktif.")

@ayiin_cmd(pattern="dbspam$")
async def dbspam(event):
    if not ACTIVE_SPAM:
        return await event.edit("Tidak ada spam yang sedang berjalan.")
    teks = "Spam aktif:\n"
    for namalist, tasks in ACTIVE_SPAM.items():
        teks += f"- List `{namalist}`, jumlah task: {len(tasks)}\n"
    await event.edit(teks)

async def spam_text(client, chat, teks, delay, stop_time):
    while True:
        now = datetime.now().time()
        if now >= stop_time:
            break
        try:
            await client.send_message(chat, teks)
            await asyncio.sleep(delay)
        except FloodWaitError as e:
            await asyncio.sleep(e.seconds)
        except asyncio.CancelledError:
            break
        except Exception:
            break

async def spam_media(client, chat, reply_msg, delay, stop_time):
    while True:
        now = datetime.now().time()
        if now >= stop_time:
            break
        try:
            await reply_msg.forward_to(chat)
            await asyncio.sleep(delay)
        except FloodWaitError as e:
            await asyncio.sleep(e.seconds)
        except asyncio.CancelledError:
            break
        except Exception:
            break

async def spam_forward(client, chat, from_chat, msg_id, delay, stop_time):
    while True:
        now = datetime.now().time()
        if now >= stop_time:
            break
        try:
            await client.forward_messages(chat, msg_id, from_chat)
            await asyncio.sleep(delay)
        except FloodWaitError as e:
            await asyncio.sleep(e.seconds)
        except asyncio.CancelledError:
            break
        except Exception:
            break

@ayiin_cmd(pattern=r"unspam (.+)")
async def unspam(event):
    args = event.pattern_match.group(1)
    parts = args.split(maxsplit=2)
    if len(parts) < 2 and not event.reply_to_msg_id:
        return await event.edit(f"Format salah.\nContoh:\n`{cmd}unspam 12:00 5 Halo semua!`\natau balas pesan dengan:\n`{cmd}unspam 12:00 5`")
    jam_stop = parts[0]
    try:
        delay = int(parts[1])
    except:
        return await event.edit("Delay harus angka detik (contoh: 5)")

    teks = parts[2] if len(parts) == 3 else None

    stop_time = parse_time(jam_stop)
    if not stop_time:
        return await event.edit("Format jam salah, harus HH:MM (contoh 12:00)")

    namalist = "default"
    grups_db = db.get_grup_by_list(namalist)
    if not grups_db:
        return await event.edit(f"List `{namalist}` kosong, tambahkan grup dengan `.sgrup {namalist} @group` terlebih dahulu.")

    await event.edit(f"Mulai spam ke {len(grups_db)} grup, akan berhenti jam {jam_stop}")

    reply_msg = None
    if event.reply_to_msg_id:
        reply_msg = await event.get_reply_message()

    tasks = []
    for grup in grups_db:
        chat = grup.grup
        if teks:
            task = asyncio.create_task(spam_text(event.client, chat, teks, delay, stop_time))
        elif reply_msg:
            task = asyncio.create_task(spam_media(event.client, chat, reply_msg, delay, stop_time))
        else:
            await event.edit("Teks spam tidak ditemukan dan tidak ada pesan balasan untuk spam media.")
            return
        tasks.append(task)

    ACTIVE_SPAM[namalist] = tasks

@ayiin_cmd(pattern=r"unfw (.+)")
async def unfw(event):
    args = event.pattern_match.group(1)
    parts = args.split(maxsplit=2)
    if len(parts) < 2:
        return await event.edit(f"Format salah.\nContoh:\n`{cmd}unfw 12:00 5 https://t.me/jasebxall/6`\n(Spam forward pesan dari channel ke grup)")

    jam_stop = parts[0]
    try:
        delay = int(parts[1])
    except:
        return await event.edit("Delay harus angka detik (contoh: 5)")

    if len(parts[1].split()) < 2 and len(parts) < 3:
        return await event.edit("Harap sertakan link pesan bubble chat channel.")

    link = parts[2] if len(parts) >= 3 else parts[1].split(maxsplit=1)[1]

    stop_time = parse_time(jam_stop)
    if not stop_time:
        return await event.edit("Format jam salah, harus HH:MM (contoh 12:00)")

    match = re.search(r"t\.me\/([^\/]+)\/(\d+)", link)
    if not match:
        return await event.edit("Link pesan channel tidak valid.")

    channel_username = match.group(1)
    pesan_nomor = int(match.group(2))

    namalist = "default"
    grups_db = db.get_grup_by_list(namalist)
    if not grups_db:
        return await event.edit(f"List `{namalist}` kosong, tambahkan grup dengan `.sgrup {namalist} @group` terlebih dahulu.")

    await event.edit(f"Mulai spam forward, akan berhenti jam {jam_stop}")

    tasks = []
    for grup in grups_db:
        chat = grup.grup
        task = asyncio.create_task(
            spam_forward(event.client, chat, channel_username, pesan_nomor, delay, stop_time)
        )
        tasks.append(task)

    ACTIVE_SPAM[namalist] = tasks

@ayiin_cmd(pattern=r"dnspam (.+)")
async def dnspam(event):
    namalist = event.pattern_match.group(1).strip()
    if not namalist:
        return await event.edit(f"Format salah.\nContoh: `{cmd}dnspam namalist`")
    if namalist not in ACTIVE_SPAM:
        return await event.edit(f"Tidak ada spam aktif di list `{namalist}`.")
    await stop_all_tasks(namalist)
    await event.edit(f"Spam pada list `{namalist}` berhasil dihentikan.")                                      
