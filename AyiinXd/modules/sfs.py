import asyncio
from telethon import events
from telethon.tl.functions.channels import JoinChannelRequest, GetParticipantRequest
from telethon.errors import UserNotParticipantError
from AyiinXd import CMD_HANDLER as cmd
from AyiinXd import CMD_HELP
from AyiinXd.ayiin import ayiin_cmd
from AyiinXd import bot
from AyiinXd.modules.sql_helper.sfs_sql import SFSDatabase

sfs_db: SFSDatabase

sfs_db = None  # akan diisi dari __main__.py
bot = None     # akan diisi dari __main__.py

WELCOME_TEMPLATE = (
    "Halo {name}!\n\n"
    "Untuk tukeran subscribe (SFS), silakan join channel berikut dulu ya:\n"
    "{channel}\n\n"
    "Kalau sudah join, balas dengan: sudah join"
)

ASK_CHANNEL = "Mantap! Sekarang balas dengan @channel kamu (harus publik)"
SUCCESS_MSG = "SFS berhasil! Gue udah subscribe channel lu. Makasih bro 🙌"
LEFT_ALERT = "⚠️ User @{username} sudah keluar dari {channel_admin}"

# ──────────────── COMMAND ────────────────
@ayiin_cmd(pattern="setsfs(?:\\s+|$)(.*)")
async def _(event):
    channel = event.pattern_match.group(1).strip()
    if not channel.startswith("@"):
        return await event.reply("Format: .setsfs @channel_kamu")
    await sfs_db.set_admin_channel(event.sender_id, channel)
    await event.reply(f"Mode SFS aktif ✅\nChannel admin diset ke {channel}")

@ayiin_cmd(pattern="stopsfs")
async def _(event):
    await sfs_db.clear_admin_channel(event.sender_id)
    await event.reply("Mode SFS dimatikan ❌")

# ──────────────── PM FLOW ────────────────
@bot.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def sfs_pm(event):
    admin_channel = await sfs_db.get_admin_channel(event.sender_id)
    if not admin_channel:
        return

    status = await sfs_db.get_status(event.sender_id)
    text = event.raw_text.strip().lower()

    if not status:
        await sfs_db.upsert_user(event.sender_id, event.sender.username or "", admin_channel)
        await event.reply(WELCOME_TEMPLATE.format(name=event.sender.first_name, channel=admin_channel))
        return

    if status == "waiting" and text == "sudah join":
        try:
            await bot(GetParticipantRequest(admin_channel, event.sender_id))
            await sfs_db.mark_joined(event.sender_id)
            await event.reply(ASK_CHANNEL)
        except UserNotParticipantError:
            await event.reply("Belum join channel. Pastikan kamu sudah join @channel dengan benar!")
        return

    if status == "joined":
        if text.startswith("@") and len(text) > 1:
            await sfs_db.save_user_channel(event.sender_id, text)
            try:
                await bot(JoinChannelRequest(text))
                await event.reply(SUCCESS_MSG)
            except Exception:
                await event.reply("Gagal join channel kamu. Pastikan channel publik dan gue belum di-ban.")
        else:
            await event.reply("Format channel salah. Kirim @username publik channel kamu.")

# ──────────────── BACKGROUND CHECK ────────────────
async def sfs_checker():
    while True:
        admins = await bot.get_dialogs()
        for admin in admins:
            if not admin.is_user:
                continue
            admin_id = admin.entity.id
            admin_channel = await sfs_db.get_admin_channel(admin_id)
            if not admin_channel:
                continue
            users = await sfs_db.get_all_done_users()
            for rec in users:
                user_id = rec["user_id"]
                username = rec["username"] or str(user_id)
                try:
                    await bot(GetParticipantRequest(admin_channel, user_id))
                except UserNotParticipantError:
                    await bot.send_message(admin_id, LEFT_ALERT.format(username=username, channel_admin=admin_channel))
        await asyncio.sleep(300)
