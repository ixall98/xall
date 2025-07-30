import asyncio
from telethon import events
from telethon.tl.functions.messages import SendReaction
from AyiinXd import bot
from AyiinXd import BOTLOG_CHATID
from AyiinXd import CMD_HANDLER as cmd
from AyiinXd import CMD_HELP, BLACKLIST_CHAT, LOGS
from AyiinXd.ayiin import ayiin_cmd
from AyiinXd.modules.sql_helper.autoreact_sql import add_react, remove_react, get_all_reacts

@ayiin_cmd(pattern="reacton (.+)")
async def _(event):
    args = event.pattern_match.group(1).split()
    if len(args) < 2:
        return await event.reply("Gunakan format: `.reacton @channel ❤️:10 🔥:5`")

    entity = args[0]
    try:
        channel = await bot.get_entity(entity)
    except Exception as e:
        return await event.reply(f"Gagal mendapatkan channel: {e}")

    chat_id = str(channel.id)
    for part in args[1:]:
        if ':' not in part:
            continue
        emoji, count = part.split(":", 1)
        try:
            jumlah = int(count)
            add_react(chat_id, emoji, jumlah)
        except ValueError:
            continue

    await event.reply("✅ Auto-reaction diaktifkan.")


@ayiin_cmd(pattern="reactoff(?: (.+))?")
async def _(event):
    args = event.pattern_match.group(1)
    if not args:
        return await event.reply("Gunakan format: `.reactoff @channel [emoji]`")

    parts = args.split()
    entity = parts[0]
    emoji = parts[1] if len(parts) > 1 else None

    try:
        channel = await bot.get_entity(entity)
    except Exception as e:
        return await event.reply(f"Gagal mendapatkan channel: {e}")

    remove_react(str(channel.id), emoji)
    await event.reply("✅ Auto-reaction dinonaktifkan.")


@ayiin_cmd(pattern="reactlist")
async def _(event):
    all_data = get_all_reacts()
    if not all_data:
        return await event.reply("Belum ada auto-reaction aktif.")

    text = "<b>Daftar Auto-Reaction:</b>\n"
    grouped = {}
    for item in all_data:
        grouped.setdefault(item.chat_id, []).append(f"{item.emoji}:{item.jumlah}")

    for chat_id, reacts in grouped.items():
        text += f"\n<code>{chat_id}</code>: {', '.join(reacts)}"

    await event.reply(text, parse_mode="html")


@bot.on(events.NewMessage(incoming=True))
async def _(event):
    if not event.is_channel or not event.out:
        return

    chat_id = str(event.chat_id)
    reacts = get_reacts_by_chat(chat_id)
    if not reacts:
        return

    for item in reacts:
        for _ in range(item.jumlah):
            try:
                await bot(SendReaction(
                    peer=event.chat_id,
                    msg_id=event.id,
                    reaction=[item.emoji]
                ))
                await asyncio.sleep(0.7)
            except Exception:
                continue
