from AyiinXd import CMD_HELP, bot
from AyiinXd.ayiin import ayiin_cmd
from telethon import events, Button
from AyiinXd.modules.sql_helper import filterchannel_sql as db

# ➕ Tambah Channel ke Filter
@ayiin_cmd(pattern="addch(?: |$)(.*)")
async def add_channel(event):
    arg = event.pattern_match.group(1)
    if not arg:
        return await event.edit("Contoh: .addch @namachannel")

    try:
        entity = await bot.get_entity(arg)
        if not entity.broadcast:
            return await event.edit("Itu bukan channel, Cong!")

        cid = entity.id
        uname = entity.username
        title = entity.title

    except Exception as e:
        return await event.edit(f"Gagal ambil info channel: {e}")

    if db.get_channel(cid):
        return await event.edit("Channel ini sudah ada.")
    
    db.add_channel(cid, uname, title)
    db.set_last(cid)
    await event.edit(f"✅ Channel `{title}` berhasil ditambahkan ke daftar filter.")
    
# ❌ Hapus Channel dari Filter
@ayiin_cmd(pattern="delch(?: |$)(.*)")
async def del_channel(event):
    channel_id = event.pattern_match.group(1)
    if not channel_id:
        return await event.edit("Contoh: `.delch @namachannel`")
    db.delete_channel(channel_id)
    await event.edit(f"🗑️ Channel `{channel_id}` berhasil dihapus dari daftar filter.")

# ➕ Tambah Kata Filter
@ayiin_cmd(pattern="addfilter(?: |$)(.*)")
async def add_filter(event):
    word = event.pattern_match.group(1).strip().lower()
    if not word:
        return await event.edit("Contoh: `.addfilter kata_yang_difilter`")
    channel_id = db.get_last()
    if not channel_id:
        return await event.edit("Set channel dulu pakai `.addch @namachannel`")
    db.add_filter(channel_id, word)
    await event.edit(f"✅ Kata filter `{word}` ditambahkan untuk `{channel_id}`")

# ❌ Hapus Kata Filter
@ayiin_cmd(pattern="delfilter(?: |$)(.*)")
async def del_filter(event):
    word = event.pattern_match.group(1).strip().lower()
    if not word:
        return await event.edit("Contoh: `.delfilter kata_yang_dihapus`")
    channel_id = db.get_last()
    if not channel_id:
        return await event.edit("Set channel dulu pakai `.addch @namachannel`")
    db.remove_filter(channel_id, word)
    await event.edit(f"🗑️ Kata filter `{word}` dihapus dari `{channel_id}`")

# 📌 Set Grup Log
@ayiin_cmd(pattern="setlog$")
async def set_log_group(event):
    if not event.is_reply:
        return await event.edit("Balas pesan dari grup log, lalu ketik `.setlog`")
    replied = await event.get_reply_message()
    db.set_log_group(replied.chat_id)
    await event.edit(f"✅ Grup log diset ke `{replied.chat_id}`")

# 📋 List Semua Filter
@ayiin_cmd(pattern="listfilter$")
async def list_filter(event):
    all_data = db.get_all()
    if not all_data:
        return await event.edit("Ga ada data filter.")

    msg = "**📋 Daftar Filter Channel**\n"
    for row in all_data:
        filters = row.filters if row.filters else []
        msg += f"\n📢 `{row.channel}`\n🔑 Filter: `{', '.join(filters) if filters else 'Tidak ada'}`"
    await event.edit(msg)

# 🚨 Monitor Channel Post
@bot.on(events.NewMessage())
async def monitor_channel(event):
    chat = await event.get_chat()

    if not getattr(chat, "broadcast", False):
        return

    channel_id = chat.id
    record = db.get_channel(channel_id)
    if not record:
        return

    text = event.raw_text.lower()
    matched = [w for w in (record.filters or []) if w in text]

    if matched:
        log_group = db.get_log_group()
        if not log_group:
            return

        link = f"https://t.me/{record.username}/{event.id}" if record.username else None

        msg = (
            f"🚨 **Pesan Terfilter!**\n\n"
            f"🧷 Kata: `{', '.join(matched)}`\n"
            f"📝 Isi: {event.raw_text}\n"
            f"📡 Channel: {record.title or record.username or channel_id}"
        )

        await bot.send_message(
            log_group,
            msg,
            buttons=[[Button.url("🔎 Lihat Pesan", link)]] if link else None
        )
