from datetime import datetime
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, PrivateMessageEvent
from nonebot.adapters.onebot.v11.exception import ActionFailed

async def get_history_messages(bot: Bot, event: GroupMessageEvent | PrivateMessageEvent, count: int):
    history = []
    try:
        if isinstance(event, GroupMessageEvent):
            group_id = event.group_id
            response = await bot.call_api("get_group_msg_history", group_id=group_id)
        elif isinstance(event, PrivateMessageEvent):
            user_id = event.user_id
            response = await bot.call_api("get_friend_msg_history", user_id=user_id, count=count)
        else:
            return history

        messages = response.get('messages', [])
        for msg in messages:
            if len(history) >= count:
                break
            history.append({
                "time": datetime.fromtimestamp(msg["time"]),
                "user_id": msg["user_id"],
                "nickname": msg["sender"]["nickname"],
                "message": msg["message"]
            })
    except ActionFailed as e:
        # 打印异常信息以便调试
        print(f"ActionFailed: status={e.status}, retcode={e.retcode}, data={e.data}, echo={e.echo}")
        # 可以根据需要处理不同的retcode
        if e.retcode not in [100, 101]:  # 例如忽略特定的错误码
            raise e  # 如果是其他错误码，重新抛出异常以便进一步处理
    return history

def format_history_messages(messages):
    formatted = ""
    for msg in messages:
        formatted += f"[{msg['time']}][名字: {msg['nickname']}, QQ号: {msg['user_id']}]消息: \"{msg['message']}\"\n"
    return formatted

