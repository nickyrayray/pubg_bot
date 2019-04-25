import logging

logger = logging.getLogger(__name__)


def parse_player_data(players_data):
    player_matches_dict = {}

    for player_data in players_data:
        player_id, matches = _get_matches_for_single_payer(player_data)
        player_matches_dict[player_id] = matches

    return player_matches_dict


def _get_matches_for_single_payer(player_data):
    player_id = player_data['id']
    match_json_array = player_data['relationships']['matches']['data']
    matches = [match_obj['id'] for match_obj in match_json_array]
    player_name = player_data['attributes']['name']
    logger.info('Found %s matches for %s', len(matches), player_name)
    return player_id, matches