from AyiinXd import CMD_HANDLER as cmd
from AyiinXd import CMD_HELP
from AyiinXd.ayiin import ayiin_cmd
from AyiinXd.modules.sql_helper import spam_sql
from asyncio import sleep
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.tl.functions.messages import GetMessagesRequest
from telethon.tl.types import InputPeerChannel, InputMessageID
import re
import asyncio

@ayiin_cmd(pattern=r"setgrup (.+?)\s*\|\s*(.+)")
async def setgrup(event):
    nama = event.pattern_match.group(1).strip()
    raw = event.pattern_match.group(2).strip()
    grups = [x for x in raw.split() if x.startswith("@")] 
    if not grups:
        return await event.edit("❌ Harus pakai @username grup!")
    spam_sql.add_groups_to_list(nama, grups)
    await event.edit(f"✅ berhasil ditambahin ke list `{nama}`: {len(grups)} grup.")


active_spams = {}

@ayiin_cmd(pattern=r"onspam (\d+)\|(.+?)\|([\s\S]*)")
async def onspamloop(event):
    delay = int(event.pattern_match.group(1))
    nama = event.pattern_match.group(2).strip()
    teks = event.pattern_match.group(3).strip()

    if nama in active_spams:
        return await event.edit(f"🚫 spam `{nama}` sudah berjalan!")

    reply = await event.get_reply_message()
    media = None
    if reply and reply.media:
        media = reply.media

    await event.edit(f"▶️ memulai spam `{nama}` dengan delay {delay}s...")

    async def spam_loop():
        grups = spam_sql.get_groups(nama)
        while True:
            for g in grups:
                try:
                    if media:
                        await event.client.send_file(g, media, caption=teks if teks else None)
                    else:
                        await event.client.send_message(g, teks)
                except Exception as e:
                    print(f"Spam error ke {g}: {e}")
                await asyncio.sleep(delay)

    task = asyncio.create_task(spam_loop())
    active_spams[nama] = task


@ayiin_cmd(pattern=r"onfw (\d+)\|(.+?)\|(https?://t\.me/[^\s]+)")
async def onfwloop(event):
    delay = int(event.pattern_match.group(1))
    nama = event.pattern_match.group(2).strip()
    link = event.pattern_match.group(3).strip()

    if nama in active_spams:
        return await event.edit(f"🚫 spam forward `{nama}` sudah berjalan!")

    await event.edit(f"▶️ memulai forward spam `{nama}` dengan delay {delay}s...")

    match = re.match(r"https://t.me/(c/)?(-?\d+|\w+)/(\d+)", link)
    if not match:
        return await event.edit("❌ Link tidak valid!")
    
    chat_part = match.group(2)
    msg_id = int(match.group(3))

    if match.group(1) == "c/":
        chat_id = int("-100" + chat_part)
    elif chat_part.isdigit() or (chat_part.startswith("-") and chat_part[1:].isdigit()):
        chat_id = int(chat_part)
    else:
        chat_id = chat_part

    async def forward_loop():
        grups = spam_sql.get_groups(nama)
        msg = await event.client.get_messages(chat_id, ids=msg_id)
        while True:
            for g in grups:
                try:
                    await event.client.forward_messages(g, msg)
                except Exception as e:
                    print(f"Error forward ke {g}: {e}")
                await asyncio.sleep(delay)

    task = asyncio.create_task(forward_loop())
    active_spams[nama] = task


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
async def list_spam(event):
    all_lists = spam_sql.get_all_lists()
    if not all_lists:
        return await event.edit("📭 Tidak ada list spam.")
    teks = "**📋 Daftar List Spam**\n\n"
    for lst in all_lists:
        aktif = "✅" if lst.name in active_spams else "❌"
        grups = spam_sql.get_groups(lst.name)
        teks += f"🔹 **{lst.name}**\n"
        teks += f"   • Jenis  : `{lst.type}`\n"
        teks += f"   • Delay  : `{lst.delay}s`\n"
        teks += f"   • Grup   : `{', '.join(grups)}`\n"
        teks += f"   • Aktif  : {aktif}\n\n"
    await event.edit(teks)

@ayiin_cmd(pattern="listsave (.+)")
async def list_save(event):
    nama = event.pattern_match.group(1).strip()
    lst = spam_sql.get_list(nama)
    if not lst:
        return await event.edit(f"❌ List `{nama}` tidak ditemukan.")
    grups = spam_sql.get_groups(nama)
    teks = f"📄 **List:** `{nama}`\n"
    teks += f"• Jenis : `{lst.type}`\n"
    teks += f"• Delay : `{lst.delay}`\n"
    teks += f"• Grup  : `{', '.join(grups)}`\n"
    teks += f"• Isi   :\n`{lst.content}`"
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
async def list_nama(event):
    all_lists = spam_sql.get_all_lists()
    if not all_lists:
        return await event.edit("📭 Tidak ada list tersedia.")
    teks = "**📌 Semua Nama List:**\n\n"
    teks += "\n".join([f"• `{lst.name}`" for lst in all_lists])
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
