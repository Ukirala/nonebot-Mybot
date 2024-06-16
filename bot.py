import nonebot
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import Adapter as ONEBOT_V11Adapter

default_format = "{time} | {level} | {message}"

nonebot.init()
logger.add("trace.log", level="TRACE", format=default_format)

driver = nonebot.get_driver()
driver.register_adapter(ONEBOT_V11Adapter)

nonebot.load_plugins("src/plugins")

if __name__ == "__main__":
    nonebot.run()
