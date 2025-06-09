from sqlalchemy import Column, String, Integer, BigInteger, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from AyiinXd.modules.sql_helper import BASE, SESSION

class AutoBanChannel(BASE):
    __tablename__ = "autoban_channels"
    channel_id = Column(BigInteger, primary_key=True)
    channel_username = Column(String, nullable=False)
    members = relationship("AutoBanMember", cascade="all, delete", backref="channel")

class AutoBanMember(BASE):
    __tablename__ = "autoban_members"
    id = Column(Integer, primary_key=True)
    channel_id = Column(BigInteger, ForeignKey("autoban_channels.channel_id"))
    username = Column(String)

    __table_args__ = (UniqueConstraint("channel_id", "username", name="user_per_channel"),)

class AutoBannedUser(BASE):
    __tablename__ = "autoban_banned"
    id = Column(Integer, primary_key=True)
    channel_username = Column(String)
    username = Column(String)

    __table_args__ = (UniqueConstraint("channel_username", "username", name="unique_banned"),)

def add_channel(channel_id, username):
    if not SESSION.query(AutoBanChannel).get(channel_id):
        ch = AutoBanChannel(channel_id=channel_id, channel_username=username)
        SESSION.add(ch)
        SESSION.commit()

def remove_channel(channel_id):
    ch = SESSION.query(AutoBanChannel).get(channel_id)
    if ch:
        SESSION.delete(ch)
        SESSION.commit()

def get_all_channels():
    return SESSION.query(AutoBanChannel).all()

def add_or_update_channel(channel_id, username, members):
    remove_channel(channel_id)
    ch = AutoBanChannel(channel_id=channel_id, channel_username=username)
    SESSION.add(ch)
    SESSION.flush()
    for m in members:
        ch.members.append(AutoBanMember(channel_id=channel_id, username=m))
    SESSION.commit()

def get_prev_members(channel_id):
    rows = SESSION.query(AutoBanMember).filter_by(channel_id=channel_id).all()
    return set(r.username for r in rows)

def add_banned_user(channel_username, username):
    exists = SESSION.query(AutoBannedUser).filter_by(channel_username=channel_username, username=username).first()
    if not exists:
        banned = AutoBannedUser(channel_username=channel_username, username=username)
        SESSION.add(banned)
        SESSION.commit()

def get_banned_users():
    rows = SESSION.query(AutoBannedUser).all()
    return [(r.channel_username, r.username) for r in rows]
