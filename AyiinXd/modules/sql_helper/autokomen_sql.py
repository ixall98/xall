from sqlalchemy import Column, String, Integer, Text
from . import BASE, SESSION
import threading

# 🔒 Lock biar thread-safe saat insert/update
INSERTION_LOCK = threading.RLock()

# 🗂️ Tabel utama untuk auto-komen
class AutoKomen(BASE):
    __tablename__ = "auto_komen"
    channel_id = Column(String(100), primary_key=True)
    trigger = Column(String(100), primary_key=True)
    reply = Column(Text)
    msg_id = Column(Integer)        # NEW
    msg_chat = Column(Integer)      # NEW

    def __init__(self, channel_id, trigger, reply, msg_id=None, msg_chat=None):
        self.channel_id = channel_id
        self.trigger = trigger
        self.reply = reply
        self.msg_id = msg_id
        self.msg_chat = msg_chat


# ➕ Tambah filter baru ke channel
def add_filter(channel_id, trigger):
    with INSERTION_LOCK:
        komen = AutoKomen(channel_id, trigger, "")
        SESSION.add(komen)
        SESSION.commit()


# 📝 Set teks balasan (komen) dari trigger
def set_reply(channel_id, trigger, reply=None, msg_id=None, msg_chat=None):
    with INSERTION_LOCK:
        komen = SESSION.query(AutoKomen).filter_by(channel_id=channel_id, trigger=trigger).first()
        if not komen:
            komen = AutoKomen(channel_id, trigger, reply, msg_id, msg_chat)
            SESSION.add(komen)
        else:
            komen.reply = reply
            komen.msg_id = msg_id
            komen.msg_chat = msg_chat
        SESSION.commit()

# 🔍 Ambil semua trigger dari satu channel
def get_triggers(channel_id):
    return SESSION.query(AutoKomen).filter_by(channel_id=channel_id).all()


# 🔍 Cek satu trigger spesifik
def get_komen(channel_id, trigger):
    return SESSION.query(AutoKomen).filter_by(channel_id=channel_id, trigger=trigger).first()


# ❌ Hapus trigger dari satu channel
def delete_trigger(channel_id, trigger):
    with INSERTION_LOCK:
        SESSION.query(AutoKomen).filter_by(channel_id=channel_id, trigger=trigger).delete()
        SESSION.commit()


# ❌ Hapus semua trigger dari satu channel
def delete_channel(channel_id):
    with INSERTION_LOCK:
        SESSION.query(AutoKomen).filter_by(channel_id=channel_id).delete()
        SESSION.commit()


# 📋 Ambil semua data auto komen
def get_all_komen():
    return SESSION.query(AutoKomen).all()
