from AyiinXd import CMD_HANDLER as cmd, CMD_HELP, bot
from AyiinXd.ayiin import ayiin_cmd
from telethon import events
from .sql_helper import autokomen_sql as db

# ➕ SET CHANNEL(S) untuk trigger
@ayiin_cmd(pattern="setch(?: |$)(.*)")
async def set_channels(event):
    args = event.pattern_match.group(1).split()
    if len(args) < 2:
        return await event.edit("Contoh: `.setch trigger @ch1 @ch2`")
    trigger = args[0].lower()
    channels = args[1:]
    for ch in channels:
        if not ch.startswith("@"):
            ch = f"@{ch}"
        db.add_komen(ch, trigger)
    await event.edit(f"✅ Auto-komen aktif untuk `{', '.join(channels)}` dengan trigger `{trigger}`")

# 📝 SET KOMEN (multiline/media/hyperlink)
@ayiin_cmd(pattern="setkomen(?: |$)(.*)")
async def set_komen(event):
    trigger = event.pattern_match.group(1).lower().strip()
    if not trigger:
        return await event.edit("Contoh: `.setkomen trigger` lalu reply ke pesan yang ingin dikomenkan.")
    if not event.is_reply:
        return await event.edit("Balas pesan yang ingin dijadikan komentar.")
    reply_msg = await event.get_reply_message()
    if not reply_msg:
        return await event.edit("Pesan tidak ditemukan.")

    # Ambil semua channel yang pakai trigger ini
    all_komens = db.get_komen_by_trigger(trigger)
    if not all_komens:
        return await event.edit("Belum ada channel yang diset dengan trigger ini.")

    for komen in all_komens:
        komen.reply_id = str(reply_msg.id)
        komen.reply_chat = str(reply_msg.chat_id)
    db.SESSION.commit()

    await event.edit(f"💬 Komen diset untuk trigger `{trigger}` (pesan ID: `{reply_msg.id}`)")

# 🗑️ HAPUS KOMEN UNTUK TRIGGER
@ayiin_cmd(pattern="delkomen(?: |$)(.*)")
async def del_komen(event):
    trigger = event.pattern_match.group(1).lower().strip()
    if not trigger:
        return await event.edit("Contoh: `.delkomen trigger`.")
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
async def del_channel(event):
    ch = event.pattern_match.group(1)
    if not ch.startswith("@"):
        ch = f"@{ch}"
    if not db.get_komen_by_channel(ch):
        return await event.edit("Channel tidak ditemukan.")
    db.delete_channel(ch)
    await event.edit(f"🗑️ Channel `{ch}` dihapus dari daftar auto-komen.")

# 📋 LIST SEMUA
@ayiin_cmd(pattern="listkomen$")
async def list_komen(event):
    data = db.get_all_komen()
    if not data:
        return await event.edit("Belum ada data auto komen.")
    msg = "**📋 Daftar Auto Komen**\n"
    for row in data:
        msg += f"\n📢 `{row.channel_id}`\n🔑 `{row.trigger}`\n🆔 Reply ID: `{row.reply_id or '-'}`"
    await event.edit(msg)

# 🔁 HANDLER UTAMA
@bot.on(events.NewMessage(incoming=True))
async def handler(event):
    if not event.is_channel or not getattr(event.chat, 'username', None):
        return
    ch = f"@{event.chat.username}"
    komen_list = db.get_komen_by_channel(ch)
    if not komen_list:
        return

    text = event.raw_text.lower()
    for komen in komen_list:
        if komen.trigger.lower() in text:
            if komen.reply_id and komen.reply_chat:
                try:
                    msg = await bot.get_messages(int(komen.reply_chat), ids=int(komen.reply_id))
                    await event.reply(msg)
                except Exception as e:
                    await event.reply(f"[ERROR] Auto-komen gagal:\n{e}")
            break  # stop setelah komen pertama cocok
