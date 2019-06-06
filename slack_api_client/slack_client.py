import os
import logging
import requests
from slack_api_client.slack_message import SlackMessage

logger = logging.getLogger(__name__)

SLACK_WEBHOOK_BASE_TEMPLATE = 'https://hooks.slack.com/services/{}'


class SlackClient(object):

    def __init__(self, webhook_identifier=None):
        if not webhook_identifier:
            webhook_identifier = os.environ.get('SLACK_WEBHOOK_PATH')
        self.webhook_path = SLACK_WEBHOOK_BASE_TEMPLATE.format(webhook_identifier)

    def post_match(self, match_id):
        slack_message = SlackMessage(match_id)
        message_payload = slack_message.to_message_json()
        logger.info('Sending message payload: %s', message_payload)
        return requests.post(self.webhook_path, json=message_payload)

