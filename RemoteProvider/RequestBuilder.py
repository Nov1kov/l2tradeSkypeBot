# coding utf-8
import json

from RemoteProvider.ResponseStructure import Response


class RequestBuilder:
    def __init__(self):
        pass

    def get_new_messages_list(self, response_data: bytes) -> list:
        new_messages_list = []
        if response_data is not None and response_data != b'':
            data_decode_unicode = response_data.decode('utf-8')
            json_list = json.loads(data_decode_unicode)

            if isinstance(json_list, list):
                for json_dict in json_list:
                    if isinstance(json_dict, dict):
                        response = Response()
                        response.__dict__.update(json_dict)
                        new_messages_list.append(response)
        return new_messages_list
