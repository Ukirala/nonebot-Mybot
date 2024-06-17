from nonebot import on_command
from nonebot.plugin import PluginMetadata
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Bot, Message, MessageSegment, GroupMessageEvent, PrivateMessageEvent
from nonebot.log import logger

from .config import oachat_on_command, history_count
from .history import get_history_messages, format_history_messages
from .utils.openai import call_openai_api, send_split_messages

__plugin_meta__ = PluginMetadata(
    name="Fake_Person Plugin",
    description="伪人插件",
    usage=f"使用方法：\n 1. {oachat_on_command} <对话内容>",
)

oachat = on_command(oachat_on_command, aliases={"/oachat"}, block=True, priority=5)
oachat_help = on_command("/oachat_help", aliases={"/对话帮助"}, block=True, priority=5)


@oachat_help.handle()
async def show_help():
    await oachat_help.finish(__plugin_meta__.usage)


@oachat.handle()
async def handle_chat(bot: Bot, event: GroupMessageEvent | PrivateMessageEvent, msg: Message = CommandArg()):
    logger.debug("handle_chat triggered")
    original_msg = msg.extract_plain_text().strip()

    history_messages = await get_history_messages(bot, event, history_count)
    formatted_history = format_history_messages(history_messages)

    if not original_msg:
        current_input = oachat_on_command
    else:
        current_input = f"{oachat_on_command} {original_msg}"

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

    reply = await call_openai_api(context)

    # 这里调用send_split_messages方法，设置分隔符和延迟范围
    await send_split_messages(bot, event, reply, separator="(+)", min_delay=500, max_delay=5000)
