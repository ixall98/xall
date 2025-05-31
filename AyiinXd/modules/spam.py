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
from asyncio import create_task
from telethon.tl.types import ChannelParticipantsAdmins

from AyiinXd import bot
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



# File: spam.py



SPAM_STATUS = {}
SPAMFW_STATUS = {}
SPAM_DATA_FILE = "spam_data.json"

# Load data
if os.path.exists(SPAM_DATA_FILE):
    with open(SPAM_DATA_FILE, 'r') as f:
        SPAM_LIST = json.load(f)
else:
    SPAM_LIST = {}

def save_data():
    with open(SPAM_DATA_FILE, 'w') as f:
        json.dump(SPAM_LIST, f)

@ayiin_cmd(pattern="setgc (\w+) (.+)")
async def set_gc(event):
    list_name, groups = event.pattern_match.group(1), event.pattern_match.group(2).split()
    SPAM_LIST.setdefault(list_name, {"groups": [], "text": []})
    for g in groups:
        if g not in SPAM_LIST[list_name]["groups"]:
            SPAM_LIST[list_name]["groups"].append(g)
    save_data()
    await event.edit(f"✅ Grup ditambahkan ke list `{list_name}`")

@ayiin_cmd(pattern="delgc (\w+) (.+)")
async def del_gc(event):
    list_name, groups = event.pattern_match.group(1), event.pattern_match.group(2).split()
    for g in groups:
        if g in SPAM_LIST.get(list_name, {}).get("groups", []):
            SPAM_LIST[list_name]["groups"].remove(g)
    save_data()
    await event.edit(f"✅ Grup dihapus dari list `{list_name}`")

@ayiin_cmd(pattern="viewlist")
async def view_list(event):
    msg = "**Daftar List Spam:**\n"
    for l, data in SPAM_LIST.items():
        gcs = data.get("groups", [])
        msg += f"\n**Nama List:** `{l}`\nGrup: {', '.join(gcs) if gcs else 'Kosong'}\n"
    await event.edit(msg)

@ayiin_cmd(pattern="listspam")
async def list_spam(event):
    msg = "**Spam Aktif:**\n"
    for g in SPAM_STATUS:
        msg += f"\nSpam Text: `{g}`"
    await event.edit(msg or "Ga ada spam jalan")

@ayiin_cmd(pattern="listfw")
async def list_fw(event):
    msg = "**Spam Forward Aktif:**\n"
    for g in SPAMFW_STATUS:
        msg += f"\nSpam Forward: `{g}`"
    await event.edit(msg or "Ga ada spam forward jalan")

@ayiin_cmd(pattern="stopspam (\w+) (.+)")
async def stop_spam(event):
    list_name, target = event.pattern_match.group(1), event.pattern_match.group(2).split()
    for g in target:
        SPAM_STATUS.pop(g, None)
    await event.edit(f"✅ Spam dihentikan di: {', '.join(target)}")

@ayiin_cmd(pattern="stopfw (\w+) (.+)")
async def stop_fw(event):
    list_name, target = event.pattern_match.group(1), event.pattern_match.group(2).split()
    for g in target:
        SPAMFW_STATUS.pop(g, None)
    await event.edit(f"✅ SpamFW dihentikan di: {', '.join(target)}")

@ayiin_cmd(pattern="(delayspam|dspam) (\d+) (\d+)(?: (.+))?")
async def delay_spam(event):
    if event.chat_id in SPAM_STATUS and SPAM_STATUS[event.chat_id]:
        return await event.edit("⚠️ Spam sedang berjalan di sini!")

    reply = await event.get_reply_message()
    delay = int(event.pattern_match.group(2))
    count = int(event.pattern_match.group(3))
    extra_text = event.pattern_match.group(4)

    media = reply.media if reply and reply.media else None

    # ambil caption
    if extra_text:
        caption = extra_text
    elif reply and reply.message:
        caption = reply.message
    else:
        caption = None

    if not media and not caption:
        return await event.edit("❌ Tidak ada media atau teks yang bisa dikirim!")

    await event.edit(f"▶️ Mulai spam {'media' if media else 'teks'} sebanyak {count}x, delay {delay}s")

    SPAM_STATUS[event.chat_id] = True

    for i in range(count):
        if not SPAM_STATUS.get(event.chat_id):
            break  # stop jika dimatikan
        try:
            if media:
                await event.client.send_file(event.chat_id, media, caption=caption)
            else:
                await event.client.send_message(event.chat_id, caption)
            await asyncio.sleep(delay)
        except Exception as e:
            print(f"❌ Gagal kirim spam: {e}")
            break

    SPAM_STATUS[event.chat_id] = False
    await event.respond("✅ Spam selesai!")

@ayiin_cmd(pattern="dspamfw (\d+) (\d+) (\w+) (https://t.me/.+)\b")
async def dspamfw_cmd(event):
    delay, amount, list_name, link = event.pattern_match.groups()
    delay, amount = int(delay), int(amount)
    if "/c/" in link:
        chatid, msgid = link.split("/c/")[1].split("/")
        chatid = int("-100" + chatid)
    else:
        username, msgid = link.split(".me/")[1].split("/")
        chatid = username
    msgid = int(msgid)

    msg = await event.client(GetMessagesRequest(peer=chatid, id=[msgid]))
    fwd = msg.messages[0]

    for g in SPAM_LIST.get(list_name, {}).get("groups", []):
        SPAMFW_STATUS[g] = True
        for _ in range(amount):
            if not SPAMFW_STATUS.get(g): break
            try:
                await event.client.forward_messages(g, fwd)
                await asyncio.sleep(delay)
            except: pass
    await event.edit("✅ dspamfw selesai.")


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
