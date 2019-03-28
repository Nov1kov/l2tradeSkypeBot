# coding utf-8
import re


class MessageFormatter:
    def __init__(self):
        self.__re_edit_body = re.compile(r'Edited previous message: (.*)<e_m ts="')

    def edit_message(self, mes_body) -> str:
        return self.__re_edit_body.search(mes_body).group(1)

