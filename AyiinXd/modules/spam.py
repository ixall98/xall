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
STATUS_FILE = "spam_status.json"
STATUS_FW_FILE = "spamfw_status.json"

# Load status dari file saat startup
if os.path.exists(STATUS_FILE):
    with open(STATUS_FILE, "r") as f:
        SPAM_STATUS.update(json.load(f))

if os.path.exists(STATUS_FW_FILE):
    with open(STATUS_FW_FILE, "r") as f:
        SPAMFW_STATUS.update(json.load(f))

# Fungsi simpan status ke file
def save_status():
    with open(STATUS_FILE, "w") as f:
        json.dump(SPAM_STATUS, f)

def save_fw_status():
    with open(STATUS_FW_FILE, "w") as f:
        json.dump(SPAMFW_STATUS, f)

@ayiin_cmd(pattern="(delayspam|dspam) ([\\s\\S]*)")
async def dlyspam(event):
    if event.chat_id in BLACKLIST_CHAT:
        return await event.edit(get_string("ayiin_1"))
    reply = await event.get_reply_message()
    input_str = "".join(event.text.split(maxsplit=1)[1:]).split(" ", 2)
    try:
        sleeptimet = sleeptimem = float(input_str[0])
    except Exception:
        return await eod(event, get_string("dspam_1").format(event.pattern_match.group(1)))
    xnxx = input_str[1:]
    try:
        int(xnxx[0])
    except Exception:
        return await eod(event, get_string("dspam_1").format(event.pattern_match.group(1)))

    await event.delete()
    SPAM_STATUS[str(event.chat_id)] = {
        "status": True,
        "delay": sleeptimem,
        "count": int(xnxx[0]),
        "text": str(xnxx[1]) if len(xnxx) > 1 else reply.text if reply else None,
    }
    save_status()
    await delay_spam_function(event, event.chat_id)

@ayiin_cmd(pattern="stopdspam(?:\\s+([\\s\\S]+))?")
async def stop_dlyspam(event):
    args = event.pattern_match.group(1)
    target_chat = event.chat_id if not args else await get_chat_id(event, args)
    if not target_chat: return
    SPAM_STATUS[str(target_chat)]["status"] = False
    save_status()
    await event.edit(f"🛑 Delay spam di `{target_chat}` berhasil dihentikan.")

@ayiin_cmd(pattern="listdspam$")
async def list_dspam(event):
    aktif = [cid for cid, val in SPAM_STATUS.items() if val.get("status")]
    if not aktif:
        return await event.edit("✅ Tidak ada delay spam yang aktif.")
    await event.edit("**📋 List Delay Spam Aktif:**\n" + "\n".join(f"• `{cid}`" for cid in aktif))

async def delay_spam_function(event, chat_id):
    data = SPAM_STATUS.get(str(chat_id), {})
    if not data or not data.get("status"):
        return
    delay = data["delay"]
    count = data["count"]
    text = data["text"]
    for _ in range(count):
        if not SPAM_STATUS[str(chat_id)]["status"]:
            break
        await event.client.send_message(chat_id, text)
        await asyncio.sleep(delay)
    SPAM_STATUS[str(chat_id)]["status"] = False
    save_status()

# Forward spam
@ayiin_cmd(pattern="(delayspamfw|dspamfw) ([\\s\\S]*)")
async def dlyspamfw(event):
    if event.chat_id in BLACKLIST_CHAT:
        return await event.edit(get_string("ayiin_1"))
    input_str = "".join(event.text.split(maxsplit=1)[1:]).split(" ", 2)
    try:
        sleeptimem = float(input_str[0])
        counter = int(input_str[1])
        link = input_str[2]
    except:
        return await eod(event, f"⚠️ Format salah. Kirim: `{event.pattern_match.group(1)} <delay> <jumlah> <link_post>`")

    try:
        message_id = int(link.split('/')[-1])
        channel_username = link.split('/')[3]
        channel = await event.client.get_entity(channel_username)
        message = await event.client.get_messages(channel, ids=message_id)
    except Exception as e:
        return await eod(event, f"Error: {str(e)}")

    await event.delete()
    SPAMFW_STATUS[str(event.chat_id)] = {
        "status": True,
        "delay": sleeptimem,
        "count": counter,
        "channel": channel_username,
        "msg_id": message_id
    }
    save_fw_status()
    await forward_spam_function(event, event.chat_id)

@ayiin_cmd(pattern="stopfw(?:\\s+([\\s\\S]+))?")
async def stop_fwspam(event):
    args = event.pattern_match.group(1)
    target_chat = event.chat_id if not args else await get_chat_id(event, args)
    if not target_chat: return
    SPAMFW_STATUS[str(target_chat)]["status"] = False
    save_fw_status()
    await event.edit(f"🛑 Forward spam di `{target_chat}` berhasil dihentikan.")

@ayiin_cmd(pattern="listfw$")
async def list_fwspam(event):
    aktif = [cid for cid, val in SPAMFW_STATUS.items() if val.get("status")]
    if not aktif:
        return await event.edit("✅ Tidak ada forward spam yang aktif.")
    await event.edit("**📋 List Forward Spam Aktif:**\n" + "\n".join(f"• `{cid}`" for cid in aktif))

async def forward_spam_function(event, chat_id):
    data = SPAMFW_STATUS.get(str(chat_id), {})
    if not data or not data.get("status"):
        return
    delay = data["delay"]
    count = data["count"]
    try:
        channel = await event.client.get_entity(data["channel"])
        message = await event.client.get_messages(channel, ids=data["msg_id"])
    except:
        return
    for _ in range(count):
        if not SPAMFW_STATUS[str(chat_id)]["status"]:
            break
        await event.client.forward_messages(chat_id, message.id, channel)
        await asyncio.sleep(delay)
    SPAMFW_STATUS[str(chat_id)]["status"] = False
    save_fw_status()

# Otomatis saat bot nyala
@ayiin.on(events.NewMessage(pattern=None, outgoing=True))
async def resume_spams(_):
    for cid in list(SPAM_STATUS.keys()):
        if SPAM_STATUS[cid].get("status"):
            asyncio.create_task(delay_spam_function(_, int(cid)))
    for cid in list(SPAMFW_STATUS.keys()):
        if SPAMFW_STATUS[cid].get("status"):
            asyncio.create_task(forward_spam_function(_, int(cid)))

# Helper
async def get_chat_id(event, arg):
    try:
        if arg.startswith("@") or arg.isalpha():
            entity = await event.client.get_entity(arg)
            return entity.id
        return int(arg)
    except:
        await event.edit(f"❌ Gagal menemukan grup `{arg}`.")
        return None
        
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
