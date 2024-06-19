from nonebot import on_command
from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11 import GroupMessageEvent, PrivateMessageEvent
from nonebot.log import logger

__plugin_meta__ = PluginMetadata(
    name="Admin Command Plugin",
    description="管理员命令插件",
    usage=f"直接发送命令即可触发",
)

vision = on_command("{bot_name}", aliases={"拉黑", "black"}, priority=10, block=True)


@vision.handle()
async def _(event: GroupMessageEvent | PrivateMessageEvent):
    logger.debug("成员: {event.user_id} 触发了拉黑命令")
    if event.user_id == 110:
        await vision.finish("您不是管理员无法使用改命令!")
