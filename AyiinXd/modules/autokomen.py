from AyiinXd import CMD_HANDLER as cmd, CMD_HELP, bot
from AyiinXd.ayiin import ayiin_cmd
from telethon import events
from .sql_helper import autokomen_sql as db

# ➕ SET CHANNEL
@ayiin_cmd(pattern="setch(?: |$)(.*)")
async def _(event):
    channel_id = event.pattern_match.group(1)
    if not channel_id:
        return await event.edit("Contoh: `.setch @namachannel`")
    if db.get_komen(channel_id):
        return await event.edit("Channel ini udah ada.")
    db.add_komen(channel_id, "", "")
    db.set_last(channel_id)
    await event.edit(f"✅ Channel `{channel_id}` siap buat auto komen.")

# 🗑️ HAPUS CHANNEL
@ayiin_cmd(pattern="delch(?: |$)(.*)")
async def _(event):
    channel_id = event.pattern_match.group(1)
    db.delete_komen(channel_id)
    await event.edit(f"🗑️ Channel `{channel_id}` dihapus dari daftar.")

# 📝 SET KOMEN + TRIGGER
@ayiin_cmd(pattern="setkomen(?: |$)(.*)")
async def _(event):
    args = event.pattern_match.group(1)
    if not args or " " not in args:
        return await event.edit("Contoh: `.setkomen Halo semua promo`")
    
    *komen_parts, trigger = args.split()
    teks_komen = " ".join(komen_parts)

    channel_id = db.get_last()
    if not channel_id:
        return await event.edit("Belum set channel. Pakai `.setch @namachannel` dulu.")

    komen = db.get_komen(channel_id)
    if not komen:
        return await event.edit("Channel belum terdaftar.")
    
    komen.reply = teks_komen
    komen.trigger = trigger
    db.SESSION.commit()
    await event.edit(f"💬 Auto komen: `{teks_komen}`\n🔑 Trigger: `{trigger}`")

# 🗑️ HAPUS KOMEN + TRIGGER
@ayiin_cmd(pattern="delkomen$")
async def _(event):
    channel_id = db.get_last()
    komen = db.get_komen(channel_id)
    if not komen:
        return await event.edit("Belum ada data komen.")
    komen.reply = ""
    komen.trigger = ""
    db.SESSION.commit()
    await event.edit("Auto komen & trigger dihapus.")

# 📋 LIHAT SEMUA
@ayiin_cmd(pattern="listkomen$")
async def _(event):
    data = db.get_all_komen()
    if not data:
        return await event.edit("Belum ada data auto komen.")
    msg = "**📋 Daftar Auto Komen**\n"
    for row in data:
        msg += f"\n📢 `{row.channel_id}`\n🔑 `{row.trigger}`\n💬 `{row.reply}`\n"
    await event.edit(msg)

# 🔁 HANDLER OTOMATIS
async def komen_channel(event):
    if event.chat.username is None:
        return
    komen = db.get_komen(f"@{event.chat.username}")
    if not komen:
        return
    if komen.trigger and komen.trigger not in event.raw_text:
        return
    if komen.reply:
        await event.reply(komen.reply)

bot.add_event_handler(komen_channel, events.NewMessage(incoming=True))
