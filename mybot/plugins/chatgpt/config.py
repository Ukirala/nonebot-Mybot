# config.py
from nonebot import get_driver
from pydantic import BaseModel

class Config(BaseModel):
    oachat_on_command: str
    api_url: str
    openai_api_key: str
    cloudflare_api_key: str
    cloudflare_account_id: str
    openai_max_tokens: int
    oachat_queue_size: int

config = Config.parse_obj(get_driver().config.dict())

