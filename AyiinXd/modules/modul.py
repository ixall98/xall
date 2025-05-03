import os
import re
from telethon import Button, events
from AyiinXd import CMD_HANDLER as cmd
from AyiinXd import CMD_HELP, tgbot
from AyiinXd.ayiin import ayiin_cmd

if tgbot:

    def paginate_help(page_number, loaded_modules, prefix):
        number_of_rows = 5
        number_of_cols = 2
        modules = sorted(loaded_modules)
        max_num_pages = len(modules) // (number_of_rows * number_of_cols) + \
            (1 if len(modules) % (number_of_rows * number_of_cols) != 0 else 0)
        modules = [Button.inline(mod, data=f"ub_modul_{mod}")
                   for mod in modules]
        pairs = list(zip(modules[::2], modules[1::2]))
        if len(modules) % 2 == 1:
            pairs.append((modules[-1],))
        pairs.append(
            (Button.inline("⪻", data=f"ub_page{page_number-1}"),
             Button.inline("⪼", data=f"ub_page{page_number+1}"))
        ) if max_num_pages > 1 else None
        return pairs

    @ayiin_cmd(pattern="module$")
    async def show_modules(event):
        if event.sender_id != event.client.uid and event.sender_id not in event.client._sudo:
            return
        buttons = paginate_help(0, CMD_HELP, cmd)
        await event.client.send_message(event.chat_id, "• **Daftar Modul:**", buttons=buttons)

    @tgbot.on(events.CallbackQuery(data=re.compile(b"ub_modul_(.*)")))
    async def callback_modul_handler(event):
        modul = event.data_match.group(1).decode("UTF-8")
        if modul in CMD_HELP:
            text = str(CMD_HELP[modul])
            await event.edit(
                text[:4096],  # limit telegram
                buttons=[Button.inline("« ʙᴀᴄᴋ", data="ub_page0")]
            )
        else:
            await event.answer("Modul tidak ditemukan.", alert=True)

    @tgbot.on(events.CallbackQuery(data=re.compile(b"ub_page(\d+)")))
    async def callback_page_handler(event):
        page = int(event.data_match.group(1).decode("UTF-8"))
        buttons = paginate_help(page, CMD_HELP, cmd)
        await event.edit("• **Daftar Modul:**", buttons=buttons)
