import argparse
import django
django.setup()
import logging
import schedule
import time
from pubg_api_client.pubg_client import PubgClient
from pubg_api_client.responses import player_response_service, match_response_service
from game_data.services import player_data_service, match_data_service
from slack_api_client.slack_client import SlackClient


logger = logging.getLogger()
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(logging.BASIC_FORMAT))
handler.setLevel(logging.INFO)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


def find_and_send_matches(slack_webhook_id=None):
    pubg_client = PubgClient()
    slack_client = SlackClient(webhook_identifier=slack_webhook_id)
    logger.info('Starting job to poll for new matches.')
    poll_and_update_player_data(pubg_client)
    populate_matches(pubg_client)
    post_matches(slack_client)


def poll_and_update_player_data(pubg_client):
    player_ids = player_data_service.get_player_ids()
    logger.info('Found %s players to lookup', len(player_ids))
    player_response = pubg_client.get_players_info(players=player_ids)
    player_match_dict = player_response_service.parse_player_data(player_response)
    match_data_service.add_new_player_matches(player_match_dict)


def populate_matches(pubg_client):
    logger.info('Populating player matches found.')
    total_user_matches = []
    new_matches = match_data_service.get_matches_to_populate()
    logger.info('Found %s new matches to populate.', len(new_matches))
    for match_id, player_names in new_matches.items():
        match_response = pubg_client.get_match_details(match_id)
        match_data, rosters, player_dict = match_response_service.get_parsed_match_data(match_response, player_names)
        user_matches = match_data_service.enrich_user_matches(
            match_id=match_id,
            match_data=match_data,
            rosters=rosters,
            player_dict=player_dict
        )
        total_user_matches.append(user_matches)
    return total_user_matches


def post_matches(slack_client):
    logger.info('Posting new matches to Slack.')
    match_ids_to_post = match_data_service.get_matches_to_post()
    for match_id in match_ids_to_post:
        slack_client.post_match(match_id)
        match_data_service.set_matches_to_completed(match_id)
        time.sleep(10)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='App to poll and send pubg matches')
    parser.add_argument('--slack_webhook_path', help='optional slack webhook path to override env variable value')
    args = parser.parse_args()
    logger.info('using %s as webhook path', args.slack_webhook_path)
    schedule.every(10).minutes.do(find_and_send_matches, slack_webhook_id=args.slack_webhook_path)
    while True:
        schedule.run_pending()
        time.sleep(30)
