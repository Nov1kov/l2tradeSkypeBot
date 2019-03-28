# coding utf-8
import datetime
from skpy import Skype


class SkypeState:
    MIN_REQUEST_UPDATE_TIME = 60

    def __init__(self, skype: Skype):
        self.__skype = skype
        self.__contact_requests = []
        self.__last_update_time = datetime.datetime.now() - datetime.timedelta(
            seconds=SkypeState.MIN_REQUEST_UPDATE_TIME)

    def update(self) -> dict:
        result = dict()
        if (datetime.datetime.now() - self.__last_update_time).total_seconds() > SkypeState.MIN_REQUEST_UPDATE_TIME:
            self.__last_update_time = datetime.datetime.now()
            self.__contact_requests = [contact.userId for contact in self.__skype.contacts.requests()]
            result['request_user_ids'] = self.__contact_requests
            self.__skype.contacts.sync()
            result['contacts_user_ids'] = list(self.__skype.contacts.cache.keys())

        return result
