import nonebot
from nonebot.adapters.onebot.v11 import Adapter as ONEBOT_V11Adapter

default_format = "{time} | {level} | {message}"

nonebot.init()
#  logger.add("trace.log", level="TRACE", format=default_format)
#  输出日志到文件谨慎开启，image2text的日志非超多，不一会就能写出几百MB

driver = nonebot.get_driver()
driver.register_adapter(ONEBOT_V11Adapter)

nonebot.load_plugins("plugins")

if __name__ == "__main__":
    nonebot.run()
