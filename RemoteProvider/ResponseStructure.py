# coding utf-8
import json
from datetime import datetime


class Response:
    def __init__(self):
        pass

    def get_datetime(self):
        mes_datetime = self.mes_datetime
        if mes_datetime != '':
            return datetime.fromtimestamp(mes_datetime)
        return datetime.now()

    def __getattr__(self, key):
        return None

    def __str__(self):
        return json.dumps(self.__dict__, indent=2)
