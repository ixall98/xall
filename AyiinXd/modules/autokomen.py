from AyiinXd import CMD_HANDLER as cmd, CMD_HELP, bot
from AyiinXd.events import ayiin_cmd
from telethon import events
from .sql_helper import autokomen_sql as db


@ayiin_cmd(pattern="setch(?: |$)(.*)")
async def add_channel(event):
    channel_id = event.pattern_match.group(1)
    if not channel_id:
        return await event.edit("Contoh: .setch @namachannel")
    if db.get_komen(channel_id):
        return await event.edit("Channel ini udah ada.")
    db.add_komen(channel_id, "", "")
    db.set_last(channel_id)
    await event.edit(f"✅ Berhasil tambah channel `{channel_id}` ke daftar auto komen.")


@ayiin_cmd(pattern="delch(?: |$)(.*)")
async def hapus_channel(event):
    channel_id = event.pattern_match.group(1)
    db.delete_komen(channel_id)
    await event.edit(f"🗑️ Berhasil hapus channel `{channel_id}`.")


@ayiin_cmd(pattern="setfilter(?: |$)(.*)")
async def add_filter(event):
    trigger = event.pattern_match.group(1)
    channel_id = db.get_last()
    if not channel_id:
        return await event.edit("Set channel dulu dong")
    komen = db.get_komen(channel_id)
    komen.trigger = trigger
    db.SESSION.commit()
    await event.edit(f"🔑 Trigger filter diset: `{trigger}`")


@ayiin_cmd(pattern="delfilter$")
async def hapus_filter(event):
    channel_id = db.get_last()
    komen = db.get_komen(channel_id)
    if not komen:
        return await event.edit("Ga ada filter.")
    komen.trigger = ""
    db.SESSION.commit()
    await event.edit("Trigger filter dihapus.")


@ayiin_cmd(pattern="setkomen(?: |$)(.*)")
async def add_komen(event):
    teks = event.pattern_match.group(1)
    channel_id = db.get_last()
    komen = db.get_komen(channel_id)
    if not komen:
        return await event.edit("Set channel dulu ya")
    komen.reply = teks
    db.SESSION.commit()
    await event.edit(f"💬 Auto komen diset: `{teks}`")


@ayiin_cmd(pattern="delkomen$")
async def hapus_komen(event):
    channel_id = db.get_last()
    komen = db.get_komen(channel_id)
    if not komen:
        return await event.edit("Belum ada komen.")
    komen.reply = ""
    db.SESSION.commit()
    await event.edit("Auto komen dihapus.")


@ayiin_cmd(pattern="listkomen$")
async def list_all(event):
    data = db.get_all_komen()
    if not data:
        return await event.edit("Ga ada data auto komen.")
    msg = "**📋 Daftar Auto Komen**\n"
    for row in data:
        msg += f"\n📢 `{row.channel_id}`\n🔑 `{row.trigger}`\n💬 `{row.reply}`\n"
    await event.edit(msg)

CMD_HELP.update({
    "autokomen": f"**Plugin :** `autokomen`\
\n\n  »  **Perintah :** `{cmd}setch @namachannel`\
\n  »  **Fungsi :** Menambahkan channel untuk auto komen.\
\n\n  »  **Perintah :** `{cmd}delch @namachannel`\
\n  »  **Fungsi :** Menghapus channel dari daftar auto komen.\
\n\n  »  **Perintah :** `{cmd}setfilter keyword`\
\n  »  **Fungsi :** Menyetel kata kunci (trigger) untuk auto komen.\
\n\n  »  **Perintah :** `{cmd}delfilter`\
\n  »  **Fungsi :** Menghapus trigger/kata kunci dari channel terakhir yang disetel.\
\n\n  »  **Perintah :** `{cmd}setkomen teks`\
\n  »  **Fungsi :** Menyetel teks auto komen yang akan dikirim saat trigger terdeteksi.\
\n\n  »  **Perintah :** `{cmd}delkomen`\
\n  »  **Fungsi :** Menghapus teks auto komen.\
\n\n  »  **Perintah :** `{cmd}listkomen`\
\n  »  **Fungsi :** Menampilkan semua channel yang disetel auto komen + trigger & teks-nya.\
"
})        
