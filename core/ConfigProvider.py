import json
import os
import re
from typing import Union

import aiofiles

comment_re = re.compile(r'(?<!\\)//.*?$|/\*(\s|\S)*?\*/', re.MULTILINE)


class OpenAI:
    Https: bool = True
    APIKey: Union[str, None] = None
    MODEL: Union[str, None] = "gpt-3.5-turbo"
    BaseUrl: Union[str, None] = None


class Spacy:
    ENABLE: bool = True
    MODEL: Union[str, None] = None


class MessageQueue:
    MaxQueueSize: Union[int, None] = None


class Cloudflare:
    ENABLE: bool = True
    AccountID: Union[str, None] = None
    APIKey: Union[str, None] = None


class Google:
    ENABLE: bool = True
    APIKey: Union[str, None] = None


class Bot:
    AdminID: Union[int, None] = None
    IsCrossGroup: Union[bool, None] = None


class ConfigFileNotFoundException(Exception):
    pass


class ConfigKeyTypeNotFoundException(Exception):
    pass


def get_class_by_name(class_name: str):
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


class ConfigProvider:
    _instance = None
    VALID_CLASS_NAMES: list = ['OpenAI', 'Spacy', 'MessageQueue', 'Cloudflare', 'Google']
    VALID_ATTR_NAMES: list = ['Https', 'APIKey', 'MODEL', 'BaseUrl', 'ENABLE', 'MaxQueueSize', 'AccountID', 'AdminID',
                              'IsCrossGroup']
    config: dict = {}

    def __init__(self):
        for class_name in self.VALID_CLASS_NAMES:
            self.config.setdefault(class_name, {})

        self.load_config()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def load_config(cls):
        if not os.path.exists('./config.jsonc'):
            raise ConfigFileNotFoundException("Config file 'config.jsonc' not found")

        # if config.future exists, rename to config.jsonc
        if os.path.exists('./config.future'):
            os.replace('./config.future', './config.jsonc')

        with open('./config.jsonc', 'r', encoding='utf-8') as f:
            jsonc_data = f.read()

        # remove comments
        json_data = comment_re.sub('', jsonc_data)
        cls.config = json.loads(json_data)

        # set class attributes
        OpenAI.Https = cls.config.get('OpenAI', {}).get('Https', True)
        OpenAI.APIKey = cls.config.get('OpenAI', {}).get('APIKey', None)
        OpenAI.BaseUrl = cls.config.get('OpenAI', {}).get('BaseUrl', None)
        OpenAI.MODEL = cls.config.get('OpenAI', {}).get('MODEL', "gpt-3.5-turbo")

        Spacy.ENABLE = cls.config.get('Spacy', {}).get('ENABLE', True)
        if Spacy.ENABLE:
            Spacy.MODEL = cls.config.get('Spacy', {}).get('MODEL', None)

        MessageQueue.MaxQueueSize = cls.config.get('MessageQueue', {}).get('MaxQueueSize', 50)

        Cloudflare.ENABLE = cls.config.get('Cloudflare', {}).get('ENABLE', True)
        if Cloudflare.ENABLE:
            Cloudflare.AccountID = cls.config.get('Cloudflare', {}).get('AccountID', None)
            Cloudflare.APIKey = cls.config.get('Cloudflare', {}).get('APIKey', None)

        Google.ENABLE = cls.config.get('Google', {}).get('ENABLE', True)
        if Google.ENABLE:
            Google.APIKey = cls.config.get('Google', {}).get('APIKey', None)

        Bot.AdminID = cls.config.get('Bot', {}).get('AdminID', None)
        Bot.IsCrossGroup = cls.config.get('Bot', {}).get('IsCrossGroup', False)

    @classmethod
    async def change_config(cls, class_name: str, key: str, value: Union[str, int, bool]) -> bool:
        if class_name not in cls.VALID_CLASS_NAMES:
            return False

        class_obj = get_class_by_name(class_name)
        if class_obj is None:
            return False

        if not hasattr(class_obj, key):
            return False

        # get type
        current_type = type(getattr(class_obj, key))
        new_type = type(value)
        if current_type != new_type:
            raise TypeError(f"Type mismatch: {current_type} != {new_type}")

        # update config
        setattr(class_obj, key, value)
        cls.config[class_name][key] = value

        async with aiofiles.open('./config.future', 'w', encoding='utf-8') as future_file:
            await future_file.write(json.dumps(cls.config, indent=4))

        return True
