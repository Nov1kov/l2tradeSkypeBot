# coding utf-8
from datetime import date
import time

from skpy import SkypeUtils


def quote(message_text, quote_user_id, quote_user_name, quote_datetime_timestamp, quote_chat_name):
    """
    Display a message excerpt as a quote from another user.
    Returns:
        str: tag to display the excerpt as a quote
    """

    if message_text == '':
        return ''

    # Single conversations lose their prefix here.
    chat_id = quote_chat_name if quote_chat_name.split(":")[0] == "19" else SkypeUtils.noPrefix(quote_chat_name)
    # Legacy timestamp includes the date if the quote is not from today.
    unixTime = int(time.mktime(quote_datetime_timestamp.timetuple()))
    legacyTime = quote_datetime_timestamp.strftime("{0}%H:%M:%S".
                                                   format(
        "" if quote_datetime_timestamp.date() == date.today() else "%d/%m/%Y "))
    return """<quote author="{0}" authorname="{1}" conversation="{2}" timestamp="{3}"><legacyquote>""" \
           """[{4}] {1}: </legacyquote>{5}<legacyquote>\n\n&lt;&lt;&lt; </legacyquote></quote>""" \
        .format(quote_user_id, quote_user_name, chat_id, unixTime, legacyTime, message_text)
