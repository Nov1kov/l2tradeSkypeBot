# coding utf-8
import logging
from datetime import datetime
from time import sleep

import requests
from skpy import SkypeEventLoop, SkypeMessageEvent, SkypeAuthException, SkypeSingleChat, SkypeNewMessageEvent, \
    SkypeGroupChat, SkypeEditMessageEvent, SkypeApiException, SkypeChatMemberEvent, SkypeEvent, SkypeEndpointEvent, \
    SkypeChatUpdateEvent, SkypeMsg

from DataManager.Settings import Settings
from DataManager.SkypeState import SkypeState
from DataManager.database import Message
from RemoteProvider.RemoteProvider import RemoteProvider
from Skype import Utils
from Skype.MessageFormatter import MessageFormatter
from Skype.RequestCommands import *

SEND_MESSAGE_DELAY = 3


class ChatBot(SkypeEventLoop):
    def __init__(self):
        super(ChatBot, self).__init__()
        self.__settings = Settings()
        self.__remote_provider = None
        self.__logging = logging.getLogger('ChatBot')
        self.__skype_state = SkypeState(self)
        self.__message_formatter = MessageFormatter()

    def load(self):
        self.conn.setTokenFile(self.__settings.token_file)
        try:
            self.conn.readToken()
        except SkypeAuthException:
            self.__logging.warning("SkypeAuthException")
            self.__login()
        self.__send_last_messages()

    def __send_last_messages(self):
        chats = self.chats.recent()
        for chat in chats.values():
            for message in chat.getMsgs():
                self.__receive_message(message)

    def __login(self):
        # Prompt the user for their credentials.
        self.conn.setUserPwd(*self.__settings.get_auth_data())
        self.conn.getSkypeToken()

    def set_remote_provider(self, network: RemoteProvider):
        self.__remote_provider = network
        self.__remote_provider.set_callback_handler(self.__remote_provider_response)

    def __remote_provider_response(self, response_messages: list):
        for message in response_messages:
            if message is not None:
                self.__logging.debug("response: " + str(message))
                if message.type == TYPE_IDENTIFIER_MESSAGE_USER_CHAT:
                    if isinstance(message.user_ids, list):
                        for user_id in message.user_ids:
                            self.__send_private_chat(user_id, message.message_text)
                            sleep(SEND_MESSAGE_DELAY)

                elif message.type == TYPE_IDENTIFIER_MESSAGE_GROUP_CHAT:
                    if isinstance(message.chat_ids, list):
                        formatted_message_text = self.__format_message(message.message_text,
                                                                       message.quote_user_id,
                                                                       message.quote_user_name,
                                                                       message.quote_timestamp,
                                                                       message.quote_chat_name)
                        for chat_id in message.chat_ids:
                            self.__send_group_chat(chat_id, formatted_message_text)
                            sleep(SEND_MESSAGE_DELAY)

                elif message.type == TYPE_IDENTIFIER_MESSAGE_EDIT_MESSAGE:
                    self.__edit_message_chat(message.chat_id, message.message_id, message.message_text)

                elif message.type == TYPE_IDENTIFIER_CHAT_ADD_MEMBER:
                    self.__chat_add_member(message.chat_id, message.user_id)

                elif message.type == TYPE_IDENTIFIER_CHAT_REMOVE_MEMBER:
                    self.__chat_remove_member(message.chat_id, message.user_id)

                elif message.type == TYPE_IDENTIFIER_CONTACT_ACCEPT_REQUEST:
                    self.__accept_request(message.user_id, True)

                elif message.type == TYPE_IDENTIFIER_CONTACT_REJECT_REQUEST:
                    self.__accept_request(message.user_id, False)

    def __chat_add_member(self, chat_id, user_id):
        try:
            chat = self.chats.chat(chat_id)
            return chat.addMember(user_id)
        except SkypeApiException as e:
            logging.error(str(e))
            return None

    def __chat_remove_member(self, chat_id, user_id):
        try:
            chat = self.chats.chat(chat_id)
            return chat.removeMember(user_id)
        except SkypeApiException as e:
            logging.error(str(e))
            return None

    def __accept_request(self, user_id, accept: bool):
        contacts = self.contacts.requests()
        for request in contacts:
            if request.userId == user_id:
                if accept:
                    request.accept()
                else:
                    request.reject()

    def _send_message_to_remote(self, *args):
        if self.__remote_provider is not None:
            self.__remote_provider.message_send(*args)

    def _send_edit_message_to_remote(self, *args):
        if self.__remote_provider is not None:
            self.__remote_provider.message_edit(*args)

    def _send_edit_message_error(self, *args):
        if self.__remote_provider is not None:
            self.__remote_provider.message_error(*args)

    def _send_event(self, event: SkypeEvent):
        if self.__remote_provider is not None:
            self.__remote_provider.event(event)

    def __send_private_chat(self, actor, msg):
        try:
            chat = self.contacts.user(actor).chat
            return chat.sendMsg(msg, rich=True)
        except SkypeApiException as e:
            return None

    def __edit_message_chat(self, chat_id: str, msg_id: int, msg: str):
        try:
            chat = self.chats.chat(chat_id)
            return chat.sendMsg(msg, edit=msg_id)
        except SkypeApiException as e:
            return None

    def __send_group_chat(self, chat_id, msg):
        try:
            chat = self.chats.chat(chat_id)
            return chat.sendMsg(msg, rich=True)
        except SkypeApiException as e:
            return None

    def __format_message(self, message_text, quote_user_id, quote_user_name, quote_timestamp, quote_chat_name):
        if quote_user_id is None or quote_user_name is None or quote_timestamp is None:
            formatted_text = message_text
        else:
            quote_datetime = datetime.fromtimestamp(quote_timestamp)
            formatted_text = Utils.quote(message_text, quote_user_id, quote_user_name, quote_datetime, quote_chat_name)
        return formatted_text

    def __get_user_sender(self, message: SkypeMsg):
        try:
            user_sender = self.contacts.contact(message.userId)
        except KeyError as e:
            self.__logging.warning("onEvent: " + str(e))
            user_sender = self.contacts.user(message.userId)
        except SkypeAuthException as e:
            self.__logging.warning("onEvent: " + str(e))
            user_sender = self.contacts.user(message.userId)
        except SkypeApiException as e:
            user_sender = self.contacts.contact(message.userId)
        return user_sender

    def __receive_edit_message(self, message: SkypeMsg):
        user_sender = self.__get_user_sender(message)
        if user_sender == self.user:
            return

        if isinstance(message.chat, SkypeSingleChat):
            self.__logging.info('SkypeSingleChat: ' + message.chat.userId)

        elif isinstance(message.chat, SkypeGroupChat):
            mes_body = message.content
            mes_author = message.userId
            mes_pretty_author = str(user_sender.name)
            mes_datetime = message.time
            chat_name = message.chatId

            mes_edited_body_text = self.__message_formatter.edit_message(mes_body)
            self._send_edit_message_to_remote(mes_edited_body_text, message.clientId, mes_author,
                                              mes_pretty_author, chat_name, mes_datetime)

    def __receive_message(self, message: SkypeMsg):
        user_sender = self.__get_user_sender(message)
        if user_sender == self.user or user_sender is None:
            return

        if isinstance(message.chat, SkypeSingleChat):
            self.__logging.info('SkypeSingleChat: ' + message.chat.userId)

        elif isinstance(message.chat, SkypeGroupChat):
            mes_db, created = Message.get_or_create_message(message)
            if not mes_db.sended:
                self._send_message_to_remote(message.chatId,

                                             message.userId,
                                             str(user_sender.name),
                                             message.time,
                                             message.content,
                                             message.clientId,
                                             message.id)
            else:
                logging.debug('message {} is also sended'.format(mes_db.id))

    def onEvent(self, event):
        if event is not None:
            self.__logging.info("event: " + event.type)

        if isinstance(event, SkypeMessageEvent) and not event.msg.userId == self.userId:
            message = event.msg
            if isinstance(event, SkypeNewMessageEvent):
                self.__receive_message(message)

            elif isinstance(event, SkypeEditMessageEvent):
                self.__receive_edit_message(message)

        elif isinstance(event, (SkypeChatMemberEvent, SkypeChatUpdateEvent)):
            self._send_event(event)

    def custom_cycle(self):
        try:
            events = self.getEvents()
        except requests.ConnectionError:
            return
        for event in events:
            self.onEvent(event)
            if self.autoAck:
                event.ack()

    def custom_loop(self):
        while True:
            try:
                self.custom_cycle()
                state_dict = self.__skype_state.update()
                if self.__remote_provider is not None:
                    self.__remote_provider.skype_state(**state_dict)
                    self.__remote_provider.send_requests()
            except SkypeAuthException as e:
                logging.error("Skype Auth Exception: \n" + str(e))
                self.__login()
                continue
            except SkypeApiException as e:
                logging.error("Skype Api Exception:\n" + str(e))
                sleep(5)
                try:
                    self.conn.refreshSkypeToken()
                except SkypeAuthException as e:
                    pass
                continue
            except Exception as e:
                logging.error(str(e))
                continue
