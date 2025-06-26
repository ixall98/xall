from AyiinXd.ayiin import ayiin_cmd
from AyiinXd import bot
from telethon.tl.functions.channels import JoinChannelRequest, GetParticipantRequest
from telethon.tl.types import ChannelParticipantSelf
from AyiinXd.modules.sql_helper.sfs_sql import add_sfs_channels, get_sfs_channels, delete_sfs_channels
from telethon import events, Button
from AyiinXd import BOTLOG_CHATID
from AyiinXd import CMD_HANDLER as cmd
from AyiinXd import CMD_HELP, LOGS

USER_STEP = {}  # nyimpen state user sementara

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

@client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def auto_sfs(event):
    user_id = event.sender_id
    if user_id in USER_STEP:
        step = USER_STEP[user_id]
        if step["status"] == "wait_channel":
            ch_link = event.raw_text.strip()
            try:
                await client(JoinChannelRequest(ch_link))
                await event.reply("✅ Berhasil join ke channel kamu. Terima kasih SFS-nya!")
                await client.send_message(
                    LOG_GROUP_ID,
                    f"👥 **SFS Baru**\n👤 [{event.sender.first_name}](tg://user?id={user_id})\n📣 Channel: `{ch_link}`"
                )
            except Exception as e:
                await event.reply(f"Gagal join ke channel kamu.\nError: {e}")
            del USER_STEP[user_id]
        return

    # Langkah awal: kirim pesan welcome
    channels = await get_sfs_channels()
    if not channels:
        return
    buttons = [Button.url(f"🔗 {c}", f"https://t.me/{c.strip('@')}") for c in channels]
    buttons.append([Button.inline("✅ Saya sudah join semua", b"sfs_check")])
    await event.respond(
        "Halo! 👋\nUntuk SFS, silakan join semua channel di bawah ini dulu ya!",
        buttons=buttons
    )

@client.on(events.CallbackQuery(data=b"sfs_check"))
async def verify_join(event):
    user = await event.get_sender()
    user_id = user.id
    channels = await get_sfs_channels()
    belum = []
    for ch in channels:
        try:
            result = await client(GetParticipantRequest(ch, user_id))
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
