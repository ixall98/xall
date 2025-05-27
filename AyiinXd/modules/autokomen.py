from telethon import events
from AyiinXd import client
from AyiinXd.events import ayiin_cmd

# Struktur data: 
# {channel_id: {filter_text: response_text}}
AUTO_KOMEN_DATA = {}

# Untuk simpan channel yang dipantau
WATCHED_CHANNELS = set()

def get_chat_id_from_input(chat_input):
    # Bisa dikembangin pakai client.get_entity, sekarang kita asumsikan input id/username langsung
    return chat_input

@ayiin_cmd(pattern=r"setch(?: |$)(.*)")
async def set_channel(event):
    chat_input = event.pattern_match.group(1).strip()
    if not chat_input:
        return await event.reply("Masukin channel username atau ID yang mau ditambah.")
    try:
        chat = await client.get_entity(chat_input)
        WATCHED_CHANNELS.add(chat.id)
        if chat.id not in AUTO_KOMEN_DATA:
            AUTO_KOMEN_DATA[chat.id] = {}
        await event.reply(f"Berhasil tambah channel: {chat.title} ({chat.id}) untuk auto komen.")
    except Exception as e:
        await event.reply(f"Gagal tambah channel: {e}")

@ayiin_cmd(pattern=r"delch(?: |$)(.*)")
async def del_channel(event):
    chat_input = event.pattern_match.group(1).strip()
    if not chat_input:
        return await event.reply("Masukin channel username atau ID yang mau dihapus.")
    try:
        chat = await client.get_entity(chat_input)
        if chat.id in WATCHED_CHANNELS:
            WATCHED_CHANNELS.remove(chat.id)
            AUTO_KOMEN_DATA.pop(chat.id, None)
            await event.reply(f"Berhasil hapus channel: {chat.title} ({chat.id}) dari auto komen.")
        else:
            await event.reply("Channel ini belum terdaftar.")
    except Exception as e:
        await event.reply(f"Gagal hapus channel: {e}")

@ayiin_cmd(pattern=r"setfilter(?: |$)(.*)")
async def set_filter(event):
    text = event.pattern_match.group(1).strip()
    if "|" not in text:
        return await event.reply("Format salah. Contoh:\n.setfilter <channel> | <filter_text>")
    chat_input, filter_text = map(str.strip, text.split("|", 1))
    try:
        chat = await client.get_entity(chat_input)
        if chat.id not in WATCHED_CHANNELS:
            return await event.reply("Channel belum terdaftar. Tambahkan dulu pake .setch")
        if chat.id not in AUTO_KOMEN_DATA:
            AUTO_KOMEN_DATA[chat.id] = {}
        if filter_text in AUTO_KOMEN_DATA[chat.id]:
            return await event.reply("Filter sudah ada di channel ini.")
        AUTO_KOMEN_DATA[chat.id][filter_text] = ""  # respon belum di set
        await event.reply(f"Berhasil tambah filter `{filter_text}` di channel {chat.title}. Jangan lupa setkomen ya!")
    except Exception as e:
        await event.reply(f"Gagal tambah filter: {e}")

@ayiin_cmd(pattern=r"delfilter(?: |$)(.*)")
async def del_filter(event):
    text = event.pattern_match.group(1).strip()
    if "|" not in text:
        return await event.reply("Format salah. Contoh:\n.delfilter <channel> | <filter_text>")
    chat_input, filter_text = map(str.strip, text.split("|", 1))
    try:
        chat = await client.get_entity(chat_input)
        if chat.id not in WATCHED_CHANNELS:
            return await event.reply("Channel belum terdaftar.")
        if chat.id in AUTO_KOMEN_DATA and filter_text in AUTO_KOMEN_DATA[chat.id]:
            AUTO_KOMEN_DATA[chat.id].pop(filter_text)
            await event.reply(f"Berhasil hapus filter `{filter_text}` dari channel {chat.title}.")
        else:
            await event.reply("Filter tidak ditemukan di channel ini.")
    except Exception as e:
        await event.reply(f"Gagal hapus filter: {e}")

@ayiin_cmd(pattern=r"setkomen(?: |$)(.*)")
async def set_komen(event):
    text = event.pattern_match.group(1).strip()
    if "|" not in text:
        return await event.reply("Format salah. Contoh:\n.setkomen <channel> | <filter_text> | <response_text>")
    try:
        parts = list(map(str.strip, text.split("|")))
        if len(parts) != 3:
            return await event.reply("Format salah. Contoh:\n.setkomen <channel> | <filter_text> | <response_text>")
        chat_input, filter_text, response_text = parts
        chat = await client.get_entity(chat_input)
        if chat.id not in WATCHED_CHANNELS:
            return await event.reply("Channel belum terdaftar.")
        if chat.id not in AUTO_KOMEN_DATA or filter_text not in AUTO_KOMEN_DATA[chat.id]:
            return await event.reply("Filter belum ada, set dulu pakai .setfilter")
        AUTO_KOMEN_DATA[chat.id][filter_text] = response_text
        await event.reply(f"Berhasil set komen untuk filter `{filter_text}` di channel {chat.title}.")
    except Exception as e:
        await event.reply(f"Gagal set komen: {e}")

@ayiin_cmd(pattern=r"delkomen(?: |$)(.*)")
async def del_komen(event):
    text = event.pattern_match.group(1).strip()
    if "|" not in text:
        return await event.reply("Format salah. Contoh:\n.delkomen <channel> | <filter_text>")
    chat_input, filter_text = map(str.strip, text.split("|", 1))
    try:
        chat = await client.get_entity(chat_input)
        if chat.id not in WATCHED_CHANNELS:
            return await event.reply("Channel belum terdaftar.")
        if chat.id in AUTO_KOMEN_DATA and filter_text in AUTO_KOMEN_DATA[chat.id]:
            AUTO_KOMEN_DATA[chat.id][filter_text] = ""
            await event.reply(f"Berhasil hapus komen untuk filter `{filter_text}` di channel {chat.title}.")
        else:
            await event.reply("Filter tidak ditemukan di channel ini.")
    except Exception as e:
        await event.reply(f"Gagal hapus komen: {e}")

@ayiin_cmd(pattern="listkomen$")
async def list_komen(event):
    if not WATCHED_CHANNELS:
        return await event.reply("Belum ada channel yang dipantau.")
    msg = "**Daftar Auto Komen:**\n"
    for cid in WATCHED_CHANNELS:
        try:
            chat = await client.get_entity(cid)
            msg += f"\nChannel: {chat.title} ({cid})\n"
            if cid in AUTO_KOMEN_DATA and AUTO_KOMEN_DATA[cid]:
                for filt, resp in AUTO_KOMEN_DATA[cid].items():
                    msg += f"• Filter: `{filt}`\n  Response: `{resp or '-tidak ada respon-'}`\n"
            else:
                msg += "• Tidak ada filter atau respon.\n"
        except:
            msg += f"\nChannel: {cid} (Gagal load info)\n"
    await event.reply(msg)

@client.on(events.NewMessage())
async def auto_reply(event):
    cid = event.chat_id
    if cid in WATCHED_CHANNELS:
        text = event.raw_text.lower()
        if cid in AUTO_KOMEN_DATA:
            for filt, resp in AUTO_KOMEN_DATA[cid].items():
                if filt.lower() in text and resp:
                    try:
                        await event.reply(resp)
                        break
                    except Exception as e:
                        print(f"Gagal auto komen: {e}")
