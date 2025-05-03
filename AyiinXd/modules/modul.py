import os
import math
import re
from telethon import Button, events
from AyiinXd import CMD_HANDLER as cmd
from AyiinXd import CMD_HELP, SUDO_USERS
from AyiinXd.ayiin import ayiin_cmd
from telethon import TelegramClient

# Mengambil BOT_TOKEN dan BOT_USERNAME dari config vars
API_ID = os.getenv('API_ID')  # Pastikan sudah ada di config vars
API_HASH = os.getenv('API_HASH')  # Pastikan sudah ada di config vars
BOT_TOKEN = os.getenv('BOT_TOKEN')  # Pastikan sudah ada di config vars

MODUL_PER_HALAMAN = 10

# Inisialisasi tgbot menggunakan token dari config vars
tgbot = TelegramClient('session_name', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@ayiin_cmd(pattern="module$")
async def show_all_modules(event):
    if event.sender_id != event.client.uid:
        return
    modul_list = sorted(list(CMD_HELP.keys()))
    total_page = math.ceil(len(modul_list) / MODUL_PER_HALAMAN)
    page = 0
    await event.edit(
        "**Daftar Modul Ubot**",
        buttons=get_modul_buttons(modul_list, page, total_page),
    )


def get_modul_buttons(modul_list, page, total_page):
    start = page * MODUL_PER_HALAMAN
    end = start + MODUL_PER_HALAMAN
    current_moduls = modul_list[start:end]

    rows = []
    for modul in current_moduls:
        rows.append([Button.inline(modul, data=f"ub_modul_{modul}")])

    nav = []
    if page > 0:
        nav.append(Button.inline("« Back", data=f"ub_page_{page - 1}"))
    if page < total_page - 1:
        nav.append(Button.inline("Next »", data=f"ub_page_{page + 1}"))
    if nav:
        rows.append(nav)

    return rows


@tgbot.on(events.callbackquery.CallbackQuery(data=re.compile(b"ub_page_(\d+)")))
async def on_page_callback(event):
    if event.query.user_id != event._bot.uid and event.query.user_id not in SUDO_USERS:
        return

    page = int(event.data_match.group(1).decode("UTF-8"))
    modul_list = sorted(list(CMD_HELP.keys()))
    total_page = math.ceil(len(modul_list) / MODUL_PER_HALAMAN)

    await event.edit(
        "**Daftar Modul Ubot**",
        buttons=get_modul_buttons(modul_list, page, total_page),
    )


@tgbot.on(events.callbackquery.CallbackQuery(data=re.compile(b"ub_modul_(.*)")))
async def on_modul_callback(event):
    if event.query.user_id != event._bot.uid and event.query.user_id not in SUDO_USERS:
        return

    modul_name = event.data_match.group(1).decode("UTF-8")
    if modul_name not in CMD_HELP:
        return await event.answer("Modul tidak ditemukan.", alert=True)

    help_str = str(CMD_HELP[modul_name])
    if len(help_str) > 950:
        help_str = (
            help_str[:950]
            + "...\n\n"
            + f"Baca teks berikutnya ketik `{cmd}help {modul_name}`"
        )

    await event.edit(
        help_str,
        buttons=[Button.inline("« Kembali", data="ub_page_0")]
    )

# Pastikan tgbot start berjalan
if __name__ == "__main__":
    tgbot.run_until_disconnected()
