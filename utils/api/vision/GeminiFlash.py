import asyncio
import base64
import time
import json
import os
from io import BytesIO

import httpx
from nonebot.log import logger
import aiofiles
from PIL import Image


async def download_image(img_url: str) -> str:
    logger.info(f"Downloading image from {img_url}")
    # 创建保存目录
    save_dir = "cache/imgs"
    os.makedirs(save_dir, exist_ok=True)

    file_path = os.path.join(save_dir, f"{time.time()}.jpg")

    # 使用 httpx 请求图片
    async with httpx.AsyncClient() as client:
        response = await client.get(img_url)
        if response.status_code == 200:
            # 读取图篇内容
            img_data = response.content

            # 保存图片
            with open(file_path, 'wb') as file:
                file.write(img_data)
                logger.info(f"Image saved to {file_path}")
            return file_path
        else:
            raise Exception(f"Failed to retrieve image. Status code: {response.status_code}")


async def process_image(file_path: str) -> str:
    logger.info(f"Processing image {file_path}")
    # 打开并调整图像大小
    async with aiofiles.open(file_path, 'rb') as image_file:
        img = Image.open(BytesIO(await image_file.read()))
        img_resized = img.resize((512, int(img.height * 512 / img.width)))

        if img_resized.mode != 'RGB':
            img_resized = img_resized.convert('RGB')

        # 将调整大小后的图像保存到内存中并进行 Base64 编码
        buffered = BytesIO()
        img_resized.save(buffered, format="JPEG")
        encoded_image = base64.b64encode(buffered.getvalue()).decode('utf-8')

    logger.info("Image processed")
    return encoded_image


async def send_request(api_key: str, encoded_image: str) -> dict:
    url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}'
    headers = {
        'Content-Type': 'application/json'
    }
    request_data = {
        "contents": [
            {
                "parts": [
                    {"text": "使用中文回答这个图片是什么内容?"},
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": encoded_image
                        }
                    }
                ]
            }
        ]
    }

    logger.info(f"Sending request")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=request_data, timeout=10)
            logger.info(f"Request sent, waiting for response: {response.status_code}")
            response_json = response.json()
            logger.info("Request sent successfully")
            return response_json
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error occurred: {e}")
        raise
    except httpx.RequestError as e:
        logger.error(f"Request failed: {e}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON response: {e}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise


async def main():
    api_key = 'AIzaSyDZgdP21rBRsNXWBeXBk8B0dQz86RT8-Hs'
    image_path = r'D:\Py_Project\nonebot-Mybot\cache\imgs\1.png'

    encoded_image = await process_image(image_path)
    response_text = await send_request(api_key, encoded_image)

    print(response_text['candidates'][0]['content']['parts'][0]['text'])


if __name__ == '__main__':
    # 运行主异步函数
    asyncio.run(main())