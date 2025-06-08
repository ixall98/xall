from AyiinXd import CMD_HELP, bot
from AyiinXd.ayiin import ayiin_cmd
from telethon import events
from telethon.tl.functions.messages import GetDiscussionMessageRequest
from telethon.tl.types import Message
from .sql_helper import autokomen_sql as db
import asyncio
import time
from telethon.errors import FloodWaitError

LAST_CHANNEL = {}  # Simpan channel terakhir per userbot sessio
last_checked = {}

@bot.on(events.NewMessage(incoming=True))
async def komen_comment_section(event):
    if not isinstance(event.message, Message):
        return

    if not event.is_channel:
        return

    try:
        chat = await event.get_chat()
    except Exception as e:
        await bot.send_message("me", f"[⚠️ Gagal Ambil Chat]\n{e}")
        return

    if not getattr(chat, "username", None):
        await bot.send_message("me", f"[⚠️ Channel Tanpa Username]\nID: `{event.chat_id}`")
        return

    cid = event.chat_id
    now = time.time()

    if cid in last_checked and now - last_checked[cid] < 10:
        return
    last_checked[cid] = now

    channel_id = f"@{chat.username.lower()}"
    text = (event.raw_text or "").lower()

    triggers = db.get_triggers(channel_id)
    if not triggers:
        await bot.send_message("me", f"[ℹ️ Tidak Ada Trigger]\nChannel: {channel_id}")
        return

    for komen in triggers:
        trigger = komen.trigger.lower()
        if trigger not in text:
            continue

        try:
            discussion_msg = await bot(GetDiscussionMessageRequest(
                peer=event.chat_id,
                msg_id=event.id
            ))

            if not discussion_msg.messages:
                await bot.send_message("me", f"[⚠️ Diskusi Tidak Ditemukan]\nChannel: {channel_id}")
                continue

            reply_msg = discussion_msg.messages[0]
            reply_chat_id = reply_msg.to_id.channel_id

            await asyncio.sleep(0.5)  # Biar smooth

            if komen.msg_id and komen.msg_chat:
                try:
                    msg = await bot.get_messages(int(komen.msg_chat), ids=int(komen.msg_id))
                    await bot.send_message(
                        entity=reply_chat_id,
                        message=msg,
                        reply_to=reply_msg.id
                    )
                    await bot.send_message("me", f"[✅ Auto-Komen Media]\nChannel: {channel_id}\nTrigger: `{trigger}`")
                except Exception as e:
                    await bot.send_message("me", f"[❌ Gagal Kirim Media]\n{e}")
            elif komen.reply:
                await bot.send_message(
                    entity=reply_chat_id,
                    message=komen.reply,
                    reply_to=reply_msg.id,
                    parse_mode="Markdown"
                )
                await bot.send_message("me", f"[✅ Auto-Komen Teks]\nChannel: {channel_id}\nTrigger: `{trigger}`")
            break  # Cuma satu trigger yang jalan

        except Exception as e:
            await bot.send_message("me", f"[❌ Error Auto-Komen]\nChannel: {channel_id}\n{e}")
            
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

    clean_channels = []
    for ch in channels:
        if not ch.startswith("@"):
            ch = "@" + ch
        db.add_filter(ch, trigger)
        clean_channels.append(ch)

    db.set_last(str(event.sender_id), channels)

    await event.edit(f"✅ Trigger `{trigger}` disimpan di channel: `{', '.join(clean_channels)}`")

# 💬 SET KOMEN (multiline & hyperlink support)
@ayiin_cmd(pattern="setkomen(?: |$)(.*)")
async def _(event):
    trigger = event.pattern_match.group(1).strip()
    if not trigger:
        return await event.edit("Contoh: `.setkomen promo` (harus reply ke pesan juga)`")

    if not event.reply_to_msg_id:
        return await event.edit("❌ Harus reply ke pesan yang mau dijadiin komen!")

    reply_msg = await event.get_reply_message()
    if not reply_msg:
        return await event.edit("❌ Gagal ambil pesan yang direply.")

    # Ambil semua channel_id dari user
    channel_ids = db.get_last(str(event.sender_id))
    if not channel_ids:
        return await event.edit("❌ Belum set channel.\nGunakan: `.setch <trigger> <@channel>`")

    # Simpan komen ke semua channel
    for ch in channel_ids:
        db.set_reply(ch, trigger, msg_id=reply_msg.id, msg_chat=str(reply_msg.chat_id))

    # Buat link preview
    try:
        link_preview = f"https://t.me/c/{str(reply_msg.chat_id)[4:]}/{reply_msg.id}"
    except Exception:
        link_preview = "pesan"

    await event.edit(
        f"✅ Disimpan ke `{len(channel_ids)}` channel:\n🔑 Trigger: `{trigger}`\n💬 Komen: [link]({link_preview})",
        link_preview=False
        )

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
