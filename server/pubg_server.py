import logging
import requests
import os
import threading
from flask import Flask, request
from pubg_api_client.pubg_client import PubgClient
from game_data.services import player_data_service, match_data_service
from server.services import auth, slack_response_service

logger = logging.getLogger()
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(logging.BASIC_FORMAT))
handler.setLevel(logging.INFO)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

app = Flask(__name__)

client = PubgClient()


@app.route('/player', methods=['POST'])
def add_player_to_db():
    request_payload = request.get_json()
    gamertag = request_payload['gamertag']
    name = request_payload['name']

    player_json = client.get_players_info([gamertag], search_criteria='playerNames')
    account_id = player_json[0]['id']
    player_data_service.add_new_user(gamertag, account_id, name)
    return 'Successfully added player {}'.format(gamertag)


@app.route('/slack/event', methods=['POST'])
@auth.slack_auth_required
def deal_with_slack_event():
    request_payload = request.get_json()
    if request_payload.get('type') == 'url_verification':
        return slack_response_service.do_request_verification(request_payload)
    else:
        t = threading.Thread(target=post_response, args=(request_payload,))
        logger.info(request_payload)
        t.start()
        return '', 200


def post_response(request_payload):
    resp = slack_response_service.handle_event_response(**request_payload)
    headers = {'Authorization': 'Bearer {}'.format(os.environ.get('SLACK_BOT_TOKEN'))}
    logger.info(resp)
    my_resp = requests.post('https://slack.com/api/chat.postMessage', json=resp, headers=headers)
    logger.info('the response')
    logger.info(my_resp.json())
