# repack by ixall. #
""" Userbot start point """

import sys
import os
import asyncpg
from importlib import import_module
from platform import python_version

from pytgcalls import __version__ as pytgcalls
from telethon import version
from telethon.tl.alltlobjects import LAYER
from AyiinXd.ayiin.events import ajg
from AyiinXd import BOT_TOKEN, bot
from AyiinXd import BOT_VER as ubotversion
from AyiinXd import BOTLOG_CHATID, LOGS, LOOP, bot
from AyiinXd.clients import ayiin_userbot_on, multiayiin
from AyiinXd.core.git import git
from AyiinXd.modules import ALL_MODULES
from AyiinXd.ayiin import AyiinDB, HOSTED_ON, autobot, autopilot, ayiin_version

# ────── 🌐 INISIALISASI DB UNTUK SFS ──────
from AyiinXd.modules.sql_helper.sfs_sql import SFSDatabase
import AyiinXd.modules.sfs as sfs_module  # inject bot dan db
sfs_db = None

async def create_sfs_tables(pool):
    await pool.execute("""
        CREATE TABLE IF NOT EXISTS sfs_config (
            admin_id BIGINT PRIMARY KEY,
            admin_channel TEXT
        );
    """)
    await pool.execute("""
        CREATE TABLE IF NOT EXISTS sfs_data (
            user_id BIGINT PRIMARY KEY,
            username TEXT,
            status TEXT,
            admin_channel TEXT,
            user_channel TEXT
        );
    """)

async def init_sfs_db():
    global sfs_db
    dsn = os.environ.get("DATABASE_URL")
    if dsn is None:
        LOGS.warning("[SFS] DATABASE_URL tidak ditemukan di env!")
        return

    dsn = dsn.replace("postgres://", "postgresql://", 1)
    try:
        pool = await asyncpg.create_pool(dsn)
        await create_sfs_tables(pool)  # 🔥 auto create table
        sfs_db = SFSDatabase(pool)
        sfs_module.sfs_db = sfs_db
        sfs_module.bot = bot
        LOOP.create_task(sfs_module.sfs_checker())
        LOGS.info("[SFS] PostgreSQL berhasil terkoneksi dan tabel siap.")
    except Exception as e:
        LOGS.warning(f"[SFS] Gagal konek ke database: {e}")

# ─────────────────────────────────────────

try:
    for module_name in ALL_MODULES:
        imported_module = import_module(f"AyiinXd.modules.{module_name}")
    adB = AyiinDB()
    client = multiayiin()
    git()
    LOGS.info(f"Python Version - {python_version()}")
    LOGS.info(f"Telethon Version - {version.__version__} [Layer: {LAYER}]")
    LOGS.info(f"PyTgCalls Version - {pytgcalls}")
    LOGS.info(f"Userbot Version - {ubotversion} •[{adB.name}]•")
    LOGS.info(f"Mutya Version - {ayiin_version} •[{HOSTED_ON}]•")
    LOGS.info("[💀 BERHASIL DIAKTIFKAN! 💀]")
except (ConnectionError, KeyboardInterrupt, NotImplementedError, SystemExit):
    pass
except BaseException as e:
    LOGS.info(str(e), exc_info=True)
    sys.exit(1)

# start userbot
LOOP.run_until_complete(ayiin_userbot_on())
LOOP.run_until_complete(init_sfs_db())  # init koneksi DB SFS
LOOP.run_until_complete(ajg())

if not BOTLOG_CHATID:
    LOOP.run_until_complete(autopilot())
if not BOT_TOKEN:
    LOOP.run_until_complete(autobot())

if len(sys.argv) not in (1, 3, 4):
    bot.disconnect()
else:
    try:
        bot.run_until_disconnected()
    except ConnectionError:
        pass
