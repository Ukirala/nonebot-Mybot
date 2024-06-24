import asyncio
import random

import nonebot
from nonebot.adapters.onebot.v11 import Adapter as ONEBOT_V11Adapter
from nonebot.log import logger

from core.ConfigProvider import ConfigProvider
from utils.SentencesSpliter import SentencesSpliter
from utils.Weather import Weather


#  logger.add("trace.log", level="TRACE", format=default_format)
#  输出日志到文件谨慎开启，image2text的日志非超多，不一会就能写出几百MB
async def load_config():
    config_provider = ConfigProvider.get_instance()
    config_provider.load_config()


async def load_model():
    SentencesSpliter.load_model()


async def main():
    tasks = []

    logger.info("开始获取随机数种子...")
    tasks.append(Weather.get_ticket())

    logger.info("加载配置文件...")
    tasks.append(asyncio.create_task(load_config()))

    logger.info("加载分句器模型...")
    tasks.append(asyncio.create_task(load_model()))

    await asyncio.gather(*tasks)

    random.seed(await Weather.get_seed())

    logger.info("启动...")


if __name__ == "__main__":
    asyncio.run(main())
    nonebot.init()

    driver = nonebot.get_driver()
    driver.register_adapter(ONEBOT_V11Adapter)

    nonebot.load_plugins("plugins")
    nonebot.run()
