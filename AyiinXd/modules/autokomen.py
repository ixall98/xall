# modules/autokomen.py
from AyiinXd import CMD_HANDLER as cmd, CMD_HELP, client
from AyiinXd.ayiin import eor
from telethon import events
from modules.sql import autokomen_sql as db

@ayiin_cmd(pattern="setch(?: |$)(.*)")
async def _(event):
    ch = event.pattern_match.group(1).strip()
    if not ch:
        return await eor(event, "⚠️ Masukin username channel!")
    return await eor(event, f"✅ Channel `{ch}` disiapkan, sekarang set filter & komen-nya pakai `.setfilter` dan `.setkomen`.")

@ayiin_cmd(pattern="setfilter(?: |$)(.*)")
async def _(event):
    tr = event.pattern_match.group(1).strip()
    if not tr:
        return await eor(event, "⚠️ Masukin teks trigger!")
    event.client._autokomen_last_filter = tr
    await eor(event, f"✅ Trigger diset: `{tr}`. Sekarang set komen dengan `.setkomen`.")

@ayiin_cmd(pattern="setkomen(?: |$)(.*)")
async def _(event):
    komen = event.pattern_match.group(1).strip()
    if not komen:
        return await eor(event, "⚠️ Masukin isi komen!")
    try:
        trigger = event.client._autokomen_last_filter
    except AttributeError:
        return await eor(event, "⚠️ Set trigger dulu dengan `.setfilter`")
    reply = await event.get_reply_message()
    if not reply or not reply.chat.username:
        return await eor(event, "⚠️ Reply ke postingan dari channel target.")
    ch = reply.chat.username
    db.add_komen(ch, trigger, komen)
    await eor(event, f"✅ Auto komen aktif untuk channel `{ch}` jika mengandung: `{trigger}`")

@ayiin_cmd(pattern="delch(?: |$)(.*)")
async def _(event):
    ch = event.pattern_match.group(1).strip()
    db.delete_channel(ch)
    await eor(event, f"🗑️ Semua komen untuk channel `{ch}` dihapus.")

@ayiin_cmd(pattern="delfilter(?: |$)(.*)")
async def _(event):
    fl = event.pattern_match.group(1).strip()
    db.delete_trigger(fl)
    await eor(event, f"🗑️ Filter `{fl}` dihapus dari auto komen.")

@ayiin_cmd(pattern="delkomen(?: |$)(.*)")
async def _(event):
    km = event.pattern_match.group(1).strip()
    db.delete_komen_text(km)
    await eor(event, f"🗑️ Komen `{km}` dihapus dari auto komen.")

@ayiin_cmd(pattern="listkomen$")
async def _(event):
    all_data = db.get_all()
    if not all_data:
        return await eor(event, "📭 Belum ada data auto komen.")
    text = "**📄 List Auto Komen:**\n\n"
    for x in all_data:
        text += f"• 📢 Channel: `{x.channel}`\n   🔍 Filter: `{x.trigger}`\n   💬 Komen: `{x.komen}`\n\n"
    await eor(event, text)

@client.on(events.NewMessage())
async def _(event):
    if not event.chat or not event.chat.username or not event.raw_text:
        return
    data = db.get_all()
    for row in data:
        if event.chat.username == row.channel:
            if row.trigger.lower() in event.raw_text.lower():
                try:
                    await client.send_message(event.chat_id, row.komen, comment_to=event.id)
                except Exception as e:
                    print(f"[AUTO KOMEN ERROR] {e}")
