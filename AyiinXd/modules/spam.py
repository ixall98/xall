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

@ayiin_cmd(pattern="setgc ([^ ]+) (.+)")
async def set_gc(event):
    listname, groups = event.pattern_match.group(1), event.pattern_match.group(2).split()
    data = load_gc()
    data[listname] = groups
    save_gc(data)
    await event.edit(f"✅ Grup untuk list `{listname}` disimpan.")

@ayiin_cmd(pattern="delgc ([^ ]+) ([^ ]+)")
async def del_gc(event):
    listname, target = event.pattern_match.group(1), event.pattern_match.group(2)
    data = load_gc()
    if listname not in data or target not in data[listname]:
        return await event.edit("⚠️ Grup tidak ditemukan di list.")
    data[listname].remove(target)
    if not data[listname]:
        del data[listname]
    save_gc(data)
    await event.edit(f"✅ Grup `{target}` dihapus dari list `{listname}`.")

@ayiin_cmd(pattern="viewgc$")
async def view_gc(event):
    data = load_gc()
    if not data:
        return await event.edit("📭 Belum ada list grup yang disimpan.")
    txt = "**📋 List Grup Spam:**\n"
    for name, grups in data.items():
        txt += f"\n**{name}**:\n"
        for g in grups:
            txt += f"• `{g}`\n"
    await event.edit(txt)
    
@ayiin_cmd(pattern="(delayspam|dspam|dspm) ([\\s\\S]*)")
async def delayspam(event):
    args = event.pattern_match.group(2).split(" ", 3)
    if len(args) < 4:
        return await eod(event, "⚠️ Format salah. Gunakan `.delayspam <delay> <jumlah> <namalist> <teks>`")

    delay, jumlah, listname, text = args
    try:
        delay = float(delay)
        jumlah = int(jumlah)
    except ValueError:
        return await eod(event, "⚠️ Delay dan jumlah harus berupa angka.")

    data = load_gc()
    if listname not in data:
        return await eod(event, f"❌ List `{listname}` tidak ditemukan.")

    await event.edit("🚀 Memulai delay spam...")
    for _ in range(jumlah):
        for gc in data[listname]:
            try:
                await event.client.send_message(gc, text)
                await asyncio.sleep(delay)
            except Exception as e:
                await event.client.send_message(event.chat_id, f"Gagal kirim ke {gc}: {e}")
        await asyncio.sleep(delay)

    if BOTLOG_CHATID:
        await event.client.send_message(BOTLOG_CHATID, f"✅ `.delayspam` ke list `{listname}` selesai.")

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

@ayiin_cmd(pattern="(delayspamfw|dspamfw|dpmfw) ([\\s\\S]*)")
async def delayspamfw(event):
    args = event.pattern_match.group(2).split(" ", 3)
    if len(args) < 4:
        return await eod(event, "⚠️ Format salah. Gunakan `.delayspamfw <delay> <jumlah> <namalist> <link_post>`")

    delay, jumlah, listname, link = args
    try:
        delay = float(delay)
        jumlah = int(jumlah)
    except ValueError:
        return await eod(event, "⚠️ Delay dan jumlah harus berupa angka.")

    data = load_gc()
    if listname not in data:
        return await eod(event, f"❌ List `{listname}` tidak ditemukan.")

    try:
        channel_username = link.split("/")[3]
        message_id = int(link.split("/")[-1])
        channel = await event.client.get_entity(channel_username)
    except Exception:
        return await eod(event, "❌ Link tidak valid.")

    await event.edit("🚀 Memulai forward spam...")
    for _ in range(jumlah):
        for gc in data[listname]:
            try:
                await event.client.forward_messages(gc, message_id, channel)
                await asyncio.sleep(delay)
            except Exception as e:
                await event.client.send_message(event.chat_id, f"Gagal kirim ke {gc}: {e}")
        await asyncio.sleep(delay)

    if BOTLOG_CHATID:
        await event.client.send_message(BOTLOG_CHATID, f"✅ `.delayspamfw` ke list `{listname}` selesai.")

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
