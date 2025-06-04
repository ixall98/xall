from AyiinXd import CMD_HANDLER as cmd, CMD_HELP, bot
from AyiinXd.ayiin import ayiin_cmd
from telethon import events
from .sql_helper import autokomen_sql as db
from telethon.tl.functions.messages import GetRepliesRequest, SendMessageRequest
from telethon.tl.types import Message
from telethon.tl.types import InputPeerChannel, PeerChannel, PeerUser, PeerChat
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.messages import GetDiscussionMessageRequest
from telethon.tl.types import Message

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

    reply_chat_id = reply_msg.chat_id

    for row in data:
        row.reply_id = reply_msg.id
        row.reply_chat = str(reply_chat_id)
    db.SESSION.commit()

@bot.on(events.NewMessage(incoming=True))
async def autokomen_trigger(event):
    if not event.is_channel or event.chat is None:
        return

    text = event.raw_text.lower()
    if not text:
        return

    # Ambil semua trigger dari DB
    all_data = db.get_all_autokomen()

    for row in all_data:
        if row.trigger.lower() in text and str(event.chat_id) in row.channels:
            try:
                channel = await client(GetFullChannelRequest(event.chat_id))
                input_peer = InputPeerChannel(
                    channel.channel.id,
                    channel.channel.access_hash
                )

                await client(SendMessageRequest(
                    peer=input_peer,
                    message=row.komen,
                    reply_to_msg_id=int(row.reply_id)
                ))
            except Exception as e:
                await event.reply(f"[ERROR] Gagal komen: {e}")
                
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
# 🔁 Handler auto-komen di comment section channel
@bot.on(events.NewMessage(incoming=True))
async def komen_comment_section(event):
    if not isinstance(event.message, Message):
        return
    if not event.is_channel or event.chat.username is None:
        return

    channel_id = f"@{event.chat.username}"
    komen = db.get_komen(channel_id)

    if not komen or not komen.trigger or not komen.reply:
        return

    if komen.trigger.lower() not in (event.raw_text or "").lower():
        return

    try:
        discussion = await bot(GetDiscussionMessageRequest(
            peer=event.chat_id,
            msg_id=event.id
        ))

        if not discussion.messages:
            return

        reply_msg = discussion.messages[0]
        reply_chat_id = reply_msg.to_id.channel_id  # 🔧 FIXED LINE

        await bot.send_message(
            entity=reply_chat_id,
            message=komen.reply,
            reply_to=reply_msg.id
        )
    except Exception as e:
        await bot.send_message("me", f"[ERROR] Auto-komen gagal:\n`{e}`")
