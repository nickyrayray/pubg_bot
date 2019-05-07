import django
django.setup()
import logging
import schedule
import time
from pubg_api_client.pubg_client import PubgClient
from pubg_api_client.responses import player_response_service, match_response_service
from game_data.services import player_data_service, match_data_service

client = PubgClient()

logger = logging.getLogger()
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(logging.BASIC_FORMAT))
logger.addHandler(handler)
logger.setLevel(logging.INFO)


def find_and_send_matches():
    logger.info('Starting job to poll for new matches.')
    poll_and_update_player_data()
    populate_matches()


def poll_and_update_player_data():
    player_ids = player_data_service.get_player_ids()
    logger.info('Found %s players to lookup', len(player_ids))
    player_response = client.get_players_info(players=player_ids)
    player_match_dict = player_response_service.parse_player_data(player_response)
    for player_id, matches in player_match_dict.items():
        player_data_service.add_new_player_matches(player_id, matches)


def populate_matches():
    logger.info('Populating player matches found.')
    total_user_matches = []
    new_matches = match_data_service.get_matches_to_populate()
    logger.info('Found %s new matches to populate.', len(new_matches))
    for match_id, player_names in new_matches.items():
        match_response = client.get_match_details(match_id)
        match_data, rosters, player_dict = match_response_service.get_parsed_match_data(match_response, player_names)
        user_matches = match_data_service.enrich_user_matches(
            match_id=match_id,
            match_data=match_data,
            rosters=rosters,
            player_dict=player_dict
        )
        total_user_matches.append(user_matches)
    return total_user_matches


def post_matches():
    logger.info('Posting new matches to Slack.')
    user_matches_to_post = match_data_service.get_matches_to_post()


schedule.every(10).minutes.do(find_and_send_matches)

if __name__ == '__main__':
    while True:
        schedule.run_pending()
        time.sleep(10)
