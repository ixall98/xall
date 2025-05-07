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


SPAM_STATUS = {}
SPAMFW_STATUS = {}

SPAM_GC_FILE = "spam_gc.json"

def load_gc():
    if not os.path.exists(SPAM_GC_FILE):
        return []
    with open(SPAM_GC_FILE, "r") as f:
        return json.load(f)

def save_gc(gcs):
    with open(SPAM_GC_FILE, "w") as f:
        json.dump(gcs, f)

@ayiin_cmd(pattern="setgcspam(?:\\s+([\\s\\S]+))?")
async def set_gc_spam(event):
    args = event.pattern_match.group(1)
    if not args:
        return await event.edit("⚠️ Kirim username grup yang mau diset.\nContoh: `.setgcspam @gc1 @gc2`")
    
    group_list = args.split()
    saved = load_gc()
    added = []
    
    for g in group_list:
        if g not in saved:
            saved.append(g)
            added.append(g)
    save_gc(saved)
    
    if added:
        await event.edit(f"✅ Grup ditambahkan: {' '.join(added)}")
    else:
        await event.edit("⚠️ Tidak ada grup baru ditambahkan.")

@ayiin_cmd(pattern="delgcspam(?:\\s+([\\s\\S]+))?")
async def del_gc_spam(event):
    args = event.pattern_match.group(1)
    if not args:
        return await event.edit("⚠️ Kirim username grup yang mau dihapus.\nContoh: `.delgcspam @gc1`")
    
    group_list = args.split()
    saved = load_gc()
    removed = []
    
    for g in group_list:
        if g in saved:
            saved.remove(g)
            removed.append(g)
    save_gc(saved)
    
    if removed:
        await event.edit(f"✅ Grup dihapus: {' '.join(removed)}")
    else:
        await event.edit("⚠️ Grup tidak ditemukan dalam daftar.")

@ayiin_cmd(pattern="(delayspam|dspam) ([\\s\\S]*)")
async def dlyspam(event):
    input_str = event.pattern_match.group(2).split(" ", 2)
    try:
        sleeptimem = float(input_str[0])
        counter = int(input_str[1])
        spam_text = input_str[2] if len(input_str) > 2 else (await event.get_reply_message()).text
    except:
        return await event.edit("⚠️ Format salah.\nContoh: `.delayspam 3 5 tes`")
    
    targets = load_gc()
    SPAM_STATUS[event.chat_id] = True
    await event.edit("▶️ Memulai delay spam...")
    
    for i in range(counter):
        if not SPAM_STATUS.get(event.chat_id, False):
            break
        if targets:
            for gc in targets:
                try:
                    await event.client.send_message(gc, spam_text)
                except:
                    pass
        else:
            await event.client.send_message(event.chat_id, spam_text)
        await asyncio.sleep(sleeptimem)
    
    if event.chat_id in SPAM_STATUS:
        del SPAM_STATUS[event.chat_id]

@ayiin_cmd(pattern="stopdspam(?:\\s+([\\s\\S]+))?")
async def stop_dlyspam(event):
    args = event.pattern_match.group(1)
    target = event.chat_id
    if args:
        try:
            entity = await event.client.get_entity(args)
            target = entity.id
        except:
            return await event.edit("❌ Gagal menemukan grup.")
    SPAM_STATUS[target] = False
    await event.edit(f"🛑 Delay spam dihentikan di `{target}`.")

@ayiin_cmd(pattern="(delayspamfw|dspamfw) ([\\s\\S]*)")
async def dlyspamfw(event):
    input_str = event.pattern_match.group(2).split(" ", 2)
    try:
        sleeptimem = float(input_str[0])
        counter = int(input_str[1])
        link = input_str[2]
    except:
        return await event.edit("⚠️ Format salah.\nContoh: `.delayspamfw 3 5 https://t.me/xxxx/123`")

    try:
        channel = link.split("/")[3]
        msg_id = int(link.split("/")[-1])
        entity = await event.client.get_entity(channel)
        msg = await event.client.get_messages(entity, ids=msg_id)
    except:
        return await event.edit("❌ Link post salah atau tidak bisa diakses.")

    targets = load_gc()
    SPAMFW_STATUS[event.chat_id] = True
    await event.edit("▶️ Memulai forward spam...")

    for _ in range(counter):
        if not SPAMFW_STATUS.get(event.chat_id, False):
            break
        if targets:
            for gc in targets:
                try:
                    await event.client.forward_messages(gc, msg)
                except:
                    pass
        else:
            await event.client.forward_messages(event.chat_id, msg)
        await asyncio.sleep(sleeptimem)

    if event.chat_id in SPAMFW_STATUS:
        del SPAMFW_STATUS[event.chat_id]

@ayiin_cmd(pattern="stopfw(?:\\s+([\\s\\S]+))?")
async def stop_fw(event):
    args = event.pattern_match.group(1)
    target = event.chat_id
    if args:
        try:
            entity = await event.client.get_entity(args)
            target = entity.id
        except:
            return await event.edit("❌ Gagal menemukan grup.")
    SPAMFW_STATUS[target] = False
    await event.edit(f"🛑 Forward spam dihentikan di `{target}`.")

@ayiin_cmd(pattern="listdspam$")
async def list_d(event):
    if not SPAM_STATUS:
        return await event.edit("✅ Tidak ada delay spam aktif.")
    aktif = [str(cid) for cid, status in SPAM_STATUS.items() if status]
    await event.edit("**📋 Delay Spam Aktif:**\n" + "\n".join([f"• `{x}`" for x in aktif]))

@ayiin_cmd(pattern="listfw$")
async def list_fw(event):
    if not SPAMFW_STATUS:
        return await event.edit("✅ Tidak ada forward spam aktif.")
    aktif = [str(cid) for cid, status in SPAMFW_STATUS.items() if status]
    await event.edit("**📋 Forward Spam Aktif:**\n" + "\n".join([f"• `{x}`" for x in aktif]))

        
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
