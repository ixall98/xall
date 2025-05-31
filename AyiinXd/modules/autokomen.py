from AyiinXd import CMD_HANDLER as cmd, CMD_HELP, bot
from AyiinXd.ayiin import ayiin_cmd
from telethon import events
from .sql_helper import autokomen_sql as db

# ➕ Commands Buat Atur Auto Komen

@ayiin_cmd(pattern="setch(?: |$)(.*)")
async def _(event):
    channel_id = event.pattern_match.group(1)
    if not channel_id:
        return await event.edit("Contoh: .setch @namachannel")
    if db.get_komen(channel_id):
        return await event.edit("Channel ini udah ada.")
    db.add_komen(channel_id, "", "")
    db.set_last(channel_id)
    await event.edit(f"✅ Berhasil tambah channel {channel_id} ke daftar auto komen.")

@ayiin_cmd(pattern="delch(?: |$)(.*)")
async def _(event):
    channel_id = event.pattern_match.group(1)
    db.delete_komen(channel_id)
    await event.edit(f"🗑️ Berhasil hapus channel {channel_id}.")

@ayiin_cmd(pattern="setfilter(?: |$)(.*)")
async def _(event):
    trigger = event.pattern_match.group(1)
    channel_id = db.get_last()
    if not channel_id:
        return await event.edit("Set channel dulu dong")
    komen = db.get_komen(channel_id)
    komen.trigger = trigger
    db.SESSION.commit()
    await event.edit(f"🔑 Trigger filter diset: {trigger}")

@ayiin_cmd(pattern="delfilter$")
async def _(event):
    channel_id = db.get_last()
    komen = db.get_komen(channel_id)
    if not komen:
        return await event.edit("Ga ada filter.")
    komen.trigger = ""
    db.SESSION.commit()
    await event.edit("Trigger filter dihapus.")

@ayiin_cmd(pattern="setkomen(?: |$)(.*)")
async def _(event):
    teks = event.pattern_match.group(1)
    channel_id = db.get_last()
    komen = db.get_komen(channel_id)
    if not komen:
        return await event.edit("Set channel dulu ya")
    komen.reply = teks
    db.SESSION.commit()
    await event.edit(f"💬 Auto komen diset: {teks}")

@ayiin_cmd(pattern="delkomen$")
async def _(event):
    channel_id = db.get_last()
    komen = db.get_komen(channel_id)
    if not komen:
        return await event.edit("Belum ada komen.")
    komen.reply = ""
    db.SESSION.commit()
    await event.edit("Auto komen dihapus.")

@ayiin_cmd(pattern="listkomen$")
async def _(event):
    data = db.get_all_komen()
    if not data:
        return await event.edit("Ga ada data auto komen.")
    msg = "📋 Daftar Auto Komen\n"
    for row in data:
        msg += f"\n📢 {row.channel_id}\n🔑 {row.trigger}\n💬 {row.reply}\n"
    await event.edit(msg)

# ⛓️ Handler utama yang memonitor channel post

@bot.on(events.NewMessage(incoming=True, func=lambda e: e.is_channel))
async def komen_channel(event):
    if not event.chat or not getattr(event.chat, "username", None):
        return
    komen = db.get_komen(f"@{event.chat.username}")
    if not komen:
        return
    if komen.trigger and komen.trigger not in event.raw_text:
        return
    if komen.reply:
        await event.reply(komen.reply)
