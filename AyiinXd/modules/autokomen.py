from AyiinXd import CMD_HELP, bot
from AyiinXd.ayiin import ayiin_cmd
from telethon import events
from telethon.tl.functions.messages import GetDiscussionMessageRequest
from telethon.tl.types import Message
from .sql_helper import autokomen_sql as db

LAST_CHANNEL = {}  # Simpan channel terakhir per userbot session


# 🔁 Auto-komen handler
@bot.on(events.NewMessage(incoming=True))
async def auto_komen_handler(event):
    if not isinstance(event.message, Message):
        return
    if not event.is_channel or event.chat.username is None:
        return

    channel_id = f"@{event.chat.username}"
    komen_list = db.get_triggers(channel_id)
    if not komen_list:
        return

    msg_text = (event.raw_text or "").lower()
    for komen in komen_list:
        if komen.trigger.lower() in msg_text and komen.reply:
            try:
                discussion = await bot(GetDiscussionMessageRequest(
                    peer=event.chat_id,
                    msg_id=event.id
                ))
                if not discussion.messages:
                    return
                reply_msg = discussion.messages[0]
                reply_chat_id = reply_msg.to_id.channel_id

                await bot.send_message(
                    entity=reply_chat_id,
                    message=komen.reply,
                    reply_to=reply_msg.id
                )
            except Exception as e:
                await bot.send_message("me", f"[ERROR] Auto-komen gagal:\n`{e}`")
            break


# ➕ SET CHANNEL
@ayiin_cmd(pattern="setch(?: |$)(.*)")
async def _(event):
    args = event.pattern_match.group(1)
    if not args:
        return await event.edit("Contoh: `.setch <trigger> <@channel1 @channel2>`")

    parts = args.split()
    trigger = parts[0]
    channels = parts[1:]

    if not channels:
        return await event.edit("Harap sebutkan minimal 1 @channel.")

    for ch in channels:
        if not ch.startswith("@"):
            ch = "@" + ch
        db.add_filter(ch, trigger)
        LAST_CHANNEL[event.sender_id] = (ch, trigger)

    await event.edit(f"✅ Trigger `{trigger}` disimpan di channel: `{', '.join(channels)}`")


# 💬 SET KOMEN (multiline & hyperlink support)
@ayiin_cmd(pattern="setkomen$")
async def _(event):
    if not event.is_reply:
        return await event.edit("Balas ke pesan yang mau dijadiin komen.")

    if event.sender_id not in LAST_CHANNEL:
        return await event.edit("Set dulu dengan `.setch <trigger> <@channel>`")

    reply = await event.get_reply_message()
    komen_text = reply.raw_text or ""
    if not komen_text:
        return await event.edit("Teks tidak ditemukan dalam balasan.")

    ch, trig = LAST_CHANNEL[event.sender_id]
    db.set_reply(ch, trig, komen_text)
    await event.edit(f"💬 Komen disimpan untuk `{trig}` di `{ch}`.")


# 🗑️ HAPUS TRIGGER
@ayiin_cmd(pattern="delkomen(?: |$)(.*)")
async def _(event):
    args = event.pattern_match.group(1).split()
    if len(args) < 2:
        return await event.edit("Contoh: `.delkomen <trigger> <@channel>`")
    trig, ch = args
    if not ch.startswith("@"):
        ch = "@" + ch
    db.delete_trigger(ch, trig)
    await event.edit(f"🗑️ Trigger `{trig}` dihapus dari `{ch}`.")


# 🗑️ HAPUS SEMUA KOMEN DI CHANNEL
@ayiin_cmd(pattern="delch(?: |$)(.*)")
async def _(event):
    ch = event.pattern_match.group(1)
    if not ch.startswith("@"):
        ch = "@" + ch
    db.delete_channel(ch)
    await event.edit(f"🗑️ Semua trigger & komen di `{ch}` dihapus.")


# 📋 LIST SEMUA KOMEN
@ayiin_cmd(pattern="listkomen$")
async def _(event):
    data = db.get_all_komen()
    if not data:
        return await event.edit("Belum ada data auto komen.")
    msg = "**📋 Daftar Auto Komen**\n\n"
    for row in data:
        msg += f"📢 `{row.channel_id}`\n🔑 `{row.trigger}`\n💬 `{row.reply}`\n\n"
    await event.edit(msg)
