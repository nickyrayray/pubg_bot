from flask import Flask, request
from api_client.pubg_client import PubgClient
from api_client.responses import player_response_service, match_response_service
from data_access.services import player_data_service, match_data_service


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


def poll_and_update_player_data():
    player_ids = player_data_service.get_player_ids()
    player_response = client.get_players_info(players=player_ids)
    player_match_dict = player_response_service.parse_player_data(player_response)
    for player_id, matches in player_match_dict.items():
        player_data_service.add_new_player_matches(player_id, matches)


def populate_matches():
    total_user_matches = []
    new_matches = match_data_service.get_matches_to_populate()
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


