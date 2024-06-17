from nonebot.adapters.onebot.v11 import Bot, Message, MessageSegment, GroupMessageEvent, PrivateMessageEvent, NoticeEvent
from loguru import logger
from .database import Database
from .config import config # 导入 config
import asyncio

class MessageQueue:
    def __init__(self, group_id: int, db: Database, max_size: int = config.oachat_queue_size):
        self.group_id = group_id
        self.db = db
        self.max_size = max_size
        self.buffer = []
        self.lock = asyncio.Lock()

    async def load_history(self):
        messages = await self.db.get_messages(self.group_id, self.max_size)
        self.buffer.extend(
            {
                "id": msg[0],
                "group_id": msg[1],
                "user_id": msg[2],
                "username": msg[3],
                "message": msg[4],
                "time": msg[5],
            }
            for msg in messages
        )
        logger.info(f"Loaded {len(messages)} messages for group {self.group_id}")

    async def add_message(self, message: dict):
        async with self.lock:
            await self.db.add_message(
                self.group_id,
                message["user_id"],
                message["username"],
                message["message"]
            )
            self.buffer.append(message)
            if len(self.buffer) > self.max_size:
                self.buffer.pop(0)
            logger.debug(f"Message added to queue: {message}")

    def get_messages(self):
        return self.buffer
