from AyiinXd import CMD_HANDLER as cmd
from AyiinXd import CMD_HELP
from AyiinXd.ayiin import ayiin_cmd
from AyiinXd.modules.sql_helper import spam_sql
from asyncio import sleep
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.tl.functions.messages import GetMessagesRequest
from telethon.tl.types import InputPeerChannel, InputMessageID
import re

@ayiin_cmd(pattern=r"setgrup (.+?)\s*\|\s*(.+)")
async def setgrup(event):
    nama = event.pattern_match.group(1).strip()
    raw = event.pattern_match.group(2).strip()
    grups = [x for x in raw.split() if x.startswith("@")] 
    if not grups:
        return await event.edit("❌ Harus pakai @username grup!")
    spam_sql.add_groups_to_list(nama, grups)
    await event.edit(f"✅ Ditambahin ke list `{nama}`: {len(grups)} grup.")

@ayiin_cmd(pattern=r"onspam (\d+)\s*\|\s*(.+?)\s*\|\s*([\s\S]+)")
async def onspam(event):
    delay = int(event.pattern_match.group(1))
    nama = event.pattern_match.group(2).strip()
    teks = event.pattern_match.group(3).strip()
    spam_sql.add_list(nama, "biasa", teks, delay)
    await event.edit(f"✅ Spam `{nama}` siap jalan dgn delay `{delay}s`.")
    grups = spam_sql.get_groups(nama)
    for g in grups:
        try:
            await event.client.send_message(g, teks)
            await sleep(delay)
        except Exception:
            continue

@ayiin_cmd(pattern=r"onfw (\d+)\s*\|\s*(.+?)\s*\|\s*(https?://t\.me/[^\s]+)")
async def onfw(event):
    delay = int(event.pattern_match.group(1))
    nama = event.pattern_match.group(2).strip()
    link = event.pattern_match.group(3).strip()
    spam_sql.add_list(nama, "fw", link, delay)
    await event.edit(f"✅ Forward spam `{nama}` aktif.")

    match = re.match(r"https://t\.me/(c/)?(-?\d+|\w+)/(\d+)", link)
    if not match:
        return await event.edit("❌ Link tidak valid!")
    chat_id = match.group(2)
    msg_id = int(match.group(3))
    if chat_id.startswith("c/") or chat_id.startswith("-100"):
        chat_id = int("-100" + chat_id.replace("c/", "").replace("-100", ""))
    grups = spam_sql.get_groups(nama)
    try:
        msg = await event.client.get_messages(chat_id, ids=msg_id)
        for g in grups:
            try:
                await event.client.forward_messages(g, msg)
                await sleep(delay)
            except Exception:
                continue
    except Exception as e:
        await event.edit(f"❌ Gagal ambil pesan dari link: {e}")

@ayiin_cmd(pattern=r"listspam$")
async def listspam(event):
    all_list = spam_sql.get_all_lists()
    if not all_list:
        return await event.edit("🚫 Ga ada list spam.")
    teks = "**📊 Daftar Spam Aktif:**\n"
    for l in all_list:
        grups = spam_sql.get_groups(l.name)
        teks += f"\n📂 `{l.name}`\n├ Grup: {len(grups)}\n├ Jenis: {l.type}\n├ Delay: {l.delay}s"
    await event.edit(teks)

@ayiin_cmd(pattern=r"listsave (.+)")
async def listsave(event):
    nama = event.pattern_match.group(1).strip()
    data = spam_sql.get_list(nama)
    if not data:
        return await event.edit("❌ List tidak ditemukan.")
    grups = spam_sql.get_groups(nama)
    teks = f"**📂 Detail List `{nama}`**\n➡️ Grup: `{', '.join(grups)}`\n➡️ Jenis: `{data.type}`\n➡️ Delay: `{data.delay}s`\n➡️ Isi: `{data.content}`"
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
