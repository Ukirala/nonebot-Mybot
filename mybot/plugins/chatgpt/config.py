import nonebot

# 读取配置
config = nonebot.get_driver().config
api_key = config.openai_api_key
proxy_api_url = config.proxy_api_url
max_tokens = config.openai_max_tokens
oachat_on_command = config.oachat_on_command
history_count = int(getattr(config, 'oachat_history_count', 20))

