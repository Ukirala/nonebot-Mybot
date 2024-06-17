import nonebot
from nonebot import on_message, on_command, on_notice
from nonebot.adapters.onebot.v11 import Bot, Message, MessageSegment, GroupMessageEvent, PrivateMessageEvent, NoticeEvent
from nonebot.plugin import PluginMetadata
from nonebot.params import CommandArg
from loguru import logger
from dotenv import load_dotenv
import os
import asyncio
import aiohttp
from nonebot.exception import FinishedException
from .config import config
from .image_to_text import image_to_text, clear_image_cache
from .utils import build_openai_request
from .database import Database
from .message_queue import MessageQueue

__plugin_meta__ = PluginMetadata(
    name="ChatGPT Plugin",
    description="通过HTTP请求调用OpenAI API的对话插件",
    usage=f"使用方法：\n 1. {config.oachat_on_command} <对话内容>",
)

# 为每个群创建一个异步锁和缓存
group_locks = {}
group_cache = {}

# 创建数据库实例
db = Database()

# 创建消息队列
group_queues = {}

@nonebot.get_driver().on_startup
async def startup():
    await db.init_db()
    for group_id in group_queues.keys():
        queue = MessageQueue(group_id, db, config.oachat_queue_size)
        await queue.load_history()
        group_queues[group_id] = queue
    asyncio.create_task(clear_image_cache())

# 定义一个消息处理器
message_handler = on_message(priority=5)

@message_handler.handle()
async def handle_group_message(bot: Bot, event: GroupMessageEvent):
    """
    处理群聊消息，将消息内容加入消息队列，处理图片消息并转为文字。
    """
    group_id = event.group_id

    # 获取或创建群组的消息历史记录对象
    if group_id not in group_queues:
        group_queues[group_id] = MessageQueue(group_id, db, config.oachat_queue_size)
        await group_queues[group_id].load_history()

    queue = group_queues[group_id]
    
    if group_id not in group_locks:
        group_locks[group_id] = asyncio.Lock()
        group_cache[group_id] = []

    lock = group_locks.get(group_id)
    
    if lock is None:
        logger.error(f"Group lock not found for group_id: {group_id}")
        return

    msg = event.get_message()

    # 处理图片消息
    for seg in msg:
        if seg.type == "image":
            image_url = seg.data.get("url")
            if image_url:
                await lock.acquire()
                try:
                    text = await image_to_text(image_url)
                    new_msg = {
                        "time": event.time,
                        "user_id": event.user_id,
                        "username": event.sender.nickname,
                        "message": f"[image: {text}]"
                    }
                    await queue.add_message(new_msg)
                    logger.info(f"图片消息已转文字并加入队列：{new_msg}")
                finally:
                    lock.release()
                return

    # 处理文字消息
    async with lock:
        for seg in msg:
            if seg.type == "text":
                text = seg.data.get("text")
                new_msg = {
                    "time": event.time,
                    "user_id": event.user_id,
                    "username": event.sender.nickname,
                    "message": text
                }
                await queue.add_message(new_msg)
                logger.info(f"文字消息已加入队列：{new_msg}")

# 定义命令
oachat = on_command(config.oachat_on_command, aliases={"/oachat"}, block=True, priority=5)
oachat_help = on_command("/oachat_help", aliases={"/对话帮助"}, block=True, priority=5)

@oachat_help.handle()
async def show_help():
    """显示插件帮助信息。"""
    await oachat_help.finish(__plugin_meta__.usage)

@oachat.handle()
async def handle_chat(bot: Bot, event: GroupMessageEvent | PrivateMessageEvent, msg: Message = CommandArg()):
    """处理 AI 对话命令，调用 OpenAI API 获取回复。"""
    logger.debug("handle_chat triggered")
    original_msg = msg.extract_plain_text().strip()

    group_id = event.group_id if isinstance(event, GroupMessageEvent) else f"private_{event.user_id}"
    if group_id not in group_queues:
        group_queues[group_id] = MessageQueue(group_id, db, config.oachat_queue_size)
        await group_queues[group_id].load_history()

    queue = group_queues[group_id]

    if group_id not in group_locks:
        group_locks[group_id] = asyncio.Lock()
        group_cache[group_id] = []

    lock = group_locks[group_id]
    cache = group_cache[group_id]

    async with lock:
        # 获取历史消息作为上下文
        history_messages = queue.get_messages()
        formatted_history = "\n".join(
            [f"{msg['username']}({msg['user_id']}) [{msg['time']}]: {msg['message']}" for msg in history_messages]
        )

        if not original_msg:
            current_input = config.oachat_on_command
        else:
            current_input = f"{config.oachat_on_command} {original_msg}"

        user_info = {
            "user_id": event.user_id,
            "nickname": event.sender.nickname
        }

        context = (
            "以下是当前群聊的总历史对话记录，其中也包含你说过的话，请仔细侦辨每个人的身份：\n\n"
            f"{formatted_history}\n"
            f"当前对话的用户是{user_info['nickname']}，QQ号{user_info['user_id']}，发送消息：\n{current_input}\n"
            "请根据以上对话内容回复："
        )

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config.openai_api_key}"
        }
        data = build_openai_request(context, config.openai_max_tokens)

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(config.api_url, headers=headers, json=data) as response:
                    result = await response.json()
                    if response.status == 200:
                        reply = result["choices"][0]["message"]["content"].strip()
                        await oachat.finish(MessageSegment.text(reply))
                    else:
                        await oachat.finish(f"请求失败: {result.get('error', {}).get('message', '未知错误')}")
            except aiohttp.ClientError as e:
                logger.error(f"HTTP请求出错: {str(e)}")
                await oachat.finish(f"请求出错: {str(e)}")
            except asyncio.TimeoutError:
                logger.error("请求超时")
                await oachat.finish("请求超时，请稍后再试")
            except FinishedException:
                pass
            except Exception as e:
                logger.error(f"未知异常: {str(e)}")
                await oachat.finish(f"发生未知错误: {str(e)}")
    
    while cache:
        msg = cache.pop(0)
        await handle_group_message(bot, msg)

@nonebot.get_driver().on_startup
async def startup():
    """
    启动时清理图片缓存任务。
    """
    asyncio.create_task(clear_image_cache())

