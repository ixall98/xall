from AyiinXd import CMD_HANDLER as cmd, CMD_HELP, bot
from AyiinXd.ayiin import ayiin_cmd
from telethon import events
from telethon.tl.functions.messages import GetDiscussionMessageRequest
from telethon.tl.types import Message

from .sql_helper import autokomen_sql as db


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


@ayiin_cmd(pattern="setkomen(?: |$)(.*)")
async def _(event):
    args = event.pattern_match.group(1)
    if not args or " " not in args:
        return await event.edit("Contoh: `.setkomen open ubot`")

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


@ayiin_cmd(pattern="delch(?: |$)(.*)")
async def _(event):
    channel_id = event.pattern_match.group(1)
    if not channel_id.startswith("@"):
        channel_id = "@" + channel_id
    db.delete_komen(channel_id)
    await event.edit(f"🗑️ Channel `{channel_id}` dihapus dari daftar.")


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


@ayiin_cmd(pattern="listkomen$")
async def _(event):
    data = db.get_all_komen()
    if not data:
        return await event.edit("Belum ada data auto komen.")
    msg = "**📋 Daftar Auto Komen**\n"
    for row in data:
        msg += f"\n📢 `{row.channel_id}`\n🔑 `{row.trigger}`\n💬 `{row.reply}`\n"
    await event.edit(msg)


# 🔁 AUTO KOMEN DI COMMENT SECTION
@bot.on(events.NewMessage(incoming=True))
async def komen_post(event):
    if not isinstance(event.message, Message):
        return
    if not event.is_channel or event.chat.username is None:
        return

    channel_id = f"@{event.chat.username}"
    komen = db.get_komen(channel_id)
    if not komen or not komen.reply or not komen.trigger:
        return

    teks = (event.raw_text or "").lower()
    if komen.trigger.lower() not in teks:
        return

    try:
        discussion = await bot(GetDiscussionMessageRequest(
            peer=event.chat_id,
            msg_id=event.id
        ))
        if not discussion.messages or not discussion.messages[0].replies:
            return

        reply_chat = discussion.messages[0].replies.chat
        reply_msg_id = discussion.messages[0].id

        await bot.send_message(
            entity=reply_chat.id,
            message=komen.reply,
            reply_to=reply_msg_id
        )
    except Exception as e:
        await bot.send_message("me", f"[ERROR] Auto-komen gagal:\n{e}")
        
CMD_HELP.update({
    "autokomen": f"**Plugin :** `autokomen`\
\n\n📌 **Fungsi:** Auto-komen di comment section channel kalo postingan mengandung trigger tertentu.\
\n\n**Perintah:**\
\n➤ `{cmd}setch @username_channel`\
\n▸ Set channel target buat auto komen.\
\n\n➤ `{cmd}setkomen tekskomen trigger`\
\n▸ Set teks komen & trigger pemicunya.\
\n▸ Contoh: `{cmd}setkomen open ubot`\
\n\n➤ `{cmd}delch @username_channel`\
\n▸ Hapus channel dari daftar auto komen.\
\n\n➤ `{cmd}delkomen`\
\n▸ Hapus trigger dan teks komen untuk channel terakhir yang diset.\
\n\n➤ `{cmd}listkomen`\
\n▸ Liat semua channel dan settingan auto komen yang aktif.\
\n\n💡 Bot akan otomatis komen di **kolom komentar postingan channel** kalau isi postingannya mengandung trigger.\
\n✔️ Pastikan channel punya **grup diskusi**, dan userbot udah join channel & grup-nya."
})
