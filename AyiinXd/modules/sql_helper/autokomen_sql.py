from sqlalchemy import Column, String, Integer
from . import BASE, SESSION

class AutoKomen(BASE):
    __tablename__ = "auto_komen"
    channel_id = Column(String(100), primary_key=True)
    trigger = Column(String(100), primary_key=True)
    reply_id = Column(Integer, nullable=True)
    reply_chat = Column(String(100), nullable=True)

    def __init__(self, channel_id, trigger, reply_id=None, reply_chat=None):
        self.channel_id = channel_id
        self.trigger = trigger
        self.reply_id = reply_id
        self.reply_chat = reply_chat

BASE.metadata.create_all(bind=SESSION.get_bind())

def add_komen(channel_id, trigger, _):
    entry = SESSION.query(AutoKomen).filter_by(channel_id=channel_id, trigger=trigger).first()
    if not entry:
        entry = AutoKomen(channel_id, trigger)
        SESSION.add(entry)
    SESSION.commit()

def get_komen_by_trigger(trigger):
    return SESSION.query(AutoKomen).filter_by(trigger=trigger).all()

def get_komen(channel_id):
    return SESSION.query(AutoKomen).filter_by(channel_id=channel_id).first()

def get_komen_by_channel(channel_id):
    return SESSION.query(AutoKomen).filter_by(channel_id=channel_id).all()

def delete_komen(channel_id):
    SESSION.query(AutoKomen).filter_by(channel_id=channel_id).delete()
    SESSION.commit()

def get_all_komen():
    return SESSION.query(AutoKomen).all()
