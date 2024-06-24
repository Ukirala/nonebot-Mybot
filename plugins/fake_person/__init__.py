import random

from nonebot import on_message
from nonebot.adapters.onebot.v11 import GroupMessageEvent, PrivateMessageEvent
from nonebot.log import logger
from nonebot.plugin import PluginMetadata

from utils.api.OpenAI import call_openai_api
from utils.SentencesSpliter import SentencesSpliter

__plugin_meta__ = PluginMetadata(
    name="Fake_Person Plugin",
    description="伪人插件",
    usage=f"随机触发",
)

fake_person = on_message(priority=15)


@fake_person.handle()
async def _(event: GroupMessageEvent | PrivateMessageEvent):
    match event:
        case GroupMessageEvent():
            logger.info(f"接收到群聊 {event.group_id} 成员: {event.user_id} 的消息")
        case PrivateMessageEvent():
            logger.info(f"接收到 {event.user_id} 的消息")
        case _:
            return

    rand = random.random()
    logger.info(f"随机数: {rand}")

    if rand <= 0.2:
        logger.success("触发伪人")
        res = await call_openai_api(event.get_plaintext())
        text = SentencesSpliter.split_text(res)

        for _ in text:
            if _.strip() == "":
                continue
            await fake_person.send(_)
