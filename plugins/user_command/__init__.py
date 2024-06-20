import json

from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, PrivateMessageEvent
from nonebot.log import logger
from nonebot.plugin import PluginMetadata

from utils.api.vision.GeminiFlash import (download_image, process_image,
                                          send_request)

__plugin_meta__ = PluginMetadata(
    name="User Command Plugin",
    description="用户命令插件",
    usage=f"直接发送命令即可触发",
)

vision = on_command("真寻酱这是什么", aliases={"{bot_name}", "+"}, priority=10, block=False)


@vision.handle()
async def _(event: GroupMessageEvent | PrivateMessageEvent):
    if not event.reply:
        return

    match event:
        case GroupMessageEvent():
            logger.info(f"接收到群聊 {event.group_id} 成员: {event.user_id} 的vision请求命令")
        case PrivateMessageEvent():
            logger.info(f"接收到 {event.user_id} 的vision请求命令")
        case _:
            return

    url = event.reply.message[0].data.get('url', "")
    if url == "":
        await vision.finish("没有找到图片, 可能是引用回复没图片")

    img_path = await download_image(url)
    encoded_image = await process_image(img_path)
    response_text = await send_request(encoded_image)

    await vision.finish(response_text['candidates'][0]['content']['parts'][0]['text'])
