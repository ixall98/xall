# modules/sql/autokomen_sql.py
from sqlalchemy import Column, String, Integer
from AyiinXd import BASE, SESSION

class AutoKomen(BASE):
    __tablename__ = "autokomen"
    id = Column(Integer, primary_key=True)
    channel = Column(String, nullable=False)
    trigger = Column(String, nullable=False)
    komen = Column(String, nullable=False)

    def __init__(self, channel, trigger, komen):
        self.channel = channel
        self.trigger = trigger
        self.komen = komen

BASE.metadata.create_all(bind=SESSION.get_bind())

def add_komen(channel, trigger, komen):
    entry = AutoKomen(channel, trigger, komen)
    SESSION.add(entry)
    SESSION.commit()

def get_all():
    return SESSION.query(AutoKomen).all()

def delete_channel(channel):
    SESSION.query(AutoKomen).filter_by(channel=channel).delete()
    SESSION.commit()

def delete_trigger(trigger):
    SESSION.query(AutoKomen).filter_by(trigger=trigger).delete()
    SESSION.commit()

def delete_komen_text(komen):
    SESSION.query(AutoKomen).filter_by(komen=komen).delete()
    SESSION.commit()
