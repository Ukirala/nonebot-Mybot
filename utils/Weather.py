import asyncio
import hashlib
import random
import time

import aiohttp
from loguru import logger


class Weather:
    index_url = 'https://h5.caiyunapp.com/h5'
    res_url = 'https://h5.caiyunapp.com/api/'
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/126.0.0.0 Safari/537.36'
    }

    @classmethod
    async def get_ticket(cls) -> None:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(cls.index_url, headers=cls.headers) as response:
                    if response.status == 200:
                        cookies = response.cookies
                        ticket_value = cookies.get('ticket').value
                        cls.headers['cookie'] = f"ticket={ticket_value}"
                        logger.debug(f"Got cookie: {ticket_value}")
                    else:
                        logger.error(f"Failed to get ticket, status code: {response.status}")
            except Exception as e:
                logger.error(f"Exception occurred while getting ticket: {e}")

    @classmethod
    async def get_seed(cls) -> int:
        async with aiohttp.ClientSession() as session:
            try:
                data = {
                    'url': f'https://api.caiyunapp.com/v2.5/<t2.5>/112.94,28.23/weather?dailysteps=16&hourlysteps=120&'
                           f'alert=true&begin={int(time.time())}'
                }
                async with session.post(cls.res_url, headers=cls.headers, json=data) as response:
                    if response.status == 200:
                        res = await response.json()

                        random_wind = random.sample(res["result"]["daily"]["wind"], 2)
                        random_aqi = random.sample(res["result"]["daily"]["air_quality"]["aqi"], 2)
                        random_humidity = random.sample(res["result"]["daily"]["humidity"], 2)
                        random_temperature = random.sample(res["result"]["daily"]["temperature"], 2)
                        random_precipitation = random.sample(res["result"]["daily"]["precipitation"], 2)

                        # full data
                        values = []

                        for item in random_wind:
                            values.append(item["max"]["speed"])

                        for item in random_aqi:
                            values.append(item["max"]["usa"])

                        for item in random_humidity:
                            values.append(item["max"])

                        for item in random_temperature:
                            values.append(item["min"])

                        for item in random_precipitation:
                            values.append(item["avg"])

                        seed_string = ''.join([str(int(value * random.randint(1003, 9999)) % 10) for value in values[:10]])

                        # generate seed
                        seed_hash = hashlib.sha256(seed_string.encode('utf-8')).hexdigest()
                        seed_int = int(seed_hash, 16) % (2 ** 32)  # 32-bit seed

                        return seed_int
                    else:
                        logger.error(f"Failed to get weather, status code: {response.status}")
            except Exception as e:
                logger.error(f"Exception occurred while getting weather: {e}")


async def main():
    await Weather.get_ticket()
    seed = await Weather.get_seed()
    print(seed)
    del Weather

if __name__ == '__main__':
    asyncio.run(main())
