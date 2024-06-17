import aiohttp
from loguru import logger
from .config import config
from .utils import build_openai_request

async def call_openai_api(context: str):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {config.openai_api_key}"
    }
    data = build_openai_request(context, config.openai_max_tokens)

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(config.api_url, headers=headers, json=data) as response:
                result = await response.json()
                if response.status == 200:
                    return result["choices"][0]["message"]["content"].strip()
                else:
                    logger.error(f"请求失败: {result.get('error', {}).get('message', '未知错误')}")
                    return "请求失败"
        except Exception as e:
            logger.error(f"请求出错: {e}")
            return "请求出错"

