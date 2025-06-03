try:
    from AyiinXd.modules.sql_helper import BASE, SESSION
except ImportError:
    raise AttributeError("Gagal import SQL Helper")

from sqlalchemy import Column, String

class AutoKomen(BASE):
    __tablename__ = "autokomen"
    id = Column(String, primary_key=True)  # "<channel_id>|<trigger>"
    channel_id = Column(String)
    trigger = Column(String)
    reply_id = Column(String, nullable=True)
    reply_chat = Column(String, nullable=True)

BASE.metadata.create_all(bind=SESSION.get_bind())

def add_komen(channel_id: str, trigger: str, reply_id: str = "", reply_chat: str = ""):
    komen_id = f"{channel_id}|{trigger}"
    komen = AutoKomen(id=komen_id, channel_id=channel_id, trigger=trigger, reply_id=reply_id, reply_chat=reply_chat)
    SESSION.merge(komen)
    SESSION.commit()

def get_komen(channel_id: str, trigger: str):
    komen_id = f"{channel_id}|{trigger}"
    return SESSION.query(AutoKomen).filter_by(id=komen_id).first()

def get_all_komen():
    return SESSION.query(AutoKomen).all()

def get_komen_by_channel(channel_id: str):
    return SESSION.query(AutoKomen).filter_by(channel_id=channel_id).all()

def get_komen_by_trigger(trigger: str):
    return SESSION.query(AutoKomen).filter_by(trigger=trigger).all()

def delete_komen(channel_id: str, trigger: str):
    komen = get_komen(channel_id, trigger)
    if komen:
        SESSION.delete(komen)
        SESSION.commit()

def delete_channel(channel_id: str):
    rows = get_komen_by_channel(channel_id)
    for row in rows:
        SESSION.delete(row)
    SESSION.commit()
