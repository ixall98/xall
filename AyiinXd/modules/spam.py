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
import asyncio
import json
import os
from telethon import events
from telethon.tl.functions.messages import ForwardMessagesRequest
from AyiinXd import ayiin, CMD_HANDLER as cmd
from AyiinXd.ayiin import ayiin_cmd

SPAM_DIR = "spam_data"
if not os.path.exists(SPAM_DIR):
    os.makedirs(SPAM_DIR)

SPAM_STATUS = {}
SPAMFW_STATUS = {}

def save_list(name, data):
    with open(f"{SPAM_DIR}/{name}.json", "w") as f:
        json.dump(data, f)

def load_list(name):
    try:
        with open(f"{SPAM_DIR}/{name}.json") as f:
            return json.load(f)
    except:
        return {}

@ayiin_cmd(pattern="setgc (\w+) (.+)")
async def setgc(event):
    name, groups = event.pattern_match.group(1), event.pattern_match.group(2).split()
    data = load_list(name)
    data["groups"] = list(set(data.get("groups", []) + groups))
    save_list(name, data)
    await event.edit(f"✅ Grup ditambahkan ke list `{name}`.")

@ayiin_cmd(pattern="delgc (\w+) (.+)")
async def delgc(event):
    name, groups = event.pattern_match.group(1), event.pattern_match.group(2).split()
    data = load_list(name)
    if "groups" in data:
        data["groups"] = [g for g in data["groups"] if g not in groups]
        save_list(name, data)
        await event.edit(f"✅ Grup dihapus dari list `{name}`.")
    else:
        await event.edit("⚠️ Grup tidak ditemukan.")

@ayiin_cmd(pattern="viewlist$")
async def viewlist(event):
    lists = os.listdir(SPAM_DIR)
    msg = "**List Spam Aktif:**\n\n"
    for file in lists:
        name = file.replace(".json", "")
        data = load_list(name)
        msg += f"**{name}**: {', '.join(data.get('groups', []))}\n"
    await event.edit(msg)

@ayiin_cmd(pattern="listspam$")
async def listspam(event):
    msg = "**Spam Aktif (Teks):**\n"
    for k in SPAM_STATUS:
        msg += f"- {k}\n"
    await event.edit(msg)

@ayiin_cmd(pattern="listfw$")
async def listfw(event):
    msg = "**Spam Aktif (Forward):**\n"
    for k in SPAMFW_STATUS:
        msg += f"- {k}\n"
    await event.edit(msg)

@ayiin_cmd(pattern="stopspam (\w+) (.+)")
async def stopspam(event):
    name, groups = event.pattern_match.group(1), event.pattern_match.group(2).split()
    for g in groups:
        SPAM_STATUS.pop((name, g), None)
    await event.edit(f"✅ Spam dihentikan untuk `{groups}` dari list `{name}`.")

@ayiin_cmd(pattern="stopfw (\w+) (.+)")
async def stopfw(event):
    name, groups = event.pattern_match.group(1), event.pattern_match.group(2).split()
    for g in groups:
        SPAMFW_STATUS.pop((name, g), None)
    await event.edit(f"✅ Spam forward dihentikan untuk `{groups}` dari list `{name}`.")

@ayiin_cmd(pattern="dspam(?: (\d+) (\d+) (\w+))?")
async def dspam(event):
    args = event.pattern_match.groups()
    if not args[0]:
        return await event.edit("⚠️ Gunakan `.dspam <delay> <jumlah> <namalist>` dan reply teks/media.")
    delay, jumlah, name = int(args[0]), int(args[1]), args[2]
    reply = await event.get_reply_message()
    if not reply:
        return await event.edit("⚠️ Reply media atau teks untuk disebar.")
    data = load_list(name)
    if not data or "groups" not in data:
        return await event.edit("⚠️ List atau grup tidak ditemukan.")

    for g in data["groups"]:
        SPAM_STATUS[(name, g)] = True

    await event.edit(f"✅ Mulai spam ke `{len(data['groups'])}` grup dari list `{name}`.")

    for i in range(jumlah):
        for g in data["groups"]:
            if not SPAM_STATUS.get((name, g)):
                continue
            try:
                if reply.media:
                    await reply.forward_to(g)
                else:
                    await ayiin.send_message(g, reply.text)
            except Exception:
                continue
            await asyncio.sleep(delay)

    for g in data["groups"]:
        SPAM_STATUS.pop((name, g), None)

@ayiin_cmd(pattern="dspamfw(?: (\d+) (\d+) (\w+))?")
async def dspamfw(event):
    args = event.pattern_match.groups()
    if not args[0]:
        return await event.edit("⚠️ Gunakan `.dspamfw <delay> <jumlah> <namalist>` dan reply media dari channel.")
    delay, jumlah, name = int(args[0]), int(args[1]), args[2]
    reply = await event.get_reply_message()
    if not reply or not reply.forward:
        return await event.edit("⚠️ Reply media yang diforward dari channel.")
    data = load_list(name)
    if not data or "groups" not in data:
        return await event.edit("⚠️ List atau grup tidak ditemukan.")

    for g in data["groups"]:
        SPAMFW_STATUS[(name, g)] = True

    await event.edit(f"✅ Mulai spam forward ke `{len(data['groups'])}` grup dari list `{name}`.")

    for _ in range(jumlah):
        for g in data["groups"]:
            if not SPAMFW_STATUS.get((name, g)):
                continue
            try:
                await ayiin(ForwardMessagesRequest(
                    from_peer=reply.forward.chat,
                    id=[reply.id],
                    to_peer=g
                ))
            except Exception:
                continue
            await asyncio.sleep(delay)

    for g in data["groups"]:
        SPAMFW_STATUS.pop((name, g), None)


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
