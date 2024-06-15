import aiohttp
import random
import asyncio
from nonebot.log import logger
from .config import api_key, proxy_api_url, max_tokens

async def call_openai_api(context: str):
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
                    return result["choices"][0]["message"]["content"].strip()
                else:
                    return f"请求失败: {result.get('error', {}).get('message', '未知错误')}"
        except Exception as e:
            logger.error(f"请求出错: {e}")
            return f"请求出错: {str(e)}"

async def send_split_messages(bot, event, message, separator="(+)", min_delay=1000, max_delay=5000):
    segments = message.split(separator)
    for segment in segments:
        await bot.send(event, segment.strip())
        delay = random.randint(min_delay, max_delay)
        await asyncio.sleep(delay / 1000.0)

