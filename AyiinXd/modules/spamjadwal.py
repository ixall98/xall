import asyncio
import re
from datetime import datetime, time as dtime
from telethon.errors.rpcerrorlist import FloodWaitError
from AyiinXd.ayiin import ayiin_cmd
from AyiinXd import CMD_HANDLER as cmd
from AyiinXd.modules.sql_helper.spamjadwal_sql as db

ACTIVE_SPAM = {}

async def stop_all_tasks(namalist):
    tasks = ACTIVE_SPAM.get(namalist, [])
    for task in tasks:
        task.cancel()
    ACTIVE_SPAM.pop(namalist, None)

@ayiin_cmd(pattern=r"sgrup (\w+) (.+)")
async def sgrup(event):
    namalist, grups = event.pattern_match.group(1), event.pattern_match.group(2).split()
    for grup in grups:
        add_group_to_list(namalist, grup)
    await event.edit(f"✅ Grup berhasil ditambahkan ke list `{namalist}`")

@ayiin_cmd(pattern=r"dgrup (\w+) (.+)")
async def dgrup(event):
    namalist, grups = event.pattern_match.group(1), event.pattern_match.group(2).split()
    for grup in grups:
        remove_group_from_list(namalist, grup)
    await event.edit(f"❌ Grup berhasil dihapus dari list `{namalist}`")

@ayiin_cmd(pattern=r"nspam")
async def nspam(event):
    all_lists = get_all_lists_with_groups()
    if not all_lists:
        return await event.edit("Belum ada list spam.")
    teks = "**Daftar Spam yang Disimpan:**\n"
    for nama, grups in all_lists.items():
        teks += f"\n- `{nama}`: {', '.join(grups)}"
    await event.edit(teks)

@ayiin_cmd(pattern=r"rlist (\w+)")
async def rlist(event):
    namalist = event.pattern_match.group(1)
    delete_list(namalist)
    await event.edit(f"🗑️ List `{namalist}` dan grup-grupnya berhasil dihapus.")

@ayiin_cmd(pattern=r"dbspam")
async def dbspam(event):
    if not ACTIVE_SPAM:
        return await event.edit("Tidak ada spam yang sedang berjalan.")
    teks = "**Spam yang Sedang Aktif:**\n"
    for nama in ACTIVE_SPAM:
        teks += f"- `{nama}`\n"
    await event.edit(teks)

@ayiin_cmd(pattern=r"unspam ([0-9]{1,2}:[0-9]{2}) (\d+) (\w+) (.+)", allow_sudo=True)
async def unspam(event):
    jam_stop, delay, namalist, teks = event.pattern_match.group(1), int(event.pattern_match.group(2)), event.pattern_match.group(3), event.pattern_match.group(4)

    grups_db = get_groups_by_list(namalist)
    if not grups_db:
        return await event.edit(f"List `{namalist}` kosong, tambahkan grup dengan `.sgrup {namalist} @group` terlebih dahulu.")

    now = datetime.now()
    stop_time = datetime.strptime(jam_stop, "%H:%M").replace(year=now.year, month=now.month, day=now.day)
    if stop_time < now:
        stop_time += timedelta(days=1)

    await event.edit(f"⏳ Mulai spam ke list `{namalist}`, akan berhenti jam {jam_stop}")

    async def spam_text(client, chat, teks, delay, stop_time):
        while datetime.now() < stop_time:
            try:
                await client.send_message(chat, teks, parse_mode="html")
            except Exception:
                pass
            await asyncio.sleep(delay)

    tasks = []
    for grup in grups_db:
        task = asyncio.create_task(spam_text(event.client, grup.grup, teks, delay, stop_time))
        tasks.append(task)

    ACTIVE_SPAM[namalist] = tasks

@ayiin_cmd(pattern=r"unfw ([0-9]{1,2}:[0-9]{2}) (\d+) (\w+) (https://t.me/[^/]+/(\d+))", allow_sudo=True)
async def unfw(event):
    jam_stop, delay, namalist, link, pesan_id = event.pattern_match.group(1), int(event.pattern_match.group(2)), event.pattern_match.group(3), event.pattern_match.group(4), int(event.pattern_match.group(5))
    grups_db = get_groups_by_list(namalist)
    if not grups_db:
        return await event.edit(f"List `{namalist}` kosong, tambahkan grup dengan `.sgrup {namalist} @group` terlebih dahulu.")

    now = datetime.now()
    stop_time = datetime.strptime(jam_stop, "%H:%M").replace(year=now.year, month=now.month, day=now.day)
    if stop_time < now:
        stop_time += timedelta(days=1)

    chat_regex = re.match(r"https://t.me/([^/]+)/", link)
    if not chat_regex:
        return await event.edit("Link tidak valid.")
    channel_username = chat_regex.group(1)

    await event.edit(f"⏳ Mulai spam forward, akan berhenti jam {jam_stop}")

    async def spam_forward(client, chat, channel_username, message_id, delay, stop_time):
        while datetime.now() < stop_time:
            try:
                await client.forward_messages(chat, message_id, from_peer=channel_username)
            except Exception:
                pass
            await asyncio.sleep(delay)

    tasks = []
    for grup in grups_db:
        task = asyncio.create_task(spam_forward(event.client, grup.grup, channel_username, pesan_id, delay, stop_time))
        tasks.append(task)

    ACTIVE_SPAM[namalist] = tasks

@ayiin_cmd(pattern=r"dnspam (\w+)")
async def dnspam(event):
    namalist = event.pattern_match.group(1).strip()
    if not namalist:
        return await event.edit(f"Format salah.\nContoh: `{cmd}dnspam namalist`")
    if namalist not in ACTIVE_SPAM:
        return await event.edit(f"Tidak ada spam aktif di list `{namalist}`.")
    await stop_all_tasks(namalist)
    await event.edit(f"✅ Spam pada list `{namalist}` berhasil dihentikan.")
