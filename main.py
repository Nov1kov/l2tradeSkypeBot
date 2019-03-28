#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import os

import datetime

from DataManager.Settings import Settings
from RemoteProvider.RemoteProvider import RemoteProvider
from Skype.SkypeWeb import ChatBot


def setup_logging(log_directory: str):
    logging.getLogger('').setLevel(logging.NOTSET)

    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    fh = logging.FileHandler(log_directory + '/LOG_' + datetime.datetime.now().strftime('%Y_%m_%d_%H_%M') + '.log')
    fh.setLevel(logging.NOTSET)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logging.getLogger('').addHandler(fh)

    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    # set a format which is simpler for console use
    formatter = logging.Formatter(fmt='%(asctime)s - %(filename)-12s: %(funcName)-6s %(message)s',
                                  datefmt='%H:%M:%S')
    # tell the handler to use this format
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)


if __name__ == '__main__':
    settings = Settings()
    setup_logging(settings.log_file)
    chatBot = ChatBot()
    remote_provider = RemoteProvider(*settings.remote_provider_settings)
    chatBot.set_remote_provider(remote_provider)
    chatBot.load()
    chatBot.custom_loop()
