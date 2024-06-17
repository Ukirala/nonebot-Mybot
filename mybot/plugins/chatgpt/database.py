import aiosqlite
import asyncio
import os

DB_PATH = "mybot/chatgpt/database/chat_history.db"  # 确保路径正确

class Database:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.lock = asyncio.Lock()
        self.ensure_db_path_exists()

    def ensure_db_path_exists(self):
        # 创建数据库目录
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    async def init_db(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    group_id INTEGER,
                    user_id INTEGER,
                    username TEXT,
                    message TEXT,
                    time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.commit()

    async def add_message(self, group_id: int, user_id: int, username: str, message: str):
        async with self.lock:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO messages (group_id, user_id, username, message)
                    VALUES (?, ?, ?, ?)
                """, (group_id, user_id, username, message))
                await db.commit()

    async def get_messages(self, group_id: int, limit: int):
        async with self.lock:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    SELECT * FROM messages
                    WHERE group_id = ?
                    ORDER BY time DESC
                    LIMIT ?
                """, (group_id, limit))
                rows = await cursor.fetchall()
                return rows[::-1]  # 按时间顺序返回消息

    async def delete_message(self, message_id: int):
        async with self.lock:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("DELETE FROM messages WHERE id = ?", (message_id,))
                await db.commit()

    async def update_message(self, message_id: int, new_message: str):
        async with self.lock:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("UPDATE messages SET message = ? WHERE id = ?", (new_message, message_id))
                await db.commit()

    async def browse_messages(self, group_id: int):
        async with self.lock:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("SELECT * FROM messages WHERE group_id = ?", (group_id,))
                rows = await cursor.fetchall()
                return rows

