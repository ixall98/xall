from AyiinXd.ayiin import ayiin_cmd
from AyiinXd import bot, tgbot, BOTLOG_CHATID, CMD_HANDLER as cmd, CMD_HELP
from telethon import events
from telethon.tl.functions.channels import JoinChannelRequest, GetParticipantRequest
from telethon.tl.types import ChannelParticipantSelf
from telethon.utils import get_display_name
from AyiinXd.modules.sql_helper.sfs_sql import add_sfs_channels, get_sfs_channels, delete_sfs_channels

USER_STEP = {}

@ayiin_cmd(pattern="setsfs(?: |$)(.*)")
async def set_sfs(event):
    args = event.pattern_match.group(1)
    if not args:
        return await event.edit("**Gunakan:** `.setsfs @channel1 @channel2 ...`")
    channels = args.split()
    await add_sfs_channels(channels)
    await event.edit("✅ Daftar channel untuk SFS berhasil disimpan.")

@ayiin_cmd(pattern="delsfs$")
async def del_sfs(event):
    await delete_sfs_channels()
    await event.edit("✅ Semua channel SFS telah dihapus.")

@ayiin_cmd(pattern="listsfs$")
async def list_sfs(event):
    channels = await get_sfs_channels()
    if not channels:
        return await event.edit("Belum ada channel yang diset.")
    teks = "**Daftar Channel SFS:**\n" + "\n".join(f"- {c}" for c in channels)
    await event.edit(teks)

@bot.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def auto_sfs(event):
    user_id = event.sender_id

    if user_id in USER_STEP:
        step = USER_STEP[user_id]
        if step["status"] == "wait_channel":
            ch_link = event.raw_text.strip()
            try:
                await bot(JoinChannelRequest(ch_link))
                await event.reply("✅ Berhasil join ke channel kamu. Terima kasih SFS-nya!")
                await bot.send_message(
                    BOTLOG_CHATID,
                    f"👥 **SFS Baru**\n👤 [{get_display_name(event.sender)}](tg://user?id={user_id})\n📣 Channel: `{ch_link}`"
                )
            except Exception as e:
                await event.reply(f"Gagal join ke channel kamu.\nError: {e}")
            del USER_STEP[user_id]
        return

    # Langkah awal: pakai inline bot untuk munculin tombol
    channels = await get_sfs_channels()
    if not channels:
        return

    AyiinUBOT = await tgbot.get_me()
    BOT_USERNAME = AyiinUBOT.username
    channel_list = "\n".join(f"🔗 {c}" for c in channels)
    sfs_text = f"Halo! 👋\nUntuk SFS, silakan join semua channel di bawah ini dulu ya!\n\n{channel_list}\n\n✅ Saya sudah join semua -> sfs_check"

    try:
        results = await bot.inline_query(BOT_USERNAME, f"Inline buttons {sfs_text}")
        await results[0].click(event.chat_id)
    except Exception as e:
        await event.reply(f"Gagal munculin tombol: {e}")

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
        await event.edit("✅ Terima kasih! Sekarang kirim channel kamu (pakai format `@namachannel`):")
        USER_STEP[user_id] = {"status": "wait_channel"}
