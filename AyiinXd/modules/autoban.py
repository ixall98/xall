import asyncio
from telethon import functions
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights
from AyiinXd import ayiin_cmd, bot
from AyiinXd.modules.sql_helper.autoban_sql import (
    add_channel, remove_channel, get_all_channels
)

BANNED_RIGHTS = ChatBannedRights(
    until_date=None,
    view_messages=True
)

@ayiin_cmd(pattern="autoban(?:\\s|$)([@\\w\\d_]+)?")
async def _(event):
    ch_username = event.pattern_match.group(1)
    if not ch_username:
        return await event.eor("❌ Masukin username channel-nya, contoh: `.autoban @channel`")
    try:
        entity = await event.client.get_entity(ch_username)
        add_channel(str(entity.id), ch_username)
        await event.eor(f"✅ Auto-ban diaktifkan untuk @{ch_username}")
    except Exception as e:
        await event.eor(f"❌ Gagal aktifkan: {e}")

@ayiin_cmd(pattern="stopban(?:\\s|$)([@\\w\\d_]+)?")
async def _(event):
    ch_username = event.pattern_match.group(1)
    if not ch_username:
        return await event.eor("❌ Masukin username channel-nya.")
    try:
        entity = await event.client.get_entity(ch_username)
        remove_channel(str(entity.id))
        await event.eor(f"🛑 Auto-ban dimatikan untuk @{ch_username}")
    except Exception as e:
        await event.eor(f"❌ Error: {e}")

@ayiin_cmd(pattern="listban$")
async def _(event):
    await event.eor("🔍 Mengambil data banned user...")

    teks = "📄 **Daftar User yang Diban Otomatis:**\n"
    total = 0

    for ch in get_all_channels():
        try:
            entity = await bot.get_entity(ch.channel_id)
            banned_users = await bot.get_participants(entity, filter=1)

            if not banned_users:
                continue

            teks += f"\n📛 Channel: @{ch.channel_username}\n"
            for u in banned_users:
                uname = f"@{u.username}" if u.username else f"`{u.id}`"
                teks += f"• {uname}\n"
                total += 1

        except Exception as e:
            teks += f"\n⚠️ Gagal ambil @{ch.channel_username}: {e}\n"

    if total == 0:
        teks = "✅ Belum ada user yang dibanned dari channel manapun."

    await event.eor(teks)

# Loop pengecekan otomatis
async def auto_ban_loop():
    prev_members = {}

    while True:
        for ch in get_all_channels():
            try:
                entity = await bot.get_entity(ch.channel_id)
                members = await bot.get_participants(entity)
                current = set(u.username for u in members if u.username)

                old = set(prev_members.get(ch.channel_id, []))
                gone = old - current

                for username in gone:
                    try:
                        user = await bot.get_entity(username)
                        await bot(EditBannedRequest(
                            channel=entity,
                            user_id=user.id,
                            banned_rights=BANNED_RIGHTS
                        ))
                        print(f"[AutoBan] @{username} dibanned dari @{ch.channel_username}")
                    except Exception as e:
                        print(f"[AutoBanError] @{username} gagal diban: {e}")

                prev_members[ch.channel_id] = list(current)
            except Exception as e:
                print(f"[LoopError] {e}")

        await asyncio.sleep(60)

bot.loop.create_task(auto_ban_loop())
