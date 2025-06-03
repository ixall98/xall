from AyiinXd import CMD_HELP, bot
from AyiinXd.ayiin import ayiin_cmd
from telethon.tl.functions.messages import GetMessagesRequest
from .sql_helper import autokomen_sql as db
from telethon.tl.types import Message
from telethon import events

# SET TRIGGER + CHANNELS
@ayiin_cmd(pattern="setch(?: |$)(.*)")
async def _(event):
    args = event.pattern_match.group(1)
    if not args or "@" not in args:
        return await event.edit("Contoh: `.setch promo @channel1 @channel2`")

    parts = args.split()
    trigger = parts[0]
    channels = [c for c in parts[1:] if c.startswith("@")]

    if not trigger or not channels:
        return await event.edit("Format salah. Contoh: `.setch promo @ch1 @ch2`")

    db.set_pending(event.sender_id, trigger, channels)
    await event.edit(f"✅ Trigger `{trigger}` siap untuk channel: `{', '.join(channels)}`.\nSekarang reply ke komen lalu ketik `.setkomen`")

# SET KOMEN (DARI REPLY)
@ayiin_cmd(pattern="setkomen$")
async def _(event):
    if not event.reply_to_msg_id:
        return await event.edit("Balas ke teks atau media yang mau dijadikan auto-komen lalu ketik `.setkomen`")

    pending = db.get_pending(event.sender_id)
    if not pending:
        return await event.edit("Belum ada trigger & channel. Gunakan `.setch <trigger> <@channel>` dulu.")

    trigger, channels = pending
    try:
        msg_obj = await bot.get_messages(event.chat_id, ids=event.reply_to_msg_id)
        for ch in channels:
            db.add_komen(ch, trigger, msg_obj.id)
        await event.edit(f"✅ Auto-komen berhasil disimpan di `{', '.join(channels)}` untuk trigger `{trigger}`.")
    except Exception as e:
        return await event.edit(f"[ERROR] Gagal simpan auto-komen:\n`{e}`")

# AUTO-KOMEN DI COMMENT SECTION
@bot.on(events.NewMessage(incoming=True))
async def auto_komen_handler(event):
    if not event.is_channel or not event.chat or not getattr(event.chat, "username", None):
        return

    channel_id = f"@{event.chat.username}"
    komen_list = db.get_komen_by_channel(channel_id)

    if not komen_list:
        return

    for komen in komen_list:
        if komen.trigger.lower() in event.raw_text.lower():
            try:
                await bot.send_message(
                    entity=event.chat_id,
                    message=komen.reply_id,
                    comment_to=event.id,
                    silent=True
                )
            except Exception as e:
                await bot.send_message("me", f"[ERROR] Auto-komen gagal:\n`{e}`")
