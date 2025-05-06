# Copyright (C) 2020 Catuserbot <https://github.com/sandy1709/catuserbot>
# Ported by @mrismanaziz
# FROM Man-Userbot <https://github.com/mrismanaziz/Man-Userbot>
# t.me/SharingUserbot & t.me/Lunatic0de

import asyncio
import os
import json
from telethon import events
from telethon.tl import functions, types
from telethon.tl.functions.messages import GetStickerSetRequest
from telethon.utils import get_display_name

from AyiinXd import ayiin
from AyiinXd import BOTLOG_CHATID
from AyiinXd import CMD_HANDLER as cmd
from AyiinXd import CMD_HELP, BLACKLIST_CHAT, LOGS
from AyiinXd.modules.sql_helper.globals import addgvar, gvarstatus
from AyiinXd.ayiin import ayiin_cmd, eod, eor
from AyiinXd.ayiin.tools import media_type
from Stringyins import get_string


async def unsavegif(event, spammer):
    try:
        await event.client(
            functions.messages.SaveGifRequest(
                id=types.InputDocument(
                    id=spammer.media.document.id,
                    access_hash=spammer.media.document.access_hash,
                    file_reference=spammer.media.document.file_reference,
                ),
                unsave=True,
            )
        )
    except Exception as e:
        LOGS.info(f"{e}")


async def spam_function(event, spammer, xnxx, sleeptimem, sleeptimet, DelaySpam=False):
    counter = int(xnxx[0])
    if len(xnxx) == 2:
        spam_message = str(xnxx[1])
        for _ in range(counter):
            if gvarstatus("spamwork") is None:
                return
            if event.reply_to_msg_id:
                await spammer.reply(spam_message)
            else:
                await event.client.send_message(event.chat_id, spam_message)
            await asyncio.sleep(sleeptimet)
    elif event.reply_to_msg_id and spammer.media:
        for _ in range(counter):
            if gvarstatus("spamwork") is None:
                return
            spammer = await event.client.send_file(
                event.chat_id, spammer, caption=spammer.text
            )
            await unsavegif(event, spammer)
            await asyncio.sleep(sleeptimem)
        if BOTLOG_CHATID:
            if DelaySpam is not True:
                if event.is_private:
                    await event.client.send_message(
                        BOTLOG_CHATID, get_string("spam_1").format(event.chat_id, counter)
                    )
                else:
                    await event.client.send_message(
                        BOTLOG_CHATID, get_string("spam_2").format(get_display_name(await event.get_chat()), event.chat_id, counter)
                    )
            elif event.is_private:
                await event.client.send_message(
                    BOTLOG_CHATID, get_string("spam_3").format(event.chat_id, counter, sleeptimet)
                )
            else:
                await event.client.send_message(
                    BOTLOG_CHATID, get_string("spam_4").format(get_display_name(await event.get_chat()), event.chat_id, counter, sleeptimet)
                )

            spammer = await event.client.send_file(BOTLOG_CHATID, spammer)
            await unsavegif(event, spammer)
        return
    elif event.reply_to_msg_id and spammer.text:
        spam_message = spammer.text
        for _ in range(counter):
            if gvarstatus("spamwork") is None:
                return
            await event.client.send_message(event.chat_id, spam_message)
            await asyncio.sleep(sleeptimet)
    else:
        return
    if DelaySpam is not True:
        if BOTLOG_CHATID:
            if event.is_private:
                await event.client.send_message(
                    BOTLOG_CHATID, get_string("spam_5").format(event.chat_id, counter, spam_message)
                )
            else:
                await event.client.send_message(
                    BOTLOG_CHATID, get_string("spam_6").format(get_display_name(await event.get_chat()), event.chat_id, counter, spam_message)
                )
    elif BOTLOG_CHATID:
        if event.is_private:
            await event.client.send_message(
                BOTLOG_CHATID, get_string("spam_7").format(event.chat_id, sleeptimet, counter, spam_message)
            )
        else:
            await event.client.send_message(
                BOTLOG_CHATID, get_string("spam_8").format(get_display_name(await event.get_chat()), event.chat_id, sleeptimet, counter, spam_message)
            )


@ayiin_cmd(pattern="spam ([\\s\\S]*)")
async def nyespam(event):
    if event.chat_id in BLACKLIST_CHAT:
        return await event.edit(get_string("ayiin_1"))
    spammer = await event.get_reply_message()
    xnxx = ("".join(event.text.split(maxsplit=1)[1:])).split(" ", 1)
    try:
        counter = int(xnxx[0])
    except Exception:
        return await eod(
            event, get_string("spam_9").format(cmd)
        )
    if counter > 50:
        sleeptimet = 0.5
        sleeptimem = 1
    else:
        sleeptimet = 0.1
        sleeptimem = 0.3
    await event.delete()
    addgvar("spamwork", True)
    await spam_function(event, spammer, xnxx, sleeptimem, sleeptimet)


@ayiin_cmd(pattern="sspam$")
async def stickerpack_spam(event):
    if event.chat_id in BLACKLIST_CHAT:
        return await event.edit(get_string("ayiin_1"))
    reply = await event.get_reply_message()
    if not reply or media_type(
            reply) is None or media_type(reply) != "Sticker":
        return await eod(
            event, get_string("sspam_1")
        )
    try:
        stickerset_attr = reply.document.attributes[1]
        xyz = await eor(event, get_string("sspam_2"))
    except BaseException:
        await eod(event, get_string("sspam_3"))
        return
    try:
        get_stickerset = await event.client(
            GetStickerSetRequest(
                types.InputStickerSetID(
                    id=stickerset_attr.stickerset.id,
                    access_hash=stickerset_attr.stickerset.access_hash,
                )
            )
        )
    except Exception:
        return await eod(
            xyz, get_string("sspam_4")
        )
    reqd_sticker_set = await event.client(
        functions.messages.GetStickerSetRequest(
            stickerset=types.InputStickerSetShortName(
                short_name=f"{get_stickerset.set.short_name}"
            )
        )
    )
    addgvar("spamwork", True)
    for m in reqd_sticker_set.documents:
        if gvarstatus("spamwork") is None:
            return
        await event.client.send_file(event.chat_id, m)
        await asyncio.sleep(0.7)
    if BOTLOG_CHATID:
        if event.is_private:
            await event.client.send_message(
                BOTLOG_CHATID, get_string("sspam_5").format(event.chat_id)
            )
        else:
            await event.client.send_message(
                BOTLOG_CHATID, get_string("sspam_6").format(get_display_name(await event.get_chat()), event.chat_id)
            )
        await event.client.send_file(BOTLOG_CHATID, reqd_sticker_set.documents[0])


@ayiin_cmd(pattern="cspam ([\\s\\S]*)")
async def tmeme(event):
    if event.chat_id in BLACKLIST_CHAT:
        return await event.edit(get_string("ayiin_1"))
    cspam = "".join(event.text.split(maxsplit=1)[1:])
    message = cspam.replace(" ", "")
    await event.delete()
    addgvar("spamwork", True)
    for letter in message:
        if gvarstatus("spamwork") is None:
            return
        await event.respond(letter)
    if BOTLOG_CHATID:
        if event.is_private:
            await event.client.send_message(
                BOTLOG_CHATID, get_string("cspam_1").format(event.chat_id, message)
            )
        else:
            await event.client.send_message(
                BOTLOG_CHATID, get_string("cspam_2").format(get_display_name(await event.get_chat()), event.chat_id, message)
            )


@ayiin_cmd(pattern="wspam ([\\s\\S]*)")
async def tmeme(event):
    if event.chat_id in BLACKLIST_CHAT:
        return await event.edit(get_string("ayiin_1"))
    wspam = "".join(event.text.split(maxsplit=1)[1:])
    message = wspam.split()
    await event.delete()
    addgvar("spamwork", True)
    for word in message:
        if gvarstatus("spamwork") is None:
            return
        await event.respond(word)
    if BOTLOG_CHATID:
        if event.is_private:
            await event.client.send_message(
                BOTLOG_CHATID, get_string("wspam_1").format(event.chat_id, message)
            )
        else:
            await event.client.send_message(
                BOTLOG_CHATID, get_string("wspam_2").format(get_display_name(await event.get_chat()), event.chat_id, message)
            )


SPAM_STATUS = {}
SPAMFW_STATUS = {}
SPAM_DATA = {}

SPAM_DATA_FILE = "spam_data.json"

# Load spam data dari file saat startup
if os.path.exists(SPAM_DATA_FILE):
    with open(SPAM_DATA_FILE, "r") as f:
        SPAM_DATA = json.load(f)
    for chat_id, data in SPAM_DATA.items():
        if data["type"] == "text":
            SPAM_STATUS[int(chat_id)] = True
        elif data["type"] == "fw":
            SPAMFW_STATUS[int(chat_id)] = True

# Simpan spam data ke file
def save_spam_data():
    with open(SPAM_DATA_FILE, "w") as f:
        json.dump(SPAM_DATA, f)


@ayiin_cmd(pattern="(delayspam|dspam) ([\\s\\S]*)")
async def dlyspam(event):
    if event.chat_id in BLACKLIST_CHAT:
        return await event.edit(get_string("ayiin_1"))
    reply = await event.get_reply_message()
    input_str = "".join(event.text.split(maxsplit=1)[1:]).split(" ", 2)
    try:
        sleeptimet = sleeptimem = float(input_str[0])
    except Exception:
        return await eod(
            event, get_string("dspam_1").format(event.pattern_match.group(1))
        )
    xnxx = input_str[1:]
    try:
        int(xnxx[0])
    except Exception:
        return await eod(
            event, get_string("dspam_1").format(event.pattern_match.group(1))
        )

    await event.delete()
    SPAM_STATUS[event.chat_id] = True
    SPAM_DATA[str(event.chat_id)] = {
        "type": "text",
        "delay": sleeptimem,
        "count": int(xnxx[0]),
        "text": str(xnxx[1]) if len(xnxx) > 1 else (reply.text if reply else ""),
    }
    save_spam_data()
    await delay_spam_function(event, reply, xnxx, sleeptimem, sleeptimet, chat_id=event.chat_id)


@ayiin_cmd(pattern="stopdspam(?:\\s+([\\s\\S]+))?")
async def stop_dlyspam(event):
    args = event.pattern_match.group(1)
    target_chat = event.chat_id if not args else await get_chat_id_from_arg(event, args)
    if target_chat in SPAM_STATUS and SPAM_STATUS[target_chat]:
        SPAM_STATUS[target_chat] = False
        SPAM_DATA.pop(str(target_chat), None)
        save_spam_data()
        await event.edit(f"🛑 Delay spam di `{target_chat}` berhasil dihentikan.")
    else:
        await event.edit(f"🚫 Tidak ada delay spam aktif di `{target_chat}`.")


@ayiin_cmd(pattern="listdspam$")
async def list_dspam(event):
    if not SPAM_STATUS:
        return await event.edit("✅ Tidak ada delay spam yang aktif.")
    active_chats = [str(cid) for cid, status in SPAM_STATUS.items() if status]
    if not active_chats:
        return await event.edit("✅ Tidak ada delay spam yang aktif.")
    text = "**📋 List Delay Spam Aktif:**\n"
    for cid in active_chats:
        text += f"• `{cid}`\n"
    await event.edit(text)


async def delay_spam_function(event, reply, xnxx, sleeptimem, sleeptimet, chat_id):
    try:
        counter = int(xnxx[0])
        spam_text = str(xnxx[1]) if len(xnxx) > 1 else reply.text if reply else None
    except Exception:
        return await eod(event, "⚠️ Format salah. Coba lagi.")

    if not spam_text:
        return await eod(event, "⚠️ Tidak ada teks untuk di-spam.")

    for _ in range(counter):
        if not SPAM_STATUS.get(chat_id, False):
            break
        await event.client.send_message(chat_id, spam_text)
        await asyncio.sleep(sleeptimem)


@ayiin_cmd(pattern="(delayspamfw|dspamfw) ([\\s\\S]*)")
async def dlyspamfw(event):
    if event.chat_id in BLACKLIST_CHAT:
        return await event.edit(get_string("ayiin_1"))

    input_str = "".join(event.text.split(maxsplit=1)[1:]).split(" ", 2)
    cmd = event.pattern_match.group(1)

    try:
        sleeptimet = sleeptimem = float(input_str[0])
        counter = int(input_str[1])
        channel_message_link = input_str[2]
    except:
        return await eod(event, f"⚠️ Format salah. Kirim: `{cmd} <delay> <jumlah> <link_post>`")

    try:
        message_id = int(channel_message_link.split('/')[-1])
        channel_username = channel_message_link.split('/')[3]
        channel = await event.client.get_entity(channel_username)
        message = await event.client.get_messages(channel, ids=message_id)
    except Exception as e:
        return await eod(event, f"Error: {str(e)}")

    await event.delete()
    SPAMFW_STATUS[event.chat_id] = True
    SPAM_DATA[str(event.chat_id)] = {
        "type": "fw",
        "delay": sleeptimem,
        "count": counter,
        "channel": channel_username,
        "msgid": message_id,
    }
    save_spam_data()

    for _ in range(counter):
        if not SPAMFW_STATUS.get(event.chat_id, False):
            break
        await event.client.forward_messages(event.chat_id, message.id, channel)
        await asyncio.sleep(sleeptimem)


@ayiin_cmd(pattern="stopfw(?:\\s+([\\s\\S]+))?")
async def stop_fwspam(event):
    args = event.pattern_match.group(1)
    target_chat = event.chat_id if not args else await get_chat_id_from_arg(event, args)

    if target_chat in SPAMFW_STATUS and SPAMFW_STATUS[target_chat]:
        SPAMFW_STATUS[target_chat] = False
        SPAM_DATA.pop(str(target_chat), None)
        save_spam_data()
        await event.edit(f"🛑 Forward spam di `{target_chat}` berhasil dihentikan.")
    else:
        await event.edit(f"🚫 Tidak ada forward spam aktif di `{target_chat}`.")


@ayiin_cmd(pattern="listfw$")
async def list_fwspam(event):
    if not SPAMFW_STATUS:
        return await event.edit("✅ Tidak ada forward spam yang aktif.")
    active_chats = [str(cid) for cid, status in SPAMFW_STATUS.items() if status]
    if not active_chats:
        return await event.edit("✅ Tidak ada forward spam yang aktif.")
    text = "**📋 List Forward Spam Aktif:**\n"
    for cid in active_chats:
        text += f"• `{cid}`\n"
    await event.edit(text)


# Auto resume spam saat startup
@ayiin.on(events.NewMessage(pattern=None, outgoing=True))
async def spam_resume_listener(event):
    if not SPAM_DATA:
        return
    for chat_id, data in SPAM_DATA.items():
        try:
            cid = int(chat_id)
            if data["type"] == "text" and cid not in SPAM_STATUS:
                SPAM_STATUS[cid] = True
                asyncio.create_task(delay_spam_function(event, None, [data["count"], data["text"]], data["delay"], data["delay"], chat_id=cid))
            elif data["type"] == "fw" and cid not in SPAMFW_STATUS:
                SPAMFW_STATUS[cid] = True
                channel = await event.client.get_entity(data["channel"])
                message = await event.client.get_messages(channel, ids=data["msgid"])
                async def run_fw():
                    for _ in range(data["count"]):
                        if not SPAMFW_STATUS.get(cid, False):
                            break
                        await event.client.forward_messages(cid, message.id, channel)
                        await asyncio.sleep(data["delay"])
                asyncio.create_task(run_fw())
        except Exception as e:
            print(f"Gagal resume spam untuk {chat_id}: {e}")


async def get_chat_id_from_arg(event, args):
    if args.startswith("@") or args.isalpha():
        entity = await event.client.get_entity(args)
        return entity.id
    else:
        return int(args)
        
CMD_HELP.update(
    {
        "spam": f"**Plugin : **`spam`\
        \n\n  »  **Perintah :** `{cmd}spam` <jumlah spam/bbc> <text/list>\
        \n  »  **Kegunaan : **Membanjiri teks dalam obrolan!!\
        \n\n  »  **Perintah :** `{cmd}cspam` <text/list>\
        \n  »  **Kegunaan : **Spam surat teks dengan huruf\
        \n\n  »  **Perintah :** `{cmd}sspam` <reply sticker>\
        \n  »  **Kegunaan : **Spam sticker dari Seluruh isi Sticker Pack.\
        \n\n  »  **Perintah :** `{cmd}wspam` <text/list>\
        \n  »  **Kegunaan : **Spam kata teks demi kata.\
        \n\n  »  **Perintah :** `{cmd}picspam` <jumlah spam> <link image/gif>\
        \n  »  **Kegunaan : **Spam Foto Seolah-olah spam teks tidak cukup !!\
        \n\n  »  **Perintah :** `{cmd}delayspam` | `{cmd}dspam` <jeda> <jumlah bbc> <text/list>\
        \n  »  **Kegunaan : **Spam dengan menggunakan jeda dan jumlah bbc tertentu\
        \n\n  »  Perintah : {cmd}dspamfw <jeda> <jumlah bbc> <link yang ingin di forward>\
        \n  »  Kegunaan : spam forward dari channel.\
        \n\n  •  **NOTE : Spam dengan Risiko Anda sendiri**"
    }
)
