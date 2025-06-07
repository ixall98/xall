from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from . import BASE, SESSION

class AutoKomen(BASE):
    __tablename__ = "autokomen"
    id = Column(Integer, primary_key=True)
    trigger = Column(String, nullable=False)
    reply = Column(String, nullable=True)
    type = Column(String, default="text")  # text or media
    channels = relationship("KomenChannel", back_populates="komen", cascade="all, delete-orphan")

class KomenChannel(BASE):
    __tablename__ = "komen_channel"
    id = Column(Integer, primary_key=True)
    trigger_id = Column(Integer, ForeignKey("autokomen.id"))
    channel_id = Column(String, nullable=False)
    komen = relationship("AutoKomen", back_populates="channels")

def add_filter(channel_id, trigger):
    with INSERTION_LOCK:
        filter = AutoKomen(channel_id=channel_id, trigger=trigger, reply="")
        SESSION.add(filter)
        SESSION.commit()

def set_komen_reply(trigger, reply, tipe="text"):
    komen = SESSION.query(AutoKomen).filter_by(trigger=trigger).first()
    if komen:
        komen.reply = reply
        komen.type = tipe
        SESSION.commit()

def add_channel_to_trigger(trigger, channel_id):
    komen = SESSION.query(AutoKomen).filter_by(trigger=trigger).first()
    if komen and not any(c.channel_id == channel_id for c in komen.channels):
        komen.channels.append(KomenChannel(channel_id=channel_id))
        SESSION.commit()

def get_komen_by_channel(channel_id):
    all_komen = SESSION.query(AutoKomen).all()
    for komen in all_komen:
        for ch in komen.channels:
            if ch.channel_id == channel_id:
                return komen
    return None

def get_all_komen():
    return SESSION.query(AutoKomen).all()

def delete_komen(trigger):
    komen = SESSION.query(AutoKomen).filter_by(trigger=trigger).first()
    if komen:
        SESSION.delete(komen)
        SESSION.commit()
