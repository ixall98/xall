try:
    from AyiinXd.modules.sql_helper import BASE, SESSION
except ImportError:
    raise AttributeError

from sqlalchemy import BigInteger, Column, Numeric, String, UnicodeText

class AutoKomen(BASE):
    __tablename__ = "auto_komen"
    channel_id = Column(String(20), primary_key=True)
    trigger = Column(String(100))
    reply = Column(String(400))

    def __init__(self, channel_id, trigger, reply):
        self.channel_id = channel_id
        self.trigger = trigger
        self.reply = reply

def add_komen(channel_id, trigger, reply):
    komen = AutoKomen(channel_id, trigger, reply)
    SESSION.merge(komen)
    SESSION.commit()

def get_komen(channel_id):
    return SESSION.query(AutoKomen).filter_by(channel_id=channel_id).first()

def get_all_komen():
    return SESSION.query(AutoKomen).all()

def delete_komen(channel_id):
    row = get_komen(channel_id)
    if row:
        SESSION.delete(row)
        SESSION.commit()
