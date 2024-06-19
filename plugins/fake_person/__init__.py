from nonebot import on_message
from nonebot.adapters.onebot.v11 import GroupMessageEvent, PrivateMessageEvent
from nonebot.log import logger
from nonebot.plugin import PluginMetadata

# from .history import get_history_messages, format_history_messages


__plugin_meta__ = PluginMetadata(
    name="Fake_Person Plugin",
    description="伪人插件",
    usage=f"随机触发",
)

fake_person = on_message(priority=15)


@fake_person.handle()
async def _(event: GroupMessageEvent | PrivateMessageEvent):
    if event.group_id:
        logger.debug(f"接收到群聊 {event.group_id} 成员: {event.user_id} 的消息")
    else:
        logger.debug(f"接收到 {event.user_id} 的消息")
    logger.success("Fake_Person Plugin: show_help")
