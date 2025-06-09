from sqlalchemy import Column, String, BigInteger, PickleType
from AyiinXd.modules.sql_helper import BASE, SESSION

class FilterChannel(BASE):
    __tablename__ = "filter_channel"
    id = Column(BigInteger, primary_key=True)
    channel_id = Column(BigInteger, unique=True)
    username = Column(String)
    title = Column(String)
    filters = Column(PickleType)

    def __init__(self, channel_id, username, title, filters=None):
        self.channel_id = channel_id
        self.username = username
        self.title = title
        self.filters = filters or []

class LogGroup(BASE):
    __tablename__ = "log_group"
    id = Column(BigInteger, primary_key=True, default=999)
    chat_id = Column(BigInteger)

BASE.metadata.create_all(SESSION.bind)

# Fungsi
def add_channel(username):
    from telethon.tl.functions.channels import GetFullChannelRequest
    from AyiinXd import bot
    import asyncio

    async def get_entity_info():
        entity = await bot.get_entity(username)
        return entity.id, entity.username, entity.title

    loop = asyncio.get_event_loop()
    channel_id, uname, title = loop.run_until_complete(get_entity_info())

    data = FilterChannel(channel_id=channel_id, username=uname, title=title)
    SESSION.add(data)
    SESSION.commit()

def delete_channel(username):
    data = SESSION.query(FilterChannel).filter_by(username=username).first()
    if data:
        SESSION.delete(data)
        SESSION.commit()

def get_channel(username):
    return SESSION.query(FilterChannel).filter_by(username=username).first()

def get_all():
    return SESSION.query(FilterChannel).all()

def add_filter(username, word):
    data = get_channel(username)
    if data:
        filters = data.filters or []
        if word not in filters:
            filters.append(word)
            data.filters = filters
            SESSION.commit()

def remove_filter(username, word):
    data = get_channel(username)
    if data and data.filters:
        filters = data.filters
        if word in filters:
            filters.remove(word)
            data.filters = filters
            SESSION.commit()

def set_last(username):
    with open("last_filter_channel.txt", "w") as f:
        f.write(username)

def get_last():
    try:
        with open("last_filter_channel.txt", "r") as f:
            return f.read().strip()
    except:
        return None

def set_log_group(chat_id):
    data = SESSION.query(LogGroup).first()
    if not data:
        data = LogGroup(chat_id=chat_id)
        SESSION.add(data)
    else:
        data.chat_id = chat_id
    SESSION.commit()

def get_log_group():
    data = SESSION.query(LogGroup).first()
    return data.chat_id if data else None
