import asyncpg
import os

DATABASE_URL = os.environ.get("DATABASE_URL")

async def ensure_tables():
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS spam_list (
            name TEXT PRIMARY KEY
        );
    """)
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS spam_groups (
            id SERIAL PRIMARY KEY,
            list_name TEXT NOT NULL,
            group_username TEXT NOT NULL,
            FOREIGN KEY (list_name) REFERENCES spam_list(name) ON DELETE CASCADE
        );
    """)
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS user_timezone (
            user_id TEXT PRIMARY KEY,
            timezone TEXT NOT NULL
        );
    """)
    await conn.close()


async def add_group_to_list(namalist: str, group: str):
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute("INSERT INTO spam_list(name) VALUES($1) ON CONFLICT DO NOTHING", namalist)
    await conn.execute("""
        INSERT INTO spam_groups(list_name, group_username)
        VALUES ($1, $2)
        ON CONFLICT DO NOTHING
    """, namalist, group)
    await conn.close()

async def remove_group_from_list(namalist: str, group: str):
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute("DELETE FROM spam_groups WHERE list_name=$1 AND group_username=$2", namalist, group)
    count = await conn.fetchval("SELECT COUNT(*) FROM spam_groups WHERE list_name=$1", namalist)
    if count == 0:
        await conn.execute("DELETE FROM spam_list WHERE name=$1", namalist)
    await conn.close()

async def get_groups_by_list(namalist: str):
    conn = await asyncpg.connect(DATABASE_URL)
    rows = await conn.fetch("SELECT group_username FROM spam_groups WHERE list_name=$1", namalist)
    await conn.close()
    return [r['group_username'] for r in rows]

async def get_all_lists():
    conn = await asyncpg.connect(DATABASE_URL)
    rows = await conn.fetch("SELECT name FROM spam_list")
    await conn.close()
    return [type("ListObj", (object,), {"name": r["name"]})() for r in rows]

async def remove_list(namalist: str):
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute("DELETE FROM spam_groups WHERE list_name=$1", namalist)
    await conn.execute("DELETE FROM spam_list WHERE name=$1", namalist)
    await conn.close()

async def set_user_timezone(user_id: str, timezone: str):
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute("""
        INSERT INTO user_timezone(user_id, timezone)
        VALUES($1, $2)
        ON CONFLICT(user_id) DO UPDATE SET timezone=excluded.timezone
    """, user_id, timezone)
    await conn.close()

async def get_user_timezone(user_id: str):
    conn = await asyncpg.connect(DATABASE_URL)
    row = await conn.fetchrow("SELECT timezone FROM user_timezone WHERE user_id=$1", user_id)
    await conn.close()
    return row["timezone"] if row else None
