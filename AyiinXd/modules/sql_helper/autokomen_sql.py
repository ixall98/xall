from sqlalchemy import Column, String, Integer, PickleType
from AyiinXd.modules.sql_helper import BASE, SESSION

class AutoKomen(BASE):
    __tablename__ = "autokomen_multi"
    channel_id = Column(String, primary_key=True)
    trigger = Column(String, primary_key=True)
    reply_id = Column(Integer)

class PendingKomen(BASE):
    __tablename__ = "pending_autokomen"
    user_id = Column(String, primary_key=True)
    trigger = Column(String)
    channels = Column(PickleType)  # Simpan list channel

BASE.metadata.create_all(bind=SESSION.get_bind())

def set_pending(user_id, trigger, channels):
    old = SESSION.query(PendingKomen).filter_by(user_id=str(user_id)).first()
    if old:
        old.trigger = trigger
        old.channels = channels
    else:
        pending = PendingKomen(user_id=str(user_id), trigger=trigger, channels=channels)
        SESSION.add(pending)
    SESSION.commit()

def get_pending(user_id):
    data = SESSION.query(PendingKomen).filter_by(user_id=str(user_id)).first()
    if data:
        return data.trigger, data.channels
    return None

def add_komen(channel_id, trigger, reply_id):
    komen = AutoKomen(channel_id=channel_id, trigger=trigger, reply_id=reply_id)
    SESSION.merge(komen)
    SESSION.commit()

def get_komen_by_channel(channel_id):
    return SESSION.query(AutoKomen).filter_by(channel_id=channel_id).all()
