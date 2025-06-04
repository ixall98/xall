from AyiinXd import CMD_HANDLER as cmd, CMD_HELP, bot
from AyiinXd.ayiin import ayiin_cmd
from telethon import events
from .sql_helper import autokomen_sql as db
from telethon.tl.functions.messages import GetRepliesRequest
from telethon.tl.types import Message
from telethon.tl.types import PeerChannel, PeerUser, PeerChat

# ✅ SET CHANNEL DENGAN TRIGGER
@ayiin_cmd(pattern="setch(?: |$)(.*)")
async def _(event):
    args = event.pattern_match.group(1).split()
    if len(args) < 2:
        return await event.edit("Contoh: `.setch trigger @ch1 @ch2`")
    trigger = args[0].lower()
    channels = args[1:]
    for ch in channels:
        if not ch.startswith("@"):
            ch = f"@{ch}"
        db.add_komen(ch, trigger, "")
    await event.edit(f"✅ Trigger `{trigger}` disimpan untuk channel: {', '.join(channels)}")

# 📝 SET KOMEN MULTILINE/MEDIA/HYPERLINK
@ayiin_cmd(pattern="setkomen(?: |$)(.*)")
async def _(event):
    trigger = event.pattern_match.group(1).lower().strip()
    if not trigger:
        return await event.edit("Contoh: `.setkomen trigger` lalu reply ke pesan yang ingin dikomen.")
    if not event.is_reply:
        return await event.edit("Balas pesan yang ingin dijadikan komentar.")

    reply_msg = await event.get_reply_message()
    if not reply_msg:
        return await event.edit("Pesan tidak ditemukan.")

    data = db.get_komen_by_trigger(trigger)
    if not data:
        return await event.edit("Trigger tidak ditemukan di channel manapun.")

    reply_to = reply_msg.to_id
    if isinstance(reply_to, PeerChannel):
      reply_chat_id = reply_to.channel_id
    elif isinstance(reply_to, PeerUser):
      reply_chat_id = reply_to.user_id
    elif isinstance(reply_to, PeerChat):
      reply_chat_id = reply_to.chat_id
    else:
      return await event.edit("Gagal ambil ID chat dari pesan yang dibalas.")

    for row in data:
       row.reply_id = reply_msg.id
       row.reply_chat = str(reply_chat_id)

     await event.edit(f"💬 Komen berhasil diset untuk trigger `{trigger}`.")

# 🗑️ HAPUS KOMEN
@ayiin_cmd(pattern="delkomen(?: |$)(.*)")
async def _(event):
    trigger = event.pattern_match.group(1).lower().strip()
    data = db.get_komen_by_trigger(trigger)
    if not data:
        return await event.edit("Trigger tidak ditemukan.")
    for row in data:
        row.reply_id = None
        row.reply_chat = None
    db.SESSION.commit()
    await event.edit(f"✅ Komentar untuk trigger `{trigger}` dihapus.")

# 🗑️ HAPUS CHANNEL
@ayiin_cmd(pattern="delch(?: |$)(.*)")
async def _(event):
    ch = event.pattern_match.group(1)
    if not ch.startswith("@"):
        ch = f"@{ch}"
    if not db.get_komen(ch):
        return await event.edit("Channel tidak ditemukan.")
    db.delete_komen(ch)
    await event.edit(f"🗑️ Channel `{ch}` dihapus dari daftar.")

# 📋 LIST SEMUA
@ayiin_cmd(pattern="listkomen$")
async def _(event):
    data = db.get_all_komen()
    if not data:
        return await event.edit("Belum ada data auto komen.")
    msg = "**📋 Daftar Auto Komen**\n"
    for row in data:
        msg += f"\n📢 `{row.channel_id}`\n🔑 `{row.trigger}`\n🆔 ID: `{row.reply_id or '-'}`"
    await event.edit(msg)

# 🔁 HANDLER KOMEN
@bot.on(events.NewMessage(incoming=True))
async def _(event):
    if not event.is_channel or not getattr(event.chat, "username", None):
        return
    ch = f"@{event.chat.username}"
    data = db.get_komen_by_channel(ch)
    if not data:
        return

    text = event.raw_text.lower()
    for komen in data:
        if komen.trigger.lower() in text and komen.reply_id and komen.reply_chat:
            try:
                original = await bot.get_messages(int(komen.reply_chat), ids=int(komen.reply_id))

                # ambil comment section via GetRepliesRequest
                replies = await bot(GetRepliesRequest(
                    peer=event.chat_id,
                    msg_id=event.id,
                    offset_id=0,
                    offset_date=None,
                    offset_rate=0,
                    limit=1
                ))

                await bot.send_message(
                    entity=event.chat_id,
                    message=original,
                    comment_to=event.id
                )
                break
            except Exception as e:
                await event.reply(f"[ERROR] Gagal komen: {e}")
