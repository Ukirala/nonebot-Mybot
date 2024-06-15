import re
import datetime
from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot.log import logger

# 屏蔽列表，记录用户ID和屏蔽结束时间
blocked_users = {}

def add_block(user_id: int, duration: int):
    """添加屏蔽用户"""
    end_time = datetime.datetime.now() + datetime.timedelta(seconds=duration)
    blocked_users[user_id] = end_time
    logger.info(f"User {user_id} blocked until {end_time}")

def remove_block(user_id: int):
    """移除屏蔽用户"""
    if user_id in blocked_users:
        del blocked_users[user_id]
        logger.info(f"User {user_id} unblocked")

def is_blocked(user_id: int) -> bool:
    """检查用户是否在屏蔽列表中"""
    if user_id in blocked_users:
        if datetime.datetime.now() < blocked_users[user_id]:
            return True
        else:
            # 如果屏蔽时间已经过了，移除屏蔽
            remove_block(user_id)
    return False

async def handle_block_commands(event: MessageEvent):
    """处理屏蔽指令"""
    msg = event.get_plaintext().strip()
    logger.debug(f"Checking block commands in message: {msg}")

    block_pattern = re.compile(r'屏蔽@(\d+)\s(\d+)秒')
    unblock_pattern = re.compile(r'解除屏蔽@(\d+)')

    block_match = block_pattern.match(msg)
    unblock_match = unblock_pattern.match(msg)

    if block_match:
        user_id = int(block_match.group(1))
        duration = int(block_match.group(2))
        add_block(user_id, duration)
    elif unblock_match:
        user_id = int(unblock_match.group(1))
        remove_block(user_id)

