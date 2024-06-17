import nonebot
import aiohttp
import asyncio
import os
import time
import ssl
from datetime import datetime
from loguru import logger


# 缓存图片的目录
IMAGE_CACHE_DIR = "mybot/plugins/chatgpt/image_cache"

# 创建缓存目录，如果不存在
if not os.path.exists(IMAGE_CACHE_DIR):
    os.makedirs(IMAGE_CACHE_DIR)
    logger.info(f"创建缓存目录: {IMAGE_CACHE_DIR}")


async def clear_image_cache():
    """
    定期清理缓存图片的任务，每隔600秒自动清理过期缓存。
    """
    while True:
        now = time.time()
        deleted_files = 0
        deleted_size = 0
        for filename in os.listdir(IMAGE_CACHE_DIR):
            file_path = os.path.join(IMAGE_CACHE_DIR, filename)
            if os.path.isfile(file_path) and now - os.path.getmtime(file_path) > 600:
                deleted_size += os.path.getsize(file_path)
                os.remove(file_path)
                deleted_files += 1
                logger.info(f"已删除缓存图片: {file_path}")
        logger.info(f"清理缓存完成，删除文件数: {deleted_files}, 总大小: {deleted_size} bytes")
        await asyncio.sleep(600)

async def download_image(url: str) -> str:
    """
    下载图片到本地的函数构成，使用时间戳命名文件以确保唯一性。
    
    :param url: 图片的URL地址
    :return: 本地图片路径
    """
    ssl_context = ssl.create_default_context()
    ssl_context.set_ciphers("DEFAULT@SECLEVEL=1")  # 降低 SSL 等级
    
    # 使用时间戳命名文件
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
    image_filename = f"{timestamp}.jpg"
    image_path = os.path.join(IMAGE_CACHE_DIR, image_filename)

    try:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=10)) as session:
            async with session.get(url, ssl=ssl_context) as response:
                if response.status == 200:
                    with open(image_path, 'wb') as f:
                        f.write(await response.read())
                    logger.info(f"图片下载成功: {image_path}")
                    return image_path
                else:
                    logger.error(f"无法下载图片: {url}, 状态码: {response.status}")
                    return None
    except aiohttp.ClientError as e:
        logger.error(f"下载图片请求失败: {e}")
        return None
    except Exception as e:
        logger.error(f"未知错误: {e}")
        return None


async def image_to_text(image_url: str) -> str:
    """
    调用 Workers AI 进行图像转文字描述。
    
    :param image_url: 图片的URL地址
    :return: 图片描述内容
    """
    logger.info(f"Starting image to text conversion for URL: {image_url}")

    # 下载图片到本地
    image_path = await download_image(image_url)
    if not image_path:
        return "[image 转文字失败]"

    url = f"https://api.cloudflare.com/client/v4/accounts/{config.cloudflare_account_id}/ai/run/@cf/llava-hf/llava-1.5-7b-hf"
    headers = {
        "Authorization": f"Bearer {config.cloudflare_api_key}",
        "Content-Type": "application/json"
    }

    async with aiohttp.ClientSession() as session:
        try:
            with open(image_path, 'rb') as f:
                image_blob = f.read()

            image_array = list(image_blob)
            inputs = {
                "image": image_array,
                "prompt": "Generate a title for this image, include emotion, if it has emotion.",
                "max_tokens": 512
            }

            logger.debug(f"Sending request to {url} with headers: {headers} and inputs: {inputs}")
            async with session.post(url, headers=headers, json=inputs) as response:
                result = await response.json()
                logger.debug(f"Received response: {result}")
                if response.status == 200 and result.get("success"):
                    description = result["result"].get("description", "[image 转文字失败]")
                    logger.info(f"Image to text conversion successful: {description}")
                    return description
                else:
                    error_message = result.get('errors', [{'message': '未知错误'}])[0]['message']
                    logger.error(f"请求失败: {error_message}")
                    return "[image 转文字失败]"
        except aiohttp.ClientError as e:
            logger.error(f"HTTP请求出错: {e}")
            return "[image 转文字失败]"
        except Exception as e:
            logger.error(f"请求出错: {e}")
            return "[image 转文字失败]"


@nonebot.get_driver().on_startup
async def startup():
    asyncio.create_task(clear_image_cache())

