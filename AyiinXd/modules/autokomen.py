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


# ➕ SET CHANNEL
@ayiin_cmd(pattern="setch(?: |$)(.*)")
async def _(event):
    channel_id = event.pattern_match.group(1)
    if not channel_id:
        return await event.edit("Contoh: `.setch @namachannel`")
    if not channel_id.startswith("@"):
        channel_id = "@" + channel_id
    if db.get_komen(channel_id):
        return await event.edit("Channel ini udah ada.")
    db.add_komen(channel_id, "", "")
    db.set_last(channel_id)
    await event.edit(f"✅ Channel `{channel_id}` siap buat auto komen.")


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
