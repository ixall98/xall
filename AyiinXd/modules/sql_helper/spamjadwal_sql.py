try:
    from AyiinXd.modules.sql_helper import BASE, SESSION
except ImportError:
    raise AttributeError("Gagal import SQL Helper")

from sqlalchemy import Table, Column, String, ForeignKey, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import create_engine
from threading import Lock

# Zona waktu user
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

# Spam jadwal list (dilengkapin)
class JadwalSpamList(BASE):
    __tablename__ = "jadwal_spam_list"
    name = Column(String, primary_key=True)
    type = Column(String)  # "biasa" atau "fw"
    content = Column(String)
    delay = Column(Integer)
    groups = relationship("JadwalSpamGroup", cascade="all, delete", backref="list")

class JadwalSpamGroup(BASE):
    __tablename__ = "jadwal_spam_group"
    id = Column(String, primary_key=True)
    list_name = Column(String, ForeignKey("jadwal_spam_list.name"))
    group_username = Column(String)

# CRUD untuk spam jadwal
def add_jadwal_list(name, type, content, delay):
    data = SESSION.query(JadwalSpamList).filter_by(name=name).first()
    if data:
        data.type = type
        data.content = content
        data.delay = delay
    else:
        data = JadwalSpamList(name=name, type=type, content=content, delay=delay)
        SESSION.add(data)
    SESSION.commit()

def get_jadwal_list(name):
    return SESSION.query(JadwalSpamList).filter_by(name=name).first()

def get_all_jadwal_lists():
    return SESSION.query(JadwalSpamList).all()

def remove_jadwal_list(name):
    SESSION.query(JadwalSpamList).filter_by(name=name).delete()
    SESSION.query(JadwalSpamGroup).filter_by(list_name=name).delete()
    SESSION.commit()

def add_groups_to_jadwal(name, groups):
    for g in groups:
        if not SESSION.query(JadwalSpamGroup).filter_by(list_name=name, group_username=g).first():
            SESSION.add(JadwalSpamGroup(id=f"{name}_{g}", list_name=name, group_username=g))
    SESSION.commit()

def get_groups_by_jadwal(name):
    return [g.group_username for g in SESSION.query(JadwalSpamGroup).filter_by(list_name=name).all()]

def remove_group_from_jadwal(name, group):
    SESSION.query(JadwalSpamGroup).filter_by(list_name=name, group_username=group).delete()
    SESSION.commit()
