from sqlalchemy import Column, String, Integer, PickleType
from AyiinXd.modules.sql_helper import BASE, SESSION

class FilterChannel(BASE):
    __tablename__ = "filter_channel"
    channel = Column(String, primary_key=True)
    filters = Column(PickleType, default=list)

class LogGroup(BASE):
    __tablename__ = "log_group"
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer)

FilterChannel.__table__.create(checkfirst=True)
LogGroup.__table__.create(checkfirst=True)

# ➕ Tambah channel ke filter
def add_channel(channel):
    if not get_channel(channel):
        SESSION.add(FilterChannel(channel=channel, filters=[]))
        SESSION.commit()

# ❌ Hapus channel dari filter
def delete_channel(channel):
    row = get_channel(channel)
    if row:
        SESSION.delete(row)
        SESSION.commit()

# 🔍 Ambil data channel tertentu
def get_channel(channel):
    return SESSION.query(FilterChannel).filter_by(channel=channel).first()

# 📋 Ambil semua channel
def get_all():
    return SESSION.query(FilterChannel).all()

# ➕ Tambah kata filter ke channel
def add_filter(channel, word):
    row = get_channel(channel)
    if row:
        filters = row.filters if row.filters else []
        if word not in filters:
            filters.append(word)
            row.filters = filters
            SESSION.commit()

# 🧹 Hapus kata filter dari channel
def remove_filter(channel, word):
    row = get_channel(channel)
    if row:
        filters = row.filters if row.filters else []
        if word in filters:
            filters.remove(word)
            row.filters = filters
            SESSION.commit()

# 📌 Set channel terakhir yang diedit
def set_last(channel):
    SESSION.query(LogGroup).filter_by(id=999).delete()
    SESSION.add(LogGroup(id=999, chat_id=channel))
    SESSION.commit()

def get_last():
    row = SESSION.query(LogGroup).filter_by(id=999).first()
    return row.chat_id if row else None

# 📝 Set grup log buat kirim alert
def set_log_group(chat_id):
    SESSION.query(LogGroup).filter_by(id=1).delete()
    SESSION.add(LogGroup(id=1, chat_id=chat_id))
    SESSION.commit()

def get_log_group():
    row = SESSION.query(LogGroup).filter_by(id=1).first()
    return row.chat_id if row else None
