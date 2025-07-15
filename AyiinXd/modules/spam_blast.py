from AyiinXd import CMD_HANDLER as cmd
from AyiinXd import CMD_HELP
from AyiinXd.ayiin import ayiin_cmd
from AyiinXd.modules.sql_helper import spam_sql
from asyncio import sleep
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.tl.functions.messages import GetMessagesRequest
from telethon.tl.types import InputPeerChannel, InputMessageID
from telethon.errors import FloodWaitError
from datetime import datetime
import re
import asyncio

@ayiin_cmd(pattern=r"setgrup (.+?)\s*\|\s*(.+)")
async def setgrup(event):
    nama = event.pattern_match.group(1).strip()
    raw = event.pattern_match.group(2).strip()
    grups = [x for x in raw.split() if x.startswith("@")] 
    if not grups:
        return await event.edit("❌ Harus pakai @username grup!")

    # ✅ Cek apakah list-nya sudah ada, kalau belum bikin default
    if not spam_sql.get_list(nama):
        spam_sql.add_list(nama, "biasa", "", 10)  # bikin default list

    spam_sql.add_groups_to_list(nama, grups)
    await event.edit(f"✅ berhasil ditambahkan ke list `{nama}`: {len(grups)} grup.")

active_spams = {}

@ayiin_cmd(pattern=r"onspam (\d+)\s+(\S+)\s+([\s\S]+)")
async def onspamloop(event):
    delay = int(event.pattern_match.group(1))
    nama  = event.pattern_match.group(2).strip()
    teks  = event.pattern_match.group(3).strip()

    spam_sql.update_list(nama, "spam", delay, teks)
    if nama in active_spams:
        return await event.edit(f"🚫 spam `{nama}` sudah berjalan!")

    reply = await event.get_reply_message()
    media = reply.media if reply and reply.media else None
    await event.edit(f"▶️ Memulai spam `{nama}`…")

    async def spam_loop():
        try:
            while True:
                grups = spam_sql.get_groups(nama)            # selalu refresh
                tasks = []
                for g in grups:
                    async def send(gdest):                   # fungsi mini agar try/except per-grup
                        try:
                            if media:
                                await event.client.send_file(gdest, media,
                                                            caption=teks or "", parse_mode="html")
                            else:
                                await event.client.send_message(gdest, teks, parse_mode="html")
                            print(f"[SPAM] {nama}->{gdest} {datetime.now():%H:%M:%S}")
                        except FloodWaitError as e:
                            print(f"[FLOOD] {gdest}: tunggu {e.seconds}s")
                            await asyncio.sleep(e.seconds)
                        except Exception as e:
                            print(f"[ERR] spam {gdest}: {e}")
                    tasks.append(send(g))
                # jalankan semua, tapi jangan crash bila satu error
                await asyncio.gather(*tasks, return_exceptions=True)
                await asyncio.sleep(delay)
        except asyncio.CancelledError:
            print(f"[SPAM] Loop `{nama}` dihentikan.")

    active_spams[nama] = asyncio.create_task(spam_loop())

@ayiin_cmd(pattern=r"onfw (\d+)\s+(\S+)\s+(https?://t\.me/[^\s]+)")
async def onfwloop(event):
    delay = int(event.pattern_match.group(1))
    nama  = event.pattern_match.group(2).strip()
    link  = event.pattern_match.group(3).strip()

    spam_sql.update_list(nama, "forward", delay, link)
    if nama in active_spams:
        return await event.edit(f"🚫 spam forward `{nama}` sudah berjalan!")

    m = re.match(r"https://t.me/(c/)?(-?\d+|\w+)/(\d+)", link)
    if not m:
        return await event.edit("❌ Link tidak valid!")

    chat_part, msg_id = m.group(2), int(m.group(3))
    chat_id = int("-100"+chat_part) if m.group(1)=="c/" else (int(chat_part) if chat_part.isdigit() else chat_part)
    msg = await event.client.get_messages(chat_id, ids=msg_id)
    await event.edit(f"▶️ Memulai forward `{nama}`…")

    async def fw_loop():
        try:
            while True:
                grups = spam_sql.get_groups(nama)
                tasks = []
                for g in grups:
                    async def fwd(gdest):
                        try:
                            await event.client.forward_messages(gdest, msg)
                            print(f"[FW] {nama}->{gdest} {datetime.now():%H:%M:%S}")
                        except FloodWaitError as e:
                            print(f"[FLOOD] {gdest}: tunggu {e.seconds}s")
                            await asyncio.sleep(e.seconds)
                        except Exception as e:
                            print(f"[ERR] fw {gdest}: {e}")
                    tasks.append(fwd(g))
                await asyncio.gather(*tasks, return_exceptions=True)
                await asyncio.sleep(delay)
        except asyncio.CancelledError:
            print(f"[FW] Loop `{nama}` dihentikan.")

    active_spams[nama] = asyncio.create_task(fw_loop())

@ayiin_cmd(pattern=r"stopspam (.+)")
async def stopspam(event):
    nama = event.pattern_match.group(1).strip()
    task = active_spams.get(nama)
    if not task:
        return await event.edit(f"❌ Spam `{nama}` tidak sedang berjalan.")
    task.cancel()
    active_spams.pop(nama)
    await event.edit(f"🛑 Spam `{nama}` berhasil dihentikan.")
    
@ayiin_cmd(pattern="listspam$")
async def list_all_spam(event):
    lists = spam_sql.get_all_lists()
    if not lists:
        return await event.edit("📭 Tidak ada data spam tersimpan.")

    teks = "**📋 Daftar List Spam:**\n\n"
    for l in lists:
        grups = spam_sql.get_groups(l.name)
        status = "Aktif ✅" if l.name in active_spams else "Nonaktif ❌"
        teks += f"• `{l.name}` [{l.type}] - {status}\n"
        teks += f"   Grup: {len(grups)} | Delay: {l.delay}s\n\n"
    await event.edit(teks)

@ayiin_cmd(pattern="listsave (.+)")
async def list_save(event):
    nama = event.pattern_match.group(1).strip()
    data = spam_sql.get_list(nama)
    if not data:
        return await event.edit(f"❌ List `{nama}` tidak ditemukan.")

    grups = spam_sql.get_groups(nama)
    teks = f"📄 **List:** `{nama}`\n"
    teks += f"• Jenis : `{data.type}`\n"
    teks += f"• Delay : `{data.delay}` detik\n"
    teks += f"• Grup : {len(grups)}\n"
    teks += f"• Teks/Link:\n`{data.content}`\n"
    teks += "\n📌 **Daftar Grup:**\n"
    for g in grups:
        teks += f" - `{g}`\n"
    await event.edit(teks)

@ayiin_cmd(pattern=r"delgrup (.+?) (.+)")
async def delgrup(event):
    nama = event.pattern_match.group(1).strip()
    grup = event.pattern_match.group(2).strip()
    spam_sql.delete_group(nama, grup)
    await event.edit(f"✅ Grup `{grup}` dihapus dari `{nama}`.")

@ayiin_cmd(pattern=r"dellist (.+)")
async def dellist(event):
    nama = event.pattern_match.group(1).strip()
    spam_sql.delete_list(nama)
    await event.edit(f"🗑️ List `{nama}` dan semua isinya dihapus.")

@ayiin_cmd(pattern="slist$")
async def show_all_spam_lists(event):
    lists = spam_sql.get_all_lists()
    if not lists:
        return await event.edit("📭 Belum ada list yang disimpan.")

    teks = "**📦 Semua Nama List Spam yang Punya Grup:**\n\n"
    count = 0
    for l in lists:
        grups = spam_sql.get_groups(l.name)
        if grups:
            count += 1
            teks += f"• `{l.name}` ({len(grups)} grup)\n"

    if count == 0:
        teks = "📭 Belum ada list yang punya grup."
        
    await event.edit(teks)
        
CMD_HELP.update(
    {
        "spamloop": f"**Plugin : **`spamloop`\
        \n\n  »  **Perintah :** `{cmd}onspam <delay>|<namalist>|<teks>`\
        \n  »  **Kegunaan :** Spam teks ke semua grup di list. Bisa reply media juga.\
        \n\n  »  **Perintah :** `{cmd}onfw <delay>|<namalist>|<link channel>`\
        \n  »  **Kegunaan :** Spam forward pesan dari channel ke semua grup di list.\
        \n\n  »  **Perintah :** `{cmd}stopspam <namalist>`\
        \n  »  **Kegunaan :** Memberhentikan spam yang sedang berjalan di list tersebut.\
        \n\n  »  **Perintah :** `{cmd}setgrup <namalist>|<@usergrup1> <@usergrup2>`\
        \n  »  **Kegunaan :** Menyimpan banyak grup ke dalam satu list.\
        \n\n  »  **Perintah :** `{cmd}listgrup <namalist>`\
        \n  »  **Kegunaan :** Menampilkan semua grup yang tersimpan dalam nama list.\
        \n\n  »  **Perintah :** `{cmd}listsave <namalist>`\
        \n  »  **Kegunaan :** Menampilkan detail isi list (grup & teks sebar).\
        \n\n  »  **Perintah :** `{cmd}slist`\
        \n  »  **Kegunaan :** Menampilkan semua nama list spam yang tersimpan.\
        \n\n  »  **Perintah :** `{cmd}delgrup <namalist> <@usergrup>`\
        \n  »  **Kegunaan :** Menghapus grup tertentu dari nama list.\
        \n\n  »  **Perintah :** `{cmd}dellist <namalist>`\
        \n  »  **Kegunaan :** Menghapus seluruh list beserta grup & teksnya.\
        \n\n  •  **NOTE :**\
        \n    - Jangan ada spasi di antara `|`\
        \n    - Delay dalam detik (angka)\
        \n    - Bisa spam media (reply dulu pesan yang ingin disebar)\
        \n    - Gunakan dengan bijak, spam berlebihan bisa dibanned telegram!"
    }
    )
