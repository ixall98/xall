try:
    from AyiinXd.modules.sql_helper import BASE, SESSION
except ImportError:
    raise AttributeError("Gagal import SQL Helper")

from sqlalchemy import Table, Column, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import create_engine
from threading import Lock

class ZonaWaktu(BASE):
    __tablename__ = "zona_waktu"
    user_id = Column(String, primary_key=True)
    zona = Column(String)

def set_user_timezone(user_id, zona):
    old = SESSION.query(ZonaWaktu).get(str(user_id))
    if old:
        old.zona = zona
    else:
        new = ZonaWaktu(user_id=str(user_id), zona=zona)
        SESSION.add(new)
    SESSION.commit()

def get_user_timezone(user_id):
    result = SESSION.query(ZonaWaktu).get(str(user_id))
    return result.zona if result else "WIB"

# Table for spam lists
class SpamList(BASE):
    __tablename__ = "spam_list"
    name = Column(String, primary_key=True)
    groups = relationship("SpamGroup", cascade="all, delete", backref="list")

class SpamGroup(BASE):
    __tablename__ = "spam_group"
    id = Column(String, primary_key=True)
    list_name = Column(String, ForeignKey("spam_list.name"))
    group_username = Column(String)

def add_group_to_list(list_name, group_username):
    # Ensure list exists
    spam_list = SESSION.query(SpamList).get(list_name)
    if not spam_list:
        spam_list = SpamList(name=list_name)
        SESSION.add(spam_list)
    # Check if group exists in list
    exists = SESSION.query(SpamGroup).filter_by(list_name=list_name, group_username=group_username).first()
    if not exists:
        new_group = SpamGroup(id=f"{list_name}_{group_username}", list_name=list_name, group_username=group_username)
        SESSION.add(new_group)
    SESSION.commit()

def remove_group_from_list(list_name, group_username):
    group = SESSION.query(SpamGroup).filter_by(list_name=list_name, group_username=group_username).first()
    if group:
        SESSION.delete(group)
        SESSION.commit()

def get_groups_by_list(list_name):
    spam_list = SESSION.query(SpamList).get(list_name)
    if not spam_list:
        return []
    return [g.group_username for g in spam_list.groups]

def get_all_lists():
    return SESSION.query(SpamList).all()

def remove_list(list_name):
    spam_list = SESSION.query(SpamList).get(list_name)
    if spam_list:
        SESSION.delete(spam_list)
        SESSION.commit()
