from AyiinXd import bot, BOTLOG_CHATID
from AyiinXd.ayiin import ayiin_cmd
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights
from AyiinXd.modules.sql_helper.autoban_sql import (
    get_all_channels,
    add_channel,
    remove_channel,
    get_prev_members,
    add_or_update_channel,
    add_banned_user,
    get_banned_users,
)
import asyncio

# Handler command
@ayiin_cmd(pattern=r"autoban(?: |$)(.*)"))
async def enable_autoban(e):
    input_str = e.pattern_match.group(1)
    if not input_str.startswith("@"):
        return await e.edit("❌ Gunakan format: `.autoban @username_channel`")
    await e.edit("⏳ Mengaktifkan auto-ban...")
    try:
        entity = await bot.get_entity(input_str)
        participants = await bot.get_participants(entity)
        usernames = [u.username for u in participants if u.username]
        add_channel(entity.id, input_str)
        add_or_update_channel(entity.id, input_str, usernames)
        await e.edit(f"✅ Auto-ban aktif di {input_str}.")
    except Exception as err:
        await e.edit(f"❌ Gagal: {err}")

@ayiin_cmd(pattern=r"stopban(?: |$)(.*)"))
async def disable_autoban(e):
    input_str = e.pattern_match.group(1)
    if not input_str.startswith("@"):
        return await e.edit("❌ Gunakan format: `.stopban @username_channel`")
    try:
        entity = await bot.get_entity(input_str)
        remove_channel(entity.id)
        await e.edit(f"✅ Auto-ban dimatikan di {input_str}.")
    except Exception as err:
        await e.edit(f"❌ Gagal: {err}")

@ayiin_cmd(pattern=r"listban(?: |$)(.*)"))
async def list_banned(e):
    input_str = e.pattern_match.group(1)
    result = get_banned_users()
    if not result:
        return await e.edit("🚫 Belum ada user yang dibanned otomatis.")
    msg = "📄 Daftar User yang Diban Otomatis:\n"
    data = {}
    for ch, user in result:
        data.setdefault(ch, []).append(user)
    for ch, users in data.items():
        msg += f"\n📛 Channel: {ch}\n"
        for u in users:
            msg += f"• {u}\n"
    await e.edit(msg)

# Loop auto-ban
async def get_usernames(channel):
    usernames = []
    async for user in bot.iter_participants(channel):
        if user.username:
            usernames.append(user.username)
    return usernames

async def auto_ban_loop():
    while True:
        for ch in get_all_channels():
            try:
                entity = await bot.get_entity(ch.channel_username)
                current = set(await get_usernames(entity))
                prev = get_prev_members(ch.channel_id)
                gone = prev - current

                for username in gone:
                    try:
                        user = await bot.get_entity(username)
                        await bot(EditBannedRequest(
                            channel=entity,
                            user_id=user.id,
                            banned_rights=ChatBannedRights(view_messages=True)
                        ))
                        add_banned_user(ch.channel_username, f"@{username}")
                        await bot.send_message(
                            BOTLOG_CHATID,
                            f"🚫 **AutoBan:**\n• User: @{username}\n• Channel: {ch.channel_username}"
                        )
                    except Exception as e:
                        print(f"[AutoBanError] @{username}: {e}")

                add_or_update_channel(ch.channel_id, ch.channel_username, list(current))

            except Exception as e:
                print(f"[AutoBanLoop Error] {ch.channel_username}: {e}")

        await asyncio.sleep(300)  # tiap 5 menit

# Start loop
bot.loop.create_task(auto_ban_loop())
