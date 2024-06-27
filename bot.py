import asyncio
import random
import sys

import nonebot
from nonebot.adapters.onebot.v11 import Adapter as ONEBOT_V11Adapter
from nonebot.log import logger

from core.ConfigProvider import ConfigProvider
from utils.SentencesSpliter import SentencesSpliterManager
from utils.Weather import Weather

log_format = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level}</level> |"
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)

# 添加一个控制台输出，并设置格式和颜色
logger.remove()  # 移除默认的日志配置
logger.add(sys.stdout, format=log_format, level="DEBUG")


async def load_config():
    config_provider = ConfigProvider.get_instance()
    config_provider.load_config()


async def main():
    tasks = []

    logger.info("开始获取随机数种子...")
    tasks.append(Weather.get_ticket())

    logger.info("加载配置文件...")
    tasks.append(asyncio.create_task(load_config()))

    await asyncio.gather(*tasks)
    random.seed(await Weather.get_seed())

    logger.info("启动...")


if __name__ == "__main__":
    asyncio.run(main())

    logger.info("加载分句器模型...")
    if SentencesSpliterManager.initialize_model():
        logger.info("分句器模型加载成功！")

    nonebot.init()

    driver = nonebot.get_driver()
    driver.register_adapter(ONEBOT_V11Adapter)

    nonebot.load_plugins("plugins")
    nonebot.run()
