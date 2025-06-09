from telethon import events
from AyiinXd import bot
from AyiinXd.ayiin import ayiin_cmd
from AyiinXd.modules.sql_helper.autoban_sql import (
    add_channel,
    add_or_update_channel,
    get_all_channels,
    get_prev_members,
    add_banned_user,
    get_banned_users
)

@ayiin_cmd(pattern=r"autoban(?: |$)(.*)")
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

@ayiin_cmd(pattern=r"stopban(?: |$)(.*)")
async def stop_autoban(e):
    input_str = e.pattern_match.group(1)
    if not input_str.startswith("@"):
        return await e.edit("❌ Gunakan format: `.stopban @username_channel`")
    from AyiinXd.modules.sql_helper.autoban_sql import remove_channel
    try:
        remove_channel((await bot.get_entity(input_str)).id)
        await e.edit(f"🛑 Auto-ban dimatikan dari {input_str}.")
    except Exception as err:
        await e.edit(f"❌ Gagal: {err}")

@ayiin_cmd(pattern="listban$")
async def list_autoban(e):
    try:
        chans = get_all_channels()
        if not chans:
            return await e.edit("📭 Belum ada channel yang aktif auto-ban.")
        teks = "📌 **Auto-ban aktif di channel:**\n\n"
        for c in chans:
            teks += f"• `{c.channel_username}`\n"
        await e.edit(teks)
    except Exception as err:
        await e.edit(f"❌ Error: {err}")

# Handler auto-ban pas user keluar dari channel
@bot.on(events.ChatAction)
async def autoban_trigger(event):
    if event.user_joined or event.user_added:
        return

    try:
        all_channels = get_all_channels()
        for chan in all_channels:
            prev_members = get_prev_members(chan.channel_id)
            banned_users = get_banned_users()

            # Kalo user yang keluar gak ada di data lama, skip
            if not event.user:
                continue
            if event.user.username in prev_members:
                continue

            # Jika belum pernah dibanned di channel ini
            if (chan.channel_username, event.user.username) not in banned_users:
                try:
                    await bot(EditBannedRequest(
                        event.chat_id,
                        event.user_id,
                        ChatBannedRights(
                            until_date=None,
                            view_messages=True
                        )
                    ))
                    add_banned_user(chan.channel_username, event.user.username)
                except Exception:
                    pass
    except Exception:
        pass
