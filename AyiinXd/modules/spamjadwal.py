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
from telethon.errors.rpcerrorlist import FloodWaitError
from AyiinXd.ayiin import ayiin_cmd
from AyiinXd import CMD_HANDLER as cmd
from AyiinXd import CMD_HELP
from AyiinXd import BOTLOG_CHATID
from telethon.utils import get_display_name

# Map zona ke pytz timezone
zona_map = {
    "WIB": "Asia/Jakarta",
    "WITA": "Asia/Makassar",
    "WIT": "Asia/Jayapura",
}

# Simpan task spam yang aktif per nama list
ACTIVE_SPAM = {}

# Command set zona waktu user
@ayiin_cmd(pattern=f"szone(?:\\s+|$)(.*)")
async def set_zona(event):
    zona_input = event.pattern_match.group(1).strip().upper()
    if zona_input not in zona_map:
        return await event.reply("Zona gak valid. Pilih salah satu: WIB, WITA, WIT.")
    set_user_timezone(str(event.sender_id), zona_input)
    await event.reply(f"Zona waktu berhasil di-set ke {zona_input}.")

# Command tambah grup ke list
@ayiin_cmd(pattern=f"sgrup(?:\\s+)(.*)")
async def sgrup(event):
    args = event.pattern_match.group(1).split()
    if len(args) < 2:
        return await event.reply(f"Format salah! {cmd}sgrup <namalist> <@grup1> [@grup2 ...]")
    namalist = args[0]
    groups = args[1:]
    for group in groups:
        add_group_to_list(namalist, group)
    await event.reply(f"Berhasil menambahkan grup ke list {namalist}:\n" + "\n".join(groups))

# Command hapus grup dari list
@ayiin_cmd(pattern=f"dgrup(?:\\s+)(.*)")
async def dgrup(event):
    args = event.pattern_match.group(1).split()
    if len(args) < 2:
        return await event.reply(f"Format salah! {cmd}dgrup <namalist> <@grup1> [@grup2 ...]")
    namalist = args[0]
    groups = args[1:]
    for group in groups:
        remove_group_from_list(namalist, group)
    await event.reply(f"Berhasil menghapus grup dari list {namalist}:\n" + "\n".join(groups))

# Command list spam yang sedang berjalan
@ayiin_cmd(pattern=f"dbspam(?:\\s*)$")
async def dbspam(event):
    if not ACTIVE_SPAM:
        await event.reply("💤 Tidak ada spam yang sedang berjalan.")
    else:
        teks = "📡 Spam yang sedang berjalan:\n"
        for namalist, tasks in ACTIVE_SPAM.items():
            teks += f"• `{namalist}` - {len(tasks)} task aktif\n"
        await event.reply(teks)

# Command lihat semua list spam dan grup
@ayiin_cmd(pattern=f"nspam(?:\\s*)$")
async def nspam(event):
    lists = get_all_lists()
    if not lists:
        return await event.reply("Tidak ada nama list spam yang disetting.")
    teks = "Nama list spam dan grup yang terdaftar:\n"
    for l in lists:
        teks += f"- {l.name}\n"
        groups = get_groups_by_list(l.name)
        teks += "\n".join(f"  • {g}" for g in groups) + "\n"
    await event.reply(teks)

# Command hapus list spam dan grupnya
@ayiin_cmd(pattern=f"rlist(?:\\s+)(.*)")
async def rlist(event):
    namalist = event.pattern_match.group(1).strip()
    if not namalist:
        return await event.reply(f"Format salah! {cmd}rlist <namalist>")
    remove_list(namalist)
    await event.reply(f"Nama list {namalist} dan grupnya berhasil dihapus.")

# Command spam teks ke grup dengan jadwal berhenti dan delay
@ayiin_cmd(pattern=f"unspam(?:\\s+)(.*)")
async def unspam(event):
    args = event.pattern_match.group(1).split(" ", 3)
    if len(args) < 4:
        return await event.reply(f"Format salah! {cmd}unspam <jam_berhenti> <delay> <namalist> <teks spam>")
    jam_henti, delay, namalist, teks = args[0], args[1], args[2], args[3]

    zona_input = get_user_timezone(str(event.sender_id)) or "WIB"
    tz = pytz.timezone(zona_map.get(zona_input, "Asia/Jakarta"))

    try:
        jam_stop = tz.localize(datetime.strptime(jam_henti, "%H:%M"))
    except Exception:
        return await event.reply("Format jam salah, harus HH:MM")

    groups = get_groups_by_list(namalist)
    if not groups:
        return await event.reply(f"Nama list '{namalist}' tidak ditemukan atau grupnya kosong.")

    await event.reply(f"🚀 Mulai spam ke grup di list `{namalist}` dengan delay {delay} detik. Akan berhenti jam {jam_henti} ({zona_input})")

    async def spam_task():
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
                except FloodWaitError as e:
                    await asyncio.sleep(e.seconds)
                except Exception:
                    pass
                await asyncio.sleep(int(delay))

    task = asyncio.create_task(spam_task())
    ACTIVE_SPAM.setdefault(namalist, []).append(task)

# Command spam forward pesan dari channel ke grup dengan jadwal berhenti dan delay
@ayiin_cmd(pattern=f"unfw(?:\\s+)(.*)")
async def unfw(event):
    args = event.pattern_match.group(1).split(" ", 3)
    if len(args) < 4:
        return await event.reply(f"Format salah! {cmd}unfw <jam_berhenti> <delay> <namalist> <link bubble chat dari channel>")
    jam_henti, delay, namalist, link = args[0], args[1], args[2], args[3]

    zona_input = get_user_timezone(str(event.sender_id)) or "WIB"
    tz = pytz.timezone(zona_map.get(zona_input, "Asia/Jakarta"))

    try:
        jam_stop = tz.localize(datetime.strptime(jam_henti, "%H:%M"))
    except Exception:
        return await event.reply("Format jam salah, harus HH:MM")

    groups = get_groups_by_list(namalist)
    if not groups:
        return await event.reply(f"Nama list '{namalist}' tidak ditemukan atau grupnya kosong.")

    try:
        message = await event.client.get_messages(link)
    except Exception as e:
        return await event.reply(f"Gagal ambil pesan dari link: {e}")

    await event.reply(f"🚀 Mulai spam forward ke grup di list `{namalist}` dengan delay {delay} detik. Akan berhenti jam {jam_henti} ({zona_input})")

    async def fw_task():
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
                except FloodWaitError as e:
                    await asyncio.sleep(e.seconds)
                except Exception:
                    pass
                await asyncio.sleep(int(delay))

    task = asyncio.create_task(fw_task())
    ACTIVE_SPAM.setdefault(namalist, []).append(task)

# Command stop dan hapus semua spam di nama list tertentu
@ayiin_cmd(pattern=f"dnspam(?:\\s+)(.*)")
async def dnspam(event):
    namalist = event.pattern_match.group(1).strip()
    if not namalist:
        return await event.reply(f"Format salah! {cmd}dnspam <namalist>")
    await stop_all_tasks(namalist)
    remove_list(namalist)
    await event.reply(f"Berhasil menghentikan semua spam dan menghapus list `{namalist}`.")

# Fungsi bantu untuk stop task spam berjalan
async def stop_all_tasks(namalist):
    tasks = ACTIVE_SPAM.get(namalist, [])
    for task in tasks:
        try:
            task.cancel()
        except Exception:
            pass
    ACTIVE_SPAM.pop(namalist, None)

# Update CMD_HELP
CMD_HELP.update(
    {
        "spamjadwal": f"**Plugin :** `spamjadwal`\
\n\n  »  **Perintah :** `{cmd}szone <zona waktu>`\
\n  »  **Kegunaan :** Set zona waktu bot, contoh: WIB, WITA, WIT. Default WIB.\
\n  »  **Perintah :** `{cmd}sgrup <nama_list> <@grup1> [@grup2 ...]`\
\n  »  **Kegunaan :** Tambah satu atau lebih grup ke dalam nama list spam.\
\n  »  **Perintah :** `{cmd}dgrup <nama_list> <@grup1> [@grup2 ...]`\
\n  »  **Kegunaan :** Hapus satu atau lebih grup dari nama list spam.\
\n  »  **Perintah :** `{cmd}dbspam`\
\n  »  **Kegunaan :** List spam yang sedang berjalan.\
\n  »  **Perintah :** `{cmd}nspam`\
\n  »  **Kegunaan :** Lihat semua nama list spam beserta grup di dalamnya.\
\n  »  **Perintah :** `{cmd}rlist <nama_list>`\
\n  »  **Kegunaan :** Hapus nama list dan semua grupnya.\
\n  »  **Perintah :** `{cmd}unspam <jam_berhenti> <delay> <nama_list> <teks spam>`\
\n  »  **Kegunaan :** Spam teks biasa ke semua grup di nama list sampai jam berhenti.\
\n  »  **Perintah :** `{cmd}unfw <jam_berhenti> <delay> <nama_list> <link bubble chat channel>`\
\n  »  **Kegunaan :** Spam forward pesan dari channel ke semua grup di nama list sampai jam berhenti.\
\n  »  **Perintah :** `{cmd}dnspam <nama_list>`\
\n  »  **Kegunaan :** Stop dan hapus semua jadwal spam dari nama list tersebut.\
\n\n**NOTE:** Jam berhenti mengikuti zona waktu yang sudah di-set dengan `{cmd}szone`."
    }
    )
