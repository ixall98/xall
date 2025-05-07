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



# Lokasi file penyimpanan list grup
GC_FILE = "dspam_gc.json"
if not os.path.exists(GC_FILE):
    with open(GC_FILE, "w") as f:
        json.dump({}, f)

def load_gc():
    with open(GC_FILE, "r") as f:
        return json.load(f)

def save_gc(data):
    with open(GC_FILE, "w") as f:
        json.dump(data, f, indent=2)


SPAM_STATUS = {}
SPAMFW_STATUS = {}
SPAM_GROUPS = {}  # format: {user_id: [group_ids]}

@ayiin_cmd(pattern="setgc(?: |$)(.*)")
async def set_gc(event):
    if event.is_private:
        return await event.edit("❌ Command ini hanya bisa digunakan di grup.")
    user_id = event.sender_id
    chat_id = event.chat_id
    if user_id not in SPAM_GROUPS:
        SPAM_GROUPS[user_id] = []
    if chat_id not in SPAM_GROUPS[user_id]:
        SPAM_GROUPS[user_id].append(chat_id)
        await event.edit("✅ Grup ini berhasil diset sebagai target spam.")
    else:
        await event.edit("⚠️ Grup ini sudah ada dalam daftar.")

@ayiin_cmd(pattern="delgc(?: |$)(.*)")
async def del_gc(event):
    user_id = event.sender_id
    chat_id = event.chat_id
    if user_id in SPAM_GROUPS and chat_id in SPAM_GROUPS[user_id]:
        SPAM_GROUPS[user_id].remove(chat_id)
        await event.edit("✅ Grup ini berhasil dihapus dari daftar spam.")
    else:
        await event.edit("⚠️ Grup ini belum ada dalam daftar.")

@ayiin_cmd(pattern="listgc$")
async def list_gc(event):
    user_id = event.sender_id
    if user_id not in SPAM_GROUPS or not SPAM_GROUPS[user_id]:
        return await event.edit("📭 Daftar grup spam kamu kosong.")
    teks = "**📋 Daftar Grup Spam-mu:**\n"
    for x in SPAM_GROUPS[user_id]:
        teks += f"• `{x}`\n"
    await event.edit(teks)

@ayiin_cmd(pattern="(delayspam|dspam) (.+)")
async def dlyspam(event):
    args = event.pattern_match.group(2).split(" ", 2)
    if len(args) < 2:
        return await eod(event, "⚠️ Format salah. Gunakan: `.delayspam <delay> <jumlah> <teks>`")
    try:
        delay = float(args[0])
        jumlah = int(args[1])
        teks = args[2] if len(args) > 2 else (await event.get_reply_message()).text
    except Exception:
        return await eod(event, "⚠️ Format salah. Delay dan jumlah harus angka.")

    if not teks:
        return await eod(event, "⚠️ Tidak ada teks untuk di-spam.")

    user_id = event.sender_id
    SPAM_STATUS[user_id] = True
    await event.edit("🚀 Delay spam dimulai...")

    target_chats = SPAM_GROUPS.get(user_id, [event.chat_id])
    await delay_spam_function(event, teks, delay, jumlah, target_chats)

async def delay_spam_function(event, text, delay, jumlah, target_chats):
    user_id = event.sender_id
    for chat_id in target_chats:
        for _ in range(jumlah):
            if not SPAM_STATUS.get(user_id, False):
                break
            try:
                await event.client.send_message(chat_id, text)
                await asyncio.sleep(delay)
            except Exception as e:
                await event.client.send_message(event.chat_id, f"❌ Error kirim ke `{chat_id}`: {str(e)}")

    if BOTLOG_CHATID:
        await event.client.send_message(
            BOTLOG_CHATID,
            f"✅ **delayspam selesai**\n\n**Grup:**\n" +
            "".join([f"• `{x}`\n" for x in target_chats]) +
            f"**Delay:** `{delay}`\n**Jumlah:** `{jumlah}`\n**Teks:** `{text}`"
        )

@ayiin_cmd(pattern="stopdspam$")
async def stop_dspam(event):
    user_id = event.sender_id
    SPAM_STATUS[user_id] = False
    await event.edit("🛑 Delay spam berhasil dihentikan.")

@ayiin_cmd(pattern="listdspam$")
async def listdspam(event):
    aktif = [str(uid) for uid, val in SPAM_STATUS.items() if val]
    if not aktif:
        return await event.edit("✅ Tidak ada delay spam yang aktif.")
    teks = "**📋 Delay Spam Aktif:**\n"
    teks += "\n".join([f"• `{x}`" for x in aktif])
    await event.edit(teks)

# ===================== FORWARD SPAM ======================

@ayiin_cmd(pattern="(delayspamfw|dspamfw) (.+)")
async def dlyspamfw(event):
    args = event.pattern_match.group(2).split(" ", 2)
    if len(args) < 3:
        return await eod(event, "⚠️ Format salah. Gunakan: `.delayspamfw <delay> <jumlah> <link_post>`")
    try:
        delay = float(args[0])
        jumlah = int(args[1])
        link = args[2]
        msg_id = int(link.split("/")[-1])
        ch_user = link.split("/")[3]
        channel = await event.client.get_entity(ch_user)
        msg = await event.client.get_messages(channel, ids=msg_id)
    except Exception as e:
        return await eod(event, f"❌ Error ambil pesan: {str(e)}")

    user_id = event.sender_id
    SPAMFW_STATUS[user_id] = True
    await event.edit("🚀 Delay forward dimulai...")

    target_chats = SPAM_GROUPS.get(user_id, [event.chat_id])
    await delay_spamfw_function(event, msg, delay, jumlah, target_chats)

async def delay_spamfw_function(event, message, delay, jumlah, target_chats):
    user_id = event.sender_id
    for chat_id in target_chats:
        for _ in range(jumlah):
            if not SPAMFW_STATUS.get(user_id, False):
                break
            try:
                await event.client.forward_messages(chat_id, message)
                await asyncio.sleep(delay)
            except Exception as e:
                await event.client.send_message(event.chat_id, f"❌ Error kirim ke `{chat_id}`: {str(e)}")

    if BOTLOG_CHATID:
        await event.client.send_message(
            BOTLOG_CHATID,
            f"✅ **delayspamfw selesai**\n\n**Grup:**\n" +
            "".join([f"• `{x}`\n" for x in target_chats]) +
            f"**Delay:** `{delay}`\n**Jumlah:** `{jumlah}`\n**Pesan:** `{message.text[:50]}...`"
        )

@ayiin_cmd(pattern="stopfw$")
async def stop_fw(event):
    user_id = event.sender_id
    SPAMFW_STATUS[user_id] = False
    await event.edit("🛑 Forward spam berhasil dihentikan.")

@ayiin_cmd(pattern="listfw$")
async def listfw(event):
    aktif = [str(uid) for uid, val in SPAMFW_STATUS.items() if val]
    if not aktif:
        return await event.edit("✅ Tidak ada forward spam yang aktif.")
    teks = "**📋 Forward Spam Aktif:**\n"
    teks += "\n".join([f"• `{x}`" for x in aktif])
    await event.edit(teks)


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
