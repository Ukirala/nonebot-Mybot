import aiohttp
import nonebot
from nonebot import on_command
from nonebot.plugin import PluginMetadata
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Bot, Message, MessageSegment, GroupMessageEvent, PrivateMessageEvent
from nonebot.exception import FinishedException
from nonebot.log import logger

# 从 history.py 中导入函数
from .history import get_history_messages, format_history_messages

# 读取配置
config = nonebot.get_driver().config
api_key = config.openai_api_key
proxy_api_url = config.proxy_api_url
max_tokens = config.openai_max_tokens
oachat_on_command = config.oachat_on_command
history_count = int(getattr(config, 'oachat_history_count', 20))

# 插件元数据
__plugin_meta__ = PluginMetadata(
    name="ChatGPT Plugin",
    description="通过HTTP请求调用OpenAI API的对话插件",
    usage=f"使用方法：\n 1. {oachat_on_command} <对话内容>",
)

# 定义命令
oachat = on_command(oachat_on_command, aliases={"/oachat"}, block=True, priority=5)
oachat_help = on_command("/oachat_help", aliases={"/对话帮助"}, block=True, priority=5)

@oachat_help.handle()
async def show_help():
    await oachat_help.finish(__plugin_meta__.usage)

@oachat.handle()
async def handle_chat(bot: Bot, event: GroupMessageEvent | PrivateMessageEvent, msg: Message = CommandArg()):
    logger.debug("handle_chat triggered")
    original_msg = msg.extract_plain_text().strip()
    
    # 获取历史消息
    history_messages = await get_history_messages(bot, event, history_count)

    # 格式化历史消息
    formatted_history = format_history_messages(history_messages)

    # 如果 original_msg 为空，则使用触发词作为内容
    if not original_msg:
        current_input = oachat_on_command
    else:
        current_input = f"{oachat_on_command} {original_msg}"

    # 获取触发对话的用户信息
    user_info = {
        "user_id": event.user_id,
        "nickname": event.sender.nickname
    }

    # 构建上下文
    context = (
        "以下是当前群聊的总历史对话记录，其中也包含你说过的话，请仔细侦辨每个人的身份：\n\n"
        f"{formatted_history}\n"
        f"当前对话的用户是{user_info['nickname']}，QQ号{user_info['user_id']}，发送消息：\n{current_input}\n"
        "请穗穗根据以上对话内容回复："
    )

    # 生成 HTTP 请求体
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "model": "model name",
        "messages": [{"role": "user", "content": context}],
        "max_tokens": max_tokens,
        "temperature": 0.7
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(proxy_api_url, headers=headers, json=data) as response:
                result = await response.json()
                if response.status == 200:
                    reply = result["choices"][0]["message"]["content"].strip()
                    await oachat.finish(MessageSegment.text(reply))
                else:
                    await oachat.finish(f"请求失败: {result.get('error', {}).get('message', '未知错误')}")
        except FinishedException:
            pass  # 忽略 FinishedException 异常
        except Exception as e:
            await oachat.finish(f"请求出错: {str(e)}")

