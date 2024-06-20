import json
import re
import os
from typing import Union
import aiofiles

comment_re = re.compile(r'(?<!\\)//.*?$|\/\*(\s|\S)*?\*/', re.MULTILINE)


class OpenAI:
    API_KEY: Union[str, None] = None
    MODEL: Union[str, None] = None
    BASE_URL: Union[str, None] = None


class Spacy:
    MODEL: Union[str, None] = None


class MessageQueue:
    MAXQueueSize: Union[int, None] = None


class Cloudflare:
    AccountID: Union[str, None] = None
    API_Key: Union[str, None] = None


class Google:
    API_KEY: Union[str, None] = None


class ConfigFileNotFoundException(Exception):
    pass


class ConfigProvider:
    _instance = None
    VALID_CLASS_NAMES = ['OpenAI', 'Spacy', 'MessageQueue', 'Cloudflare', 'Google']

    def __init__(self):
        self.config: dict = {}
        self.load_config()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def load_config(self):
        if not os.path.exists('./config.jsonc'):
            raise ConfigFileNotFoundException("Configuration file 'config.jsonc' not found")

        for class_name in self.VALID_CLASS_NAMES:
            self.config.setdefault(class_name, {})

        # if config.future exists, rename it to config.jsonc
        if os.path.exists('./config.future'):
            os.replace('./config.future', './config.jsonc')

        with open('./config.jsonc', 'r', encoding='utf-8') as f:
            jsonc_data = f.read()

        # remove comments
        json_data = comment_re.sub('', jsonc_data)
        self.config = json.loads(json_data)

        # set class attributes
        OpenAI.API_KEY = self.config.get('OpenAI', {}).get('API_KEY', None)
        OpenAI.MODEL = self.config.get('OpenAI', {}).get('MODEL', None)
        OpenAI.BASE_URL = self.config.get('OpenAI', {}).get('BASE_URL', None)

        Spacy.MODEL = self.config.get('Spacy', {}).get('MODEL', None)

        MessageQueue.MAXQueueSize = self.config.get('MessageQueue', {}).get('MAXQueue', None)

        Cloudflare.AccountID = self.config.get('Cloudflare', {}).get('AccountID', None)
        Cloudflare.API_Key = self.config.get('Cloudflare', {}).get('API_Key', None)

        Google.API_KEY = self.config.get('Google', {}).get('API_KEY', None)

    def get_class_by_name(self, class_name):
        match class_name:
            case 'OpenAI':
                return OpenAI
            case 'Spacy':
                return Spacy
            case 'MessageQueue':
                return MessageQueue
            case 'Cloudflare':
                return Cloudflare
            case 'Google':
                return Google
            case _:
                return None

    async def change_config(self, class_name: str, key: str, value: Union[str, int]) -> bool:
        if class_name not in self.VALID_CLASS_NAMES:
            return False

        class_obj = self.get_class_by_name(class_name)
        if class_obj is None:
            return False

        if not hasattr(class_obj, key):
            return False

        # get type
        current_type = type(getattr(class_obj, key))
        new_type = type(value)
        if current_type != new_type:
            return False

        # update config
        setattr(class_obj, key, value)
        self.config[class_name][key] = value

        async with aiofiles.open('./config.future', 'w', encoding='utf-8') as future_file:
            await future_file.write(json.dumps(self.config, indent=4))

        return True


if __name__ == "__main__":
    config_provider = ConfigProvider()
    # 通过 ConfigProvider 获取配置
    print(OpenAI.API_KEY)
    print(OpenAI.MODEL)
    print(OpenAI.BASE_URL)
    print(Spacy.MODEL)
    print(MessageQueue.MAXQueueSize)
    print(Cloudflare.AccountID)
    print(Cloudflare.API_Key)
    print(Google.API_KEY)


    async def example():
        try:
            result = await config_provider.change_config('Spacy', 'MODEL', 'zh_core_web_trf')
            print(f"Config change result: {result}")
        except Exception as e:
            print(f"Error changing config: {e}")


    import asyncio

    asyncio.run(example())
