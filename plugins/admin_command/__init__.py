from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, PrivateMessageEvent, Message
from nonebot.log import logger
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
from core.ConfigProvider import Bot, ConfigProvider
from utils.bot.format_value import convert_value
__plugin_meta__ = PluginMetadata(
    name="Admin Command Plugin",
    description="管理员命令插件",
    usage=f"直接发送命令即可触发",
)

block = on_command("{bot_name}", aliases={"拉黑", "black"}, priority=10, block=True)
config = on_command("设置", aliases={"set", "config"}, priority=10, block=True)


@block.handle()
async def _(event: GroupMessageEvent | PrivateMessageEvent):
    logger.debug(f"用户: {event.user_id} 触发了拉黑命令")
    if event.user_id != Bot.AdminID:
        await block.finish("您不是管理员无法使用此命令!")


@config.handle()
async def _(event: GroupMessageEvent | PrivateMessageEvent, command_args: Message = CommandArg()):
    logger.debug(f"用户: {event.user_id} 触发了设置命令")
    if event.user_id != Bot.AdminID:
        await config.finish(f"您不是管理员无法使用此命令!")

    if command_content := command_args.extract_plain_text():
        command_parts = command_content.split()
        if len(command_parts) < 3:
            await config.finish("命令格式不正确，请输入: set <类名> <属性名> <值>")

        user_class_name = command_parts[0].lower()
        key = command_parts[1]
        value = convert_value(command_parts[2])

        # check class name
        class_name_map = {cls_name.lower(): cls_name for cls_name in ConfigProvider.VALID_CLASS_NAMES}
        matched_class_name = class_name_map.get(user_class_name)

        # check attr name
        attr_name_map = {value_name.lower(): value_name for value_name in ConfigProvider.VALID_ATTR_NAMES}
        matched_attr_name = attr_name_map.get(key.lower())

        if not matched_class_name:
            await config.finish(f"无效的类名: {command_parts[0]}")

        try:
            if await ConfigProvider.change_config(class_name=matched_class_name, key=matched_attr_name, value=value):
                # finish raise FinishedException
                await config.send(f"{matched_class_name} 的 {matched_attr_name} 已成功更改为 {value}")
            else:
                await config.send(f"无法更改 {matched_class_name} 的 {key}")
        except TypeError:
            await config.finish(f"类型不匹配, 请检测你输入的类型是否正确")
        except Exception as e:
            await config.finish(f"更改配置时出错：{e}")
    else:
        await config.finish("请输入命令内容!")
