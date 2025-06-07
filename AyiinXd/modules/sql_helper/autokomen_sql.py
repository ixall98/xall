from sqlalchemy import Column, String
from . import BASE, SESSION
import threading
import json

INSERTION_LOCK = threading.RLock()

class AutoKomen(BASE):
    __tablename__ = "auto_komen"
    channel_id = Column(String(100), primary_key=True)
    trigger = Column(String(100), primary_key=True)
    reply = Column(String, default="")
    msg_id = Column(String(50), default=None)
    msg_chat = Column(String(50), default=None)

    def __init__(self, channel_id, trigger, reply="", msg_id=None, msg_chat=None):
        self.channel_id = channel_id
        self.trigger = trigger
        self.reply = reply
        self.msg_id = msg_id
        self.msg_chat = msg_chat

class LastAutoKomen(BASE):
    __tablename__ = "last_auto_komen"
    user_id = Column(String(14), primary_key=True)
    channel_id = Column(String)  # bisa simpan JSON list string

def add_filter(channel_id, trigger):
    with INSERTION_LOCK:
        komen = AutoKomen(channel_id, trigger)
        SESSION.add(komen)
        SESSION.commit()

def set_reply(channel_id, trigger, msg_id=None, msg_chat=None, reply=None):
    with INSERTION_LOCK:
        komen = SESSION.query(AutoKomen).filter_by(channel_id=channel_id, trigger=trigger).first()
        if komen:
            komen.reply = reply or ""
            komen.msg_id = msg_id
            komen.msg_chat = msg_chat
        else:
            komen = AutoKomen(
                channel_id=channel_id,
                trigger=trigger,
                reply=reply or "",
                msg_id=msg_id,
                msg_chat=msg_chat
            )
            SESSION.add(komen)
        SESSION.commit()
        
def get_triggers(channel_id):
    return SESSION.query(AutoKomen).filter_by(channel_id=channel_id).all()

def get_komen(channel_id, trigger):
    return SESSION.query(AutoKomen).filter_by(channel_id=channel_id, trigger=trigger).first()

def delete_trigger(channel_id, trigger):
    with INSERTION_LOCK:
        SESSION.query(AutoKomen).filter_by(channel_id=channel_id, trigger=trigger).delete()
        SESSION.commit()

def delete_channel(channel_id):
    with INSERTION_LOCK:
        SESSION.query(AutoKomen).filter_by(channel_id=channel_id).delete()
        SESSION.commit()

def get_all_komen():
    return SESSION.query(AutoKomen).all()

def set_last(user_id, channel_id):
    with INSERTION_LOCK:
        last = SESSION.query(LastAutoKomen).get(str(user_id))
        if not last:
            last = LastAutoKomen(
                user_id=str(user_id),
                channel_id=json.dumps([channel_id])  # simpan list
            )
            SESSION.add(last)
        else:
            existing = json.loads(last.channel_id or "[]")
            if channel_id not in existing:
                existing.append(channel_id)
                last.channel_id = json.dumps(existing)
        SESSION.commit()

def get_last(user_id):
    last = SESSION.query(LastAutoKomen).get(str(user_id))
    if last:
        return json.loads(last.channel_id)  # balikin list
    return []

    # Hapus komen berdasarkan channel & trigger
def delete_reply(channel_id, trigger):
    with INSERTION_LOCK:
        komen = SESSION.query(AutoKomen).filter_by(channel_id=channel_id, trigger=trigger).first()
        if komen:
            komen.reply = ""
            SESSION.commit()

# Ambil semua komen (trigger + reply) dari satu channel
def get_all_replies(channel_id):
    return SESSION.query(AutoKomen).filter(AutoKomen.channel_id == channel_id, AutoKomen.reply != "").all()
