import asyncpg
from typing import Optional, List, Tuple

class SFSDatabase:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def set_admin_channel(self, admin_id: int, channel: str):
        await self.pool.execute("""
            INSERT INTO sfs_config (admin_id, admin_channel)
            VALUES ($1, $2)
            ON CONFLICT (admin_id)
            DO UPDATE SET admin_channel = EXCLUDED.admin_channel;
        """, admin_id, channel)

    async def get_admin_channel(self, admin_id: int) -> Optional[str]:
        rec = await self.pool.fetchrow("SELECT admin_channel FROM sfs_config WHERE admin_id = $1;", admin_id)
        return rec["admin_channel"] if rec else None

    async def clear_admin_channel(self, admin_id: int):
        await self.pool.execute("DELETE FROM sfs_config WHERE admin_id = $1;", admin_id)

    async def upsert_user(self, user_id: int, username: str, admin_channel: str):
        await self.pool.execute("""
            INSERT INTO sfs_data (user_id, username, status, admin_channel)
            VALUES ($1, $2, 'waiting', $3)
            ON CONFLICT (user_id)
            DO UPDATE SET username = EXCLUDED.username, admin_channel = EXCLUDED.admin_channel;
        """, user_id, username, admin_channel)

    async def mark_joined(self, user_id: int):
        await self.pool.execute("UPDATE sfs_data SET status = 'joined' WHERE user_id = $1;", user_id)

    async def save_user_channel(self, user_id: int, channel: str):
        await self.pool.execute(
            "UPDATE sfs_data SET user_channel = $2, status = 'done' WHERE user_id = $1;",
            user_id, channel
        )

    async def get_status(self, user_id: int) -> Optional[str]:
        rec = await self.pool.fetchrow("SELECT status FROM sfs_data WHERE user_id = $1;", user_id)
        return rec["status"] if rec else None

    async def get_user_channel(self, user_id: int) -> Optional[str]:
        rec = await self.pool.fetchrow("SELECT user_channel FROM sfs_data WHERE user_id = $1;", user_id)
        return rec["user_channel"] if rec else None

    async def get_all_done_users(self) -> List[Tuple[int, str]]:
        return await self.pool.fetch("SELECT user_id, COALESCE(username, '') AS username FROM sfs_data WHERE status = 'done';")
