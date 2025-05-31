from AyiinXd import CMD_HELP, bot
from AyiinXd.events import ayiin_cmd
from telethon import events
from .sql_helper import filterchannel_sql as db

# ➕ Tambah Channel yang Mau Difilter
@ayiin_cmd(pattern="addch(?: |$)(.*)")
async def add_channel(event):
    channel_id = event.pattern_match.group(1)
    if not channel_id:
        return await event.edit("Contoh: .addch @namachannel")
    if db.get_channel(channel_id):
        return await event.edit("Channel ini sudah ada.")
    db.add_channel(channel_id)
    db.set_last(channel_id)
    await event.edit(f"✅ Channel `{channel_id}` berhasil ditambahkan ke daftar filter.")

# ❌ Hapus Channel dari Daftar
@ayiin_cmd(pattern="delch(?: |$)(.*)")
async def del_channel(event):
    channel_id = event.pattern_match.group(1)
    db.delete_channel(channel_id)
    await event.edit(f"🗑️ Channel `{channel_id}` berhasil dihapus dari daftar filter.")

# 🎯 Tambah Kata Filter
@ayiin_cmd(pattern="addfilter(?: |$)(.*)")
async def add_filter(event):
    word = event.pattern_match.group(1).lower()
    channel_id = db.get_last()
    if not channel_id:
        return await event.edit("Set channel dulu pakai .addch")
    db.add_filter(channel_id, word)
    await event.edit(f"✅ Kata filter `{word}` ditambahkan untuk `{channel_id}`")

# 🧹 Hapus Kata Filter
@ayiin_cmd(pattern="delfilter(?: |$)(.*)")
async def del_filter(event):
    word = event.pattern_match.group(1).lower()
    channel_id = db.get_last()
    db.remove_filter(channel_id, word)
    await event.edit(f"🗑️ Kata filter `{word}` dihapus dari `{channel_id}`")

# 📝 Set Grup Log
@ayiin_cmd(pattern="setlog$")
async def set_log_group(event):
    if not event.is_reply:
        return await event.edit("Balas pesan dari grup log, lalu ketik .setlog")
    replied = await event.get_reply_message()
    db.set_log_group(replied.chat_id)
    await event.edit(f"✅ Grup log diset ke `{replied.chat_id}`")

# 📃 Lihat Semua Data
@ayiin_cmd(pattern="listfilter$")
async def list_filter(event):
    all_data = db.get_all()
    if not all_data:
        return await event.edit("Ga ada data filter.")
    msg = "**📋 Daftar Filter Channel**\n"
    for row in all_data:
        msg += f"\n📢 `{row.channel}`\n🔑 Filter: `{', '.join(row.filters)}`"
    await event.edit(msg)

# 🔍 Listener buat pantau postingan channel
async def monitor_channel(event):
    if event.chat.username is None:
        return
    channel_id = f"@{event.chat.username}"
    record = db.get_channel(channel_id)
    if not record:
        return

    text = event.raw_text.lower()
    matched = [w for w in record.filters if w in text]
    if matched:
        link = f"https://t.me/{event.chat.username}/{event.id}"
        msg = (
            f"🚨 **Pesan Terfilter!**\n\n"
            f"🧷 Kata: `{', '.join(matched)}`\n"
            f"📝 Isi: {event.raw_text}\n"
            f"📡 Channel: {channel_id}"
        )
        await bot.send_message(
            db.get_log_group(),
            msg,
            buttons=[[("🔎 Lihat Pesan", link)]]
        )

bot.add_event_handler(monitor_channel, events.NewMessage(incoming=True, chats=None))
