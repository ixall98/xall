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

    @tgbot.on(events.callbackquery.CallbackQuery(data=re.compile(b"ub_modul_(.*)")))
        async def on_plug_in_callback_query_handler(event):
            if event.query.user_id == uid or event.query.user_id in SUDO_USERS:
                modul_name = event.data_match.group(1).decode("UTF-8")

                cmdhel = str(CMD_HELP[modul_name])
                if len(cmdhel) > 950:
                    help_string = (
                        str(CMD_HELP[modul_name])
                        .replace("`", "")
                        .replace("**", "")[:950]
                        + "..."
                        + "\n\nBaca Teks Berikutnya Ketik .help "
                        + modul_name
                        + " "
                    )
                else:
                    help_string = (str(CMD_HELP[modul_name]).replace(
                        "`", "").replace("**", ""))

                reply_pop_up_alert = (
                    help_string
                    if help_string is not None
                    else "{} Tidak ada dokumen yang telah ditulis untuk modul.".format(
                        modul_name
                    )
                )
                await event.edit(
                    reply_pop_up_alert, buttons=[
                        Button.inline("ʙᴀᴄᴋ", data="reopen")]
                )

            else:
                reply_pop_up_alert = f"Kamu Tidak diizinkan, ini Userbot Milik {owner}"
                await event.answer(reply_pop_up_alert, cache_time=0, alert=True)
