from .constants import *


class CommunicationClient(object):

    def __init__(self, address_info):
        self.address_info = address_info

    def build_message(self, match_id):
        raise NotImplementedError

    def send_message(self):
        raise NotImplementedError

    @staticmethod
    def get_communications_client(comm_type):
        if comm_type == SLACK_TYPE:
            pass
        elif comm_type == EMAIL_TYPE:
            pass
