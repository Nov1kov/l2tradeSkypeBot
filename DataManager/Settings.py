# coding utf-8
import json
import os


class Settings:
    TCP_IP = '127.0.0.1'
    TCP_PORT = 12398
    LOGS_FOLDER = 'log'
    TOKEN_FILE = '.tokens-app'
    CREDENTIALS_FILE = os.path.expanduser(os.path.join("~", ".l2trade_config"))

    _instance = None
    _first_init = True

    @staticmethod
    def __new__(cls, *more):
        if not cls._instance:
            cls._instance = super(Settings, cls).__new__(cls, *more)
        return cls._instance

    def __init__(self):
        if Settings._first_init:
            Settings._first_init = False

    @property
    def token_file(self):
        return Settings.TOKEN_FILE

    def get_auth_data(self):
        with open(Settings.CREDENTIALS_FILE, 'r') as f:
            json_object = json.loads(f.read())
            skype = json_object['skype']
            return skype['login'], skype['password']

    @property
    def remote_provider_settings(self):
        return Settings.TCP_IP, Settings.TCP_PORT

    @property
    def log_file(self):
        return Settings.LOGS_FOLDER
