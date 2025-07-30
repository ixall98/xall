from sqlalchemy import Column, Integer, String
from AyiinXd.modules.sql_helper import BASE, SESSION

class AutoReact(BASE):
    __tablename__ = "auto_react"
    id = Column(Integer, primary_key=True)
    chat_id = Column(String, nullable=False)
    emoji = Column(String, nullable=False)
    jumlah = Column(Integer, nullable=False)

def add_react(chat_id: str, emoji: str, jumlah: int):
    data = SESSION.query(AutoReact).filter_by(chat_id=chat_id, emoji=emoji).first()
    if data:
        data.jumlah = jumlah
    else:
        data = AutoReact(chat_id=chat_id, emoji=emoji, jumlah=jumlah)
        SESSION.add(data)
    SESSION.commit()

def remove_react(chat_id: str, emoji: str = None):
    query = SESSION.query(AutoReact).filter_by(chat_id=chat_id)
    if emoji:
        query = query.filter_by(emoji=emoji)
    query.delete(synchronize_session=False)
    SESSION.commit()

def get_all_reacts():
    return SESSION.query(AutoReact).all()

def get_reacts_by_chat(chat_id: str):
    return SESSION.query(AutoReact).filter_by(chat_id=chat_id).all()
