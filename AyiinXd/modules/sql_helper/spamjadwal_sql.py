import sqlite3

conn = sqlite3.connect("spamjadwal.db")
cursor = conn.cursor()

# Buat tabel list spam dan grup
cursor.execute("""
CREATE TABLE IF NOT EXISTS spam_list (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS spam_groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    list_name TEXT NOT NULL,
    group_username TEXT NOT NULL,
    FOREIGN KEY(list_name) REFERENCES spam_list(name)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS user_timezone (
    user_id TEXT PRIMARY KEY,
    timezone TEXT NOT NULL
)
""")

conn.commit()


def add_group_to_list(namalist: str, group: str):
    cursor.execute("INSERT OR IGNORE INTO spam_list (name) VALUES (?)", (namalist,))
    cursor.execute(
        "INSERT OR IGNORE INTO spam_groups (list_name, group_username) VALUES (?, ?)",
        (namalist, group),
    )
    conn.commit()


def remove_group_from_list(namalist: str, group: str):
    cursor.execute(
        "DELETE FROM spam_groups WHERE list_name = ? AND group_username = ?",
        (namalist, group),
    )
    # Jika list kosong, hapus juga list
    cursor.execute(
        "SELECT COUNT(*) FROM spam_groups WHERE list_name = ?", (namalist,)
    )
    count = cursor.fetchone()[0]
    if count == 0:
        cursor.execute("DELETE FROM spam_list WHERE name = ?", (namalist,))
    conn.commit()


def get_groups_by_list(namalist: str):
    cursor.execute(
        "SELECT group_username FROM spam_groups WHERE list_name = ?", (namalist,)
    )
    rows = cursor.fetchall()
    return [r[0] for r in rows] if rows else []


def get_all_lists():
    cursor.execute("SELECT name FROM spam_list")
    rows = cursor.fetchall()
    # Return list of objects with attribute .name
    return [type("ListObj", (object,), {"name": r[0]})() for r in rows]


def remove_list(namalist: str):
    cursor.execute("DELETE FROM spam_groups WHERE list_name = ?", (namalist,))
    cursor.execute("DELETE FROM spam_list WHERE name = ?", (namalist,))
    conn.commit()


def set_user_timezone(user_id: str, timezone: str):
    cursor.execute(
        "INSERT INTO user_timezone(user_id, timezone) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET timezone=excluded.timezone",
        (user_id, timezone),
    )
    conn.commit()


def get_user_timezone(user_id: str):
    cursor.execute("SELECT timezone FROM user_timezone WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    return row[0] if row else None
