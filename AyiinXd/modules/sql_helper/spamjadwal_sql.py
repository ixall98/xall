try:
    from AyiinXd.modules.sql_helper import BASE, SESSION
except ImportError:
    raise AttributeError("Gagal import SQL Helper")

from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from threading import Lock

# Ganti URL sesuai konfigurasi database lo
DATABASE_URL = 'sqlite:///spamjadwal.db'  # atau PostgreSQL URL dari Heroku

Base = declarative_base()
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
SPAMJADWAL_LOCK = Lock()

class SpamJadwal(Base):
    __tablename__ = 'spamjadwal'
    nama = Column(String, primary_key=True)
    grup = Column(String, primary_key=True)

Base.metadata.create_all(engine)

def add_group_to_list(nama, grup):
    with SPAMJADWAL_LOCK:
        session = Session()
        entry = session.query(SpamJadwal).filter_by(nama=nama, grup=grup).first()
        if not entry:
            session.add(SpamJadwal(nama=nama, grup=grup))
            session.commit()
        session.close()

def remove_group_from_list(nama, grup):
    with SPAMJADWAL_LOCK:
        session = Session()
        entry = session.query(SpamJadwal).filter_by(nama=nama, grup=grup).first()
        if entry:
            session.delete(entry)
            session.commit()
        session.close()

def get_groups_by_list(nama):
    with SPAMJADWAL_LOCK:
        session = Session()
        result = session.query(SpamJadwal).filter_by(nama=nama).all()
        session.close()
        return result

def delete_list(nama):
    with SPAMJADWAL_LOCK:
        session = Session()
        session.query(SpamJadwal).filter_by(nama=nama).delete()
        session.commit()
        session.close()

def list_all_lists():
    with SPAMJADWAL_LOCK:
        session = Session()
        result = session.query(SpamJadwal.nama).distinct().all()
        session.close()
        return [r[0] for r in result]

def get_all_lists_with_groups():
    with SPAMJADWAL_LOCK:
        session = Session()
        all_entries = session.query(SpamJadwal).all()
        session.close()
        lists = {}
        for entry in all_entries:
            if entry.nama not in lists:
                lists[entry.nama] = []
            lists[entry.nama].append(entry.grup)
        return lists
