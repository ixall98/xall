try:
    from AyiinXd.modules.sql_helper import BASE, SESSION
except ImportError:
    raise AttributeError("Gagal import SQL Helper")

from sqlalchemy import Column, String

class SpamJadwal(BASE):
    __tablename__ = "spam_jadwal"
    namalist = Column(String, primary_key=True)
    grup = Column(String, primary_key=True)

    def __init__(self, namalist, grup):
        self.namalist = namalist
        self.grup = grup

BASE.metadata.create_all(bind=SESSION.get_bind())

def add_grup(namalist, grup):
    exists = SESSION.query(SpamJadwal).filter_by(namalist=namalist, grup=grup).first()
    if not exists:
        row = SpamJadwal(namalist, grup)
        SESSION.add(row)
        SESSION.commit()

def remove_grup(namalist, grup):
    row = SESSION.query(SpamJadwal).filter_by(namalist=namalist, grup=grup).first()
    if row:
        SESSION.delete(row)
        SESSION.commit()

def get_grup_by_list(namalist):
    return SESSION.query(SpamJadwal).filter_by(namalist=namalist).all()

def get_all_lists():
    return SESSION.query(SpamJadwal).all()

def delete_list(namalist):
    SESSION.query(SpamJadwal).filter_by(namalist=namalist).delete()
    SESSION.commit()
