import aiohttp
import asyncio
import time
from loguru import logger


class Weather:
    def __init__(self):
        self.index_url = 'https://h5.caiyunapp.com/h5'
        self.res_url = 'https://h5.caiyunapp.com/api/'
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/126.0.0.0 Safari/537.36'
        }

    async def get_ticket(self) -> None:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(self.index_url, headers=self.headers) as response:
                    if response.status == 200:
                        cookies = response.cookies
                        ticket_value = cookies.get('ticket').value
                        self.headers['cookie'] = f"ticket={ticket_value}"
                        logger.debug(f"Got cookie: {ticket_value}")
                    else:
                        logger.error(f"Failed to get ticket, status code: {response.status}")
            except Exception as e:
                logger.error(f"Exception occurred while getting ticket: {e}")

    async def get_weather(self) -> None:
        async with aiohttp.ClientSession() as session:
            try:
                # TODO 使用 config provide 提供经纬度
                data = {
                    'url': f'https://api.caiyunapp.com/v2.5/<t2.5>/112.94,28.23/weather?dailysteps=16&hourlysteps=120&'
                           f'alert=true&begin={int(time.time())}'
                }
                async with session.post(self.res_url, headers=self.headers, json=data) as response:
                    if response.status == 200:
                        res = await response.json()
                        res = res["result"]["daily"]["temperature"][0]
                        for r in res:
                            print(r, ":", res[r])
                    else:
                        logger.error(f"Failed to get weather, status code: {response.status}")
            except Exception as e:
                logger.error(f"Exception occurred while getting weather: {e}")


async def main():
    weather = Weather()
    await weather.get_ticket()
    await weather.get_weather()


if __name__ == '__main__':
    asyncio.run(main())
