from sqlalchemy import Column, String, Integer, PickleType
from AyiinXd.modules.sql_helper import BASE, SESSION

# Model table
class FilterChannel(BASE):
    __tablename__ = "filter_channel"
    id = Column(Integer, primary_key=True)  # auto increment
    channel_id = Column(Integer, unique=True)  # integer ID channel
    username = Column(String)  # username channel (optional)
    title = Column(String)     # judul channel
    filters = Column(PickleType)  # daftar kata filter

class LogGroup(BASE):
    __tablename__ = "log_group"
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer)

BASE.metadata.create_all(SESSION.bind)

# Add channel ke DB
def add_channel(channel_id, username=None, title=None):
    existing = SESSION.query(FilterChannel).filter_by(channel_id=channel_id).first()
    if not existing:
        new = FilterChannel(channel_id=channel_id, username=username, title=title, filters=[])
        SESSION.add(new)
        SESSION.commit()

def delete_channel(channel_id):
    row = SESSION.query(FilterChannel).filter_by(channel_id=channel_id).first()
    if row:
        SESSION.delete(row)
        SESSION.commit()

def get_channel(channel_id):
    return SESSION.query(FilterChannel).filter_by(channel_id=channel_id).first()

def get_all():
    return SESSION.query(FilterChannel).all()

def add_filter(channel_id, word):
    row = get_channel(channel_id)
    if row:
        if row.filters is None:
            row.filters = []
        if word not in row.filters:
            row.filters.append(word)
            SESSION.commit()

def remove_filter(channel_id, word):
    row = get_channel(channel_id)
    if row and row.filters and word in row.filters:
        row.filters.remove(word)
        SESSION.commit()

# Last used channel (biar bisa dipakai .addfilter/delfilter tanpa harus sebutin channel)
_last_channel = {}

def set_last(channel_id):
    _last_channel["last"] = channel_id

def get_last():
    return _last_channel.get("last")

# Set/Get grup log
def set_log_group(chat_id):
    SESSION.query(LogGroup).delete()  # cuma 1 log group
    SESSION.add(LogGroup(id=999, chat_id=chat_id))
    SESSION.commit()

def get_log_group():
    row = SESSION.query(LogGroup).first()
    return row.chat_id if row else None
