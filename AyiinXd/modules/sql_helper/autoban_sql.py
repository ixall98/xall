from sqlalchemy import Column, String, Boolean
from AyiinXd.modules.sql_helper import BASE, SESSION

class AutoBanChannel(BASE):
    __tablename__ = "autoban_channel"
    channel_id = Column(String, primary_key=True)
    channel_username = Column(String)
    enabled = Column(Boolean, default=True)

    def __init__(self, channel_id, channel_username):
        self.channel_id = channel_id
        self.channel_username = channel_username
        self.enabled = True

BASE.metadata.create_all()

def add_channel(channel_id, username):
    if not SESSION.get(AutoBanChannel, channel_id):
        ch = AutoBanChannel(channel_id, username)
        SESSION.add(ch)
        SESSION.commit()

def remove_channel(channel_id):
    ch = SESSION.get(AutoBanChannel, channel_id)
    if ch:
        SESSION.delete(ch)
        SESSION.commit()

def get_all_channels():
    return SESSION.query(AutoBanChannel).filter_by(enabled=True).all()
