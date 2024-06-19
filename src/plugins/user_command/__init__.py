from nonebot import on_command
from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11 import GroupMessageEvent, PrivateMessageEvent
from nonebot.log import logger

__plugin_meta__ = PluginMetadata(
    name="User Command Plugin",
    description="用户命令插件",
    usage=f"直接发送命令即可触发",
)

vision = on_command("{bot_name}这是个什么", aliases={"{bot_name}", "这是个什么"}, priority=10, block=True)


@vision.handle()
async def _(event: GroupMessageEvent | PrivateMessageEvent):
    if not event.reply:
        return

    if event.group_id:
        logger.debug(f"接收到群聊 {event.group_id} 成员: {event.user_id} 的vision请求命令")
    else:
        logger.debug(f"接收到 {event.user_id} 的vision请求命令")
