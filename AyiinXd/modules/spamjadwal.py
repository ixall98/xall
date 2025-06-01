from AyiinXd.modules.sql_helper.spamjadwal_sql import (
    add_group_to_list,
    remove_group_from_list,
    get_groups_by_list,
    get_all_lists,
    remove_list,
    set_user_timezone,
    get_user_timezone,
)

from datetime import datetime
import pytz
import asyncio
import re
from telethon.errors.rpcerrorlist import FloodWaitError
from AyiinXd.ayiin import ayiin_cmd
from AyiinXd import CMD_HANDLER as cmd
from AyiinXd import CMD_HELP
from AyiinXd import BOTLOG_CHATID
from telethon.utils import get_display_name

zona_map = {
    "WIB": "Asia/Jakarta",
    "WITA": "Asia/Makassar",
    "WIT": "Asia/Jayapura",
}

@ayiin_cmd(pattern="szone(?:\\s+|$)(.*)")
async def set_zona(event):
    zona_input = event.pattern_match.group(1).strip().upper()
    if zona_input not in zona_map:
        return await event.reply("Zona gak valid. Pilih salah satu: WIB, WITA, WIT.")

    set_user_timezone(str(event.sender_id), zona_input)
    await event.reply(f"Zona waktu berhasil di-set ke {zona_input}.")

@ayiin_cmd(pattern="sgrup(?:\\s+)(.*)")
async def sgrup(event):
    args = event.pattern_match.group(1).split()
    if len(args) < 2:
        return await event.reply("Format salah! .sgrup <namalist> <@grup1> [@grup2 ...]")

    namalist = args[0]
    groups = args[1:]
    for group in groups:
        add_group_to_list(namalist, group)
    await event.reply(f"Berhasil menambahkan grup ke list {namalist}:\n" + "\n".join(groups))

@ayiin_cmd(pattern="dgrup(?:\\s+)(.*)")
async def dgrup(event):
    args = event.pattern_match.group(1).split()
    if len(args) < 2:
        return await event.reply("Format salah! .dgrup <namalist> <@grup1> [@grup2 ...]")

    namalist = args[0]
    groups = args[1:]
    for group in groups:
        remove_group_from_list(namalist, group)
    await event.reply(f"Berhasil menghapus grup dari list {namalist}:\n" + "\n".join(groups))

@ayiin_cmd(pattern="dbspam(?:\\s*)$")
async def dbspam(event):
    running_spams = []  # Implementasikan tracking spam yang berjalan sesuai sistemmu
    if not running_spams:
        await event.reply("Tidak ada spam yang sedang berjalan.")
    else:
        teks = "Spam yang berjalan:\n" + "\n".join(running_spams)
        await event.reply(teks)

@ayiin_cmd(pattern="nspam(?:\\s*)$")
async def nspam(event):
    lists = get_all_lists()
    if not lists:
        await event.reply("Tidak ada nama list spam yang disetting.")
        return
    teks = "Nama list spam dan grup yang terdaftar:\n"
    for l in lists:
        teks += f"- {l.name}\n"
        groups = get_groups_by_list(l.name)
        teks += "\n".join(f"  • {g}" for g in groups) + "\n"
    await event.reply(teks)

@ayiin_cmd(pattern="rlist(?:\\s+)(.*)")
async def rlist(event):
    namalist = event.pattern_match.group(1).strip()
    if not namalist:
        return await event.reply("Format salah! .rlist <namalist>")
    remove_list(namalist)
    await event.reply(f"Nama list {namalist} dan grupnya berhasil dihapus.")

@ayiin_cmd(pattern="unspam(?:\\s+)(.*)")
async def unspam(event):
    args = event.pattern_match.group(1).split(" ", 3)
    if len(args) < 4:
        return await event.reply("Format salah! .unspam <jam_berhenti> <delay> <namalist> <teks spam>")

    jam_henti, delay, namalist, teks = args
    zona_input = get_user_timezone(str(event.sender_id))
    tz = pytz.timezone(zona_map.get(zona_input, "Asia/Jakarta"))

    try:
        jam_stop = tz.localize(datetime.strptime(jam_henti, "%H:%M"))
    except:
        return await event.reply("Format jam salah, harus HH:MM")

    groups = get_groups_by_list(namalist)
    if not groups:
        return await event.reply(f"Nama list '{namalist}' tidak ditemukan atau grupnya kosong.")

    await event.reply(f"🚀 Mulai spam ke grup di list `{namalist}` dengan delay {delay} detik. Akan berhenti jam {jam_henti} ({zona_input})")

    counter = 0
    while True:
        now = datetime.now(tz)
        if now >= jam_stop:
            if BOTLOG_CHATID:
                log_msg = (
                    f"📛 **SPAM SELESAI**\n\n"
                    f"📂 Nama List : `{namalist}`\n"
                    f"⏰ Waktu Berhenti : `{jam_henti} ({zona_input})`\n"
                    f"📊 Total Pesan Terkirim : `{counter}`\n"
                    f"🧠 Teks :\n{teks}"
                )
                await event.client.send_message(BOTLOG_CHATID, log_msg)
            break

        for group in groups:
            try:
                await event.client.send_message(group, teks)
                counter += 1
            except Exception:
                pass
            await asyncio.sleep(int(delay))
            
@ayiin_cmd(pattern="unfw(?:\\s+)(.*)")
async def unfw(event):
    args = event.pattern_match.group(1).split(" ", 3)
    if len(args) < 4:
        return await event.reply("Format salah! .unfw <jam_berhenti> <delay> <namalist> <link bubble chat dari channel>")

    jam_henti, delay, namalist, link = args
    zona_input = get_user_timezone(str(event.sender_id))
    tz = pytz.timezone(zona_map.get(zona_input, "Asia/Jakarta"))

    try:
        jam_stop = tz.localize(datetime.strptime(jam_henti, "%H:%M"))
    except:
        return await event.reply("Format jam salah, harus HH:MM")

    groups = get_groups_by_list(namalist)
    if not groups:
        return await event.reply(f"Nama list '{namalist}' tidak ditemukan atau grupnya kosong.")

    # Ambil pesan dari link bubble chat channel
    try:
        message = await event.client.get_messages(link)
    except Exception as e:
        return await event.reply(f"Gagal ambil pesan dari link: {e}")

    await event.reply(f"🚀 Mulai spam forward ke grup di list `{namalist}` dengan delay {delay} detik. Akan berhenti jam {jam_henti} ({zona_input})")

    counter = 0
    while True:
        now = datetime.now(tz)
        if now >= jam_stop:
            if BOTLOG_CHATID:
                context = event.chat_id if event.is_private else get_display_name(await event.get_chat())
                log_msg = (
                    f"📛 **SPAM FORWARD SELESAI**\n\n"
                    f"👤 Context: `{context}`\n"
                    f"📂 Nama List: `{namalist}`\n"
                    f"⏰ Waktu Berhenti: `{jam_henti} ({zona_input})`\n"
                    f"📊 Total Pesan Ter-forward: `{counter}`\n"
                    f"🔗 Link: {link}"
                )
                await event.client.send_message(BOTLOG_CHATID, log_msg)
            break

        for group in groups:
            try:
                await event.client.forward_messages(group, message)
                counter += 1
            except Exception:
                pass
            await asyncio.sleep(int(delay))

@ayiin_cmd(pattern="dnspam(?:\\s+)(.*)")
async def dnspam(event):
    namalist = event.pattern_match.group(1).strip()
    if not namalist:
        return await event.reply("Format salah! .dnspam <namalist>")
    remove_list
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

while True:
    waktu_sekarang = datetime.now(tz=timezone_bot)
    if waktu_sekarang >= waktu_berhenti:
        if BOTLOG_CHATID:
            log_msg = f"Spam forward di list `{namalist}` sudah berhenti.\nTotal pesan terkirim: {counter}."
            await event.client.send_message(BOTLOG_CHATID, log_msg)
        break
    # ... kode spam lanjut ...

@ayiin_cmd(pattern=r"dnspam (\w+)")
async def dnspam(event):
    namalist = event.pattern_match.group(1).strip()
    if not namalist:
        return await event.edit(f"Format salah.\nContoh: `{cmd}dnspam namalist`")
    if namalist not in ACTIVE_SPAM:
        return await event.edit(f"Tidak ada spam aktif di list `{namalist}`.")
    await stop_all_tasks(namalist)
    await event.edit(f"✅ Spam pada list `{namalist}` berhasil dihentikan.")


CMD_HELP.update(
    {
        "spamjadwal": f"**Plugin :** `spamjadwal`\
\n\n  »  **Perintah :** `.szone <zona waktu>`\
\n  »  **Kegunaan :** Set zona waktu bot, contoh: WIB, WITA, WIT. Default WIB.\
\n\n  »  **Perintah :** `.sgrup <nama_list> <@grup1> [@grup2 ...]`\
\n  »  **Kegunaan :** Tambah satu atau lebih grup ke dalam nama list spam.\
\n\n  »  **Perintah :** `.dgrup <nama_list> <@grup1> [@grup2 ...]`\
\n  »  **Kegunaan :** Hapus satu atau lebih grup dari nama list spam.\
\n\n  »  **Perintah :** `.dbspam`\
\n  »  **Kegunaan :** List spam yang sedang berjalan.\
\n\n  »  **Perintah :** `.nspam`\
\n  »  **Kegunaan :** Lihat semua nama list spam beserta grup di dalamnya.\
\n\n  »  **Perintah :** `.rlist <nama_list>`\
\n  »  **Kegunaan :** Hapus nama list dan semua grupnya.\
\n\n  »  **Perintah :** `.unspam <jam_berhenti> <delay> <nama_list> <teks spam>`\
\n  »  **Kegunaan :** Spam teks biasa ke semua grup di nama list sampai jam berhenti.\
\n\n  »  **Perintah :** `.unfw <jam_berhenti> <delay> <nama_list> <link bubble chat channel>`\
\n  »  **Kegunaan :** Spam forward pesan dari channel ke semua grup di nama list sampai jam berhenti.\
\n\n  »  **Perintah :** `.dnspam <nama_list>`\
\n  »  **Kegunaan :** Stop dan hapus semua jadwal spam dari nama list tersebut.\
\n\n  **NOTE:** Jam berhenti mengikuti zona waktu yang sudah di-set dengan `.szone`."
    }
                         )
