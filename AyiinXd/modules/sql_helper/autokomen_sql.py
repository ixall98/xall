try:
    from AyiinXd.modules.sql_helper import BASE, SESSION
except ImportError:
    raise AttributeError

from sqlalchemy import BigInteger, Column, Numeric, String, UnicodeText

class AutoKomen(BASE):
    __tablename__ = "autokomen"
    channel_id = Column(String, primary_key=True)
    trigger = Column(String)
    reply = Column(String)

class LastChannel(BASE):
    __tablename__ = "autokomen_last"
    user_id = Column(String, primary_key=True, default="last")
    channel_id = Column(String)

BASE.metadata.create_all(bind=SESSION.get_bind())

def get_komen(channel_id):
    try:
        return SESSION.query(AutoKomen).filter_by(channel_id=channel_id).first()
    except Exception:
        return None

def get_all_komen():
    try:
        return SESSION.query(AutoKomen).all()
    except Exception:
        return []

def add_komen(channel_id, trigger, reply):
    komen = AutoKomen(channel_id=channel_id, trigger=trigger, reply=reply)
    SESSION.add(komen)
    SESSION.commit()

def delete_komen(channel_id):
    komen = SESSION.query(AutoKomen).filter_by(channel_id=channel_id).first()
    if komen:
        SESSION.delete(komen)
        SESSION.commit()

def set_last(channel_id):
    last = SESSION.query(LastChannel).first()
    if last:
        last.channel_id = channel_id
    else:
        last = LastChannel(channel_id=channel_id)
        SESSION.add(last)
    SESSION.commit()

def get_last():
    last = SESSION.query(LastChannel).first()
    return last.channel_id if last else None
