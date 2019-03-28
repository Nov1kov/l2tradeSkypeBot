# -*- coding: utf-8 -*-
import json
import logging
import socket

import datetime

from skpy import SkypeEvent, SkypeChatMemberEvent

from RemoteProvider.RequestStuctures import *
from .RequestBuilder import RequestBuilder


class RemoteProvider:
    MIN_REQUEST_UPDATE_TIME = 10

    def __init__(self, tcp_ip, tcp_port):
        self.tcpIp = tcp_ip
        self.tcpPort = tcp_port
        self.requestBuilder = RequestBuilder()
        self.__callback_handler = None
        self.__request_list = []  # list of SkpyRequest
        self.__last_send_time = datetime.datetime.now()

    def __send(self, data: bytes):
        self.__last_send_time = datetime.datetime.now()
        s = socket.socket()
        try:
            s.connect((self.tcpIp, self.tcpPort))
            s.send(data)
            self.__receive_response(self.recvall(s))
            return True
        except Exception as e:
            logging.error(str(e))
            return False
        finally:
            s.close()

    @staticmethod
    def recvall(sock) -> bytes:
        # Helper function to recv n bytes or return None if EOF is hit
        data = b''
        while True:
            packet = sock.recv(4096)
            if not packet:
                logging.debug('len of recv data: ' + str(len(data)))
                return data
            data += packet

    def __receive_response(self, data: bytes):
        response = self.requestBuilder.get_new_messages_list(data)
        if self.__callback_handler is not None and response is not None:
            self.__callback_handler(response)

    def message_send(self, *args):
        new_request = ChatMessageRequest(*args)
        self.__request_list.append(new_request)

    def message_edit(self, *args):
        new_request = ChatMessageEditRequest(*args)
        self.__request_list.append(new_request)

    def message_error(self, *args):
        new_request = ChatMessageErrorRequest(*args)
        self.__request_list.append(new_request)

    def update(self):
        new_request = UpdateRequest()
        self.__request_list.append(new_request)

    def event(self, event: SkypeEvent):
        params = dict(event_name=event.__class__.__name__)
        if isinstance(event, SkypeChatMemberEvent):
            params['user_ids'] = [user.id for user in event.users]
            params['chat_id'] = event.chat.id
        new_request = ChatEventRequest(**params)
        self.__request_list.append(new_request)

    def skype_state(self, **kwargs):
        if len(kwargs) > 0:
            new_request = SkypeStateRequest(**kwargs)
            self.__request_list.append(new_request)

    def send_requests(self):
        if len(self.__request_list) == 0 and (datetime.datetime.now() - self.__last_send_time).total_seconds() > \
                RemoteProvider.MIN_REQUEST_UPDATE_TIME:
            self.update()
        while len(self.__request_list) > 0:
            logging.info('request_list len: ' + str(len(self.__request_list)))
            request = self.__request_list.pop()
            json_bytes = self.__obj_to_json_bytes(request)
            if self.__send(json_bytes):
                request.on_send()
            else:
                logging.warning('fail send request, try again')
                self.__request_list.append(request)

    def __obj_to_json_bytes(self, obj) -> bytes:
        return json.dumps(obj.__dict__, ensure_ascii=False).encode('utf8')

    def set_callback_handler(self, callback_handler):
        self.__callback_handler = callback_handler
