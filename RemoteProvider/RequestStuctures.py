# coding utf-8

from datetime import datetime

from DataManager.database import Message
from Skype.RequestCommands import *

__all__ = ["SkpyRequest",
           "ChatMessageRequest",
           "ChatMessageEditRequest",
           "ChatMessageErrorRequest",
           "SkypeStateRequest",
           "UpdateRequest",
           "ChatEventRequest",
           ]


class SkpyRequest:
    def __init__(self, type_request):
        self.type = type_request
        self.service_name = SERVICE_NAME_SKPY

    def on_send(self):
        pass


class ChatMessageRequest(SkpyRequest):
    def __init__(self, chat_name, mes_author, mes_pretty_author, mes_datetime, message_text, message_id, id):
        super().__init__(REQUEST_TYPE_IDENTIFIER_CHAT_MESSAGE_NEW)
        self.chat_name = chat_name
        self.mes_pretty_author = mes_pretty_author
        self.mes_author = mes_author
        self.mes_datetime = int((mes_datetime - datetime(1970, 1, 1)).total_seconds())
        self.message_text = message_text
        self.message_id = message_id
        self.id = id

    def on_send(self):
        message = Message.get(id=self.id)
        message.sended = True
        message.save()


class ChatMessageEditRequest(SkpyRequest):
    def __init__(self, message_text, message_id, mes_author, mes_pretty_author, chat_name, mes_datetime):
        super().__init__(REQUEST_TYPE_IDENTIFIER_CHAT_MESSAGE_EDIT)
        self.chat_name = chat_name
        self.message_id = message_id
        self.message_text = message_text
        self.mes_pretty_author = mes_pretty_author
        self.mes_author = mes_author
        self.mes_datetime = int((mes_datetime - datetime(1970, 1, 1)).total_seconds())


class ChatMessageErrorRequest(SkpyRequest):
    def __init__(self, message_text, error_priority):
        super().__init__(REQUEST_TYPE_IDENTIFIER_MESSAGE_ERROR)
        self.message_text = message_text
        self.error_priority = error_priority


class SkypeStateRequest(SkpyRequest):
    def __init__(self, request_user_ids=None, contacts_user_ids=None):
        super().__init__(REQUEST_TYPE_IDENTIFIER_SKYPE_STATE)
        self.request_user_ids = request_user_ids
        self.contacts_user_ids = contacts_user_ids


class UpdateRequest(SkpyRequest):
    def __init__(self):
        super().__init__(REQUEST_TYPE_IDENTIFIER_UPDATE)


class ChatEventRequest(SkpyRequest):
    def __init__(self, **kwargs):
        super().__init__(REQUEST_TYPE_IDENTIFIER_EVENT)
        self.__dict__.update(kwargs)
