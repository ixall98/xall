from AyiinXd import CMD_HELP, bot
from AyiinXd.ayiin import ayiin_cmd
from telethon import events
from telethon.tl.functions.messages import GetDiscussionMessageRequest
from telethon.tl.types import Message
from .sql_helper import autokomen_sql as db


# 🔁 Handler auto-komen di comment section channel
@bot.on(events.NewMessage(incoming=True))
async def komen_comment_section(event):
    if not isinstance(event.message, Message):
        return
    if not event.is_channel or event.chat.username is None:
        return

    channel_id = f"@{event.chat.username}"
    text = (event.raw_text or "").lower()
    triggers = db.get_triggers(channel_id)

    if not triggers:
        return

    for trig in triggers:
        if trig.lower() in text:
            reply_data = db.get_komen(trig)
            if not reply_data:
                continue
            try:
                discussion = await bot(GetDiscussionMessageRequest(
                    peer=event.chat_id,
                    msg_id=event.id
                ))
                if not discussion.messages:
                    continue
                reply_msg = discussion.messages[0]
                reply_chat_id = reply_msg.to_id.channel_id

                await bot.send_message(
                    entity=reply_chat_id,
                    message=reply_data.get("text"),
                    entities=reply_data.get("entities"),
                    file=reply_data.get("media"),
                    reply_to=reply_msg.id
                )
            except Exception as e:
                await bot.send_message("me", f"[ERROR] Auto-komen gagal:\n`{e}`")

# ➕ SET CHANNEL
@ayiin_cmd(pattern="setch(?: |$)(.*)")
async def _(event):
    args = event.pattern_match.group(1)
    if not args or " " not in args:
        return await event.edit("Contoh: `.setch promo @channel1 @channel2`")

    parts = args.split()
    trigger = parts[0]
    channels = parts[1:]

    for ch in channels:
        if not ch.startswith("@"):
            continue
        db.add_filter(ch, trigger)  # Tambah relasi trigger ke channel

    db.set_last(trigger)
    await event.edit(f"✅ Trigger `{trigger}` disimpan untuk: {', '.join(channels)}")


# 📝 SET KOMEN + TRIGGER
@ayiin_cmd(pattern="setkomen$")
async def _(event):
    reply = await event.get_reply_message()
    if not reply:
        return await event.edit("Reply ke pesan yang mau dijadikan komen.")

    trigger = db.get_last()
    if not trigger:
        return await event.edit("Belum set trigger. Pakai `.setch <trigger> <@channel>` dulu.")

    msg_data = {
        "text": reply.text or "",
        "entities": reply.entities,
        "media": reply.media
    }
    db.save_komen(trigger, msg_data)
    await event.edit(f"💬 Komen disimpan untuk trigger `{trigger}`")

# 🗑️ HAPUS CHANNEL
@ayiin_cmd(pattern="delch(?: |$)(.*)")
async def _(event):
    channel_id = event.pattern_match.group(1)
    if not channel_id.startswith("@"):
        channel_id = "@" + channel_id
    db.delete_komen(channel_id)
    await event.edit(f"🗑️ Channel `{channel_id}` dihapus dari daftar.")


# 🗑️ HAPUS KOMEN
@ayiin_cmd(pattern="delkomen$")
async def _(event):
    channel_id = db.get_last()
    komen = db.get_komen(channel_id)
    if not komen:
        return await event.edit("Belum ada data komen.")
    komen.reply = ""
    komen.trigger = ""
    db.SESSION.commit()
    await event.edit("✅ Auto komen & trigger dihapus.")


# 📋 LIST SEMUA
@ayiin_cmd(pattern="listkomen$")
async def _(event):
    data = db.get_all_komen()
    if not data:
        return await event.edit("Belum ada data auto komen.")
    msg = "**📋 Daftar Auto Komen**\n"
    for row in data:
        msg += f"\n📢 `{row.channel_id}`\n🔑 `{row.trigger}`\n💬 `{row.reply}`\n"
    await event.edit(msg)
