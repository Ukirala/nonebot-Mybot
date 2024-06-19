import aiohttp
import asyncio
import base64
import json
from PIL import Image
from io import BytesIO
import aiofiles


async def process_image(file_path):
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

    return encoded_image


async def send_request(api_key, encoded_image):
    # 构建 JSON 请求体
    request_data = {
        "contents": [
            {
                "parts": [
                    {"text": "这个图片是什么内容?"},
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

    # 将请求体转换为 JSON 字符串
    request_json = json.dumps(request_data)

    url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}'
    headers = {
        'Content-Type': 'application/json'
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=request_json) as response:
            response_text = await response.text()
            return response_text


async def main():
    api_key = ''  # 请替换为你的实际 API 密钥
    image_path = 'a.jpg'

    encoded_image = await process_image(image_path)
    response_text = await send_request(api_key, encoded_image)

    response_data = json.loads(response_text)
    print(response_data['candidates'][0]['content']['parts'][0]['text'])


if __name__ == '__main__':
    # 运行主异步函数
    asyncio.run(main())
