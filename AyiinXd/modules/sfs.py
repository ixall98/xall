from AyiinXd.ayiin import ayiin_cmd
from AyiinXd import bot
from AyiinXd.modules.sql_helper.sfs_sql import add_sfs_channels, get_sfs_channels, delete_sfs_channels
from telethon.tl.functions.channels import JoinChannelRequest, GetParticipantRequest
from telethon.tl.types import ChannelParticipantSelf
from telethon import events, Button
from AyiinXd import BOTLOG_CHATID, CMD_HANDLER as cmd, CMD_HELP, LOGS

USER_STEP = {}

# Set channel SFS
@ayiin_cmd(pattern="setsfs(?: |$)(.*)")
async def set_sfs(event):
    args = event.pattern_match.group(1)
    if not args:
        return await event.edit(f"**Contoh:** `{cmd}setsfs @channel1 @channel2 ...`")
    channels = args.split()
    await add_sfs_channels(channels)
    await event.edit("✅ Daftar channel SFS berhasil disimpan.")

# Hapus semua channel SFS
@ayiin_cmd(pattern="delsfs$")
async def del_sfs(event):
    await delete_sfs_channels()
    await event.edit("✅ Semua channel SFS telah dihapus.")

# Lihat daftar channel SFS
@ayiin_cmd(pattern="listsfs$")
async def list_sfs(event):
    channels = await get_sfs_channels()
    if not channels:
        return await event.edit("Belum ada channel yang diset.")
    teks = "**Daftar Channel SFS:**\n" + "\n".join(f"- {c}" for c in channels)
    await event.edit(teks)

# Auto respon PM
@bot.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def auto_sfs(event):
    user_id = event.sender_id
    # Step kirim channel
    if user_id in USER_STEP:
        step = USER_STEP[user_id]
        if step["status"] == "wait_channel":
            ch_link = event.raw_text.strip()
            try:
                await bot(JoinChannelRequest(ch_link))
                await event.reply("✅ Berhasil join ke channel kamu. Terima kasih SFS-nya!")
                await bot.send_message(
                    BOTLOG_CHATID,
                    f"👥 **SFS Baru**\n👤 [{event.sender.first_name}](tg://user?id={user_id})\n📣 Channel: `{ch_link}`"
                )
            except Exception as e:
                await event.reply(f"❌ Gagal join ke channel kamu.\nError: `{e}`")
            del USER_STEP[user_id]
        return

    # Step awal: minta join semua channel
    channels = await get_sfs_channels()
    if not channels:
        return

    buttons = [[Button.url(f"🔗 {c}", f"https://t.me/{c.strip('@')}")] for c in channels]
    buttons.append([Button.inline("✅ Saya sudah join semua", b"sfs_check")])

    await event.respond(
        "Halo! 👋\nUntuk SFS, silakan join semua channel di bawah ini dulu ya!",
        buttons=buttons
    )

# Verifikasi apakah user sudah join semua channel
@bot.on(events.CallbackQuery(data=b"sfs_check"))
async def verify_join(event):
    user = await event.get_sender()
    user_id = user.id
    channels = await get_sfs_channels()
    belum = []

    for ch in channels:
        try:
            result = await bot(GetParticipantRequest(ch, user_id))
            if not isinstance(result.participant, ChannelParticipantSelf):
                belum.append(ch)
        except:
            belum.append(ch)

    if belum:
        msg = "**Kamu belum join ke channel berikut:**\n"
        msg += "\n".join(f"- {c}" for c in belum)
        msg += "\n\nSilakan join dulu dan klik tombol lagi."
        await event.answer("Belum semua channel kamu join", alert=True)
        await event.edit(msg)
    else:
        await event.edit("✅ Terima kasih! Sekarang kirim channel kamu (format `@namachannel`):")
        USER_STEP[user_id] = {"status": "wait_channel"}
