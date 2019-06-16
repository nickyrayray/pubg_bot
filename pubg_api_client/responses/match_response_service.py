import json
from datetime import datetime
from functools import reduce
from pubg_api_client.responses.telemetry_response_service import Telemetry

pubg_server_timestring_format = '%Y-%m-%dT%H:%M:%S'


def get_parsed_match_data(match_json, player_names):
    match_data = _get_match_data(match_json)
    player_dict = _find_persons_json_by_name(match_json, player_names)
    rosters = _find_rosters(match_json, player_dict)
    extra_players = _find_extra_players_json_from_rosters(match_json, rosters)
    player_dict.update(extra_players)
    telemetry = _get_telemetry(match_json)
    return match_data, rosters, player_dict, telemetry


def _find_extra_players_json_from_rosters(match_json, rosters):
    extra_players = reduce(
        lambda x, y: x | y,
        (r['extra_players'] for r in rosters.values()),
        set()
    )
    if not extra_players:
        return {}
    return {p['id']: p['attributes']['stats'] for p in match_json['included']
            if p['type'] == 'participant' and
            p['id'] in extra_players}


def _find_persons_json_by_name(match_json, player_names):
    player_portion = [p for p in match_json['included']
                      if p['type'] == 'participant' and
                      p['attributes']['stats']['name'] in player_names]
    return {p['id']: p['attributes']['stats'] for p in player_portion}


def _find_rosters(match_json, players_dict):
    roster_jsons = [r for r in match_json['included'] if r['type'] == 'roster']
    rosters = {}
    for roster_json in roster_jsons:
        roster_entry = _build_roster_from_json(roster_json, players_dict.keys())
        if roster_entry:
            rosters.update(roster_entry)
    return rosters


def _build_roster_from_json(roster_json, player_ids):
    p_ids = {p['id'] for p in roster_json['relationships']['participants']['data']}
    player_ids_in_roster = set(player_ids) & p_ids

    if not player_ids_in_roster:
        return None

    return {
        roster_json['id']: {
            'players': player_ids_in_roster,
            'extra_players': p_ids - set(player_ids),
            'team_rank': int(roster_json['attributes']['stats']['rank']),
            'won': roster_json['attributes']['won'] == 'true'
        }
    }


def _get_match_data(match_json):
    attributes = match_json['data']['attributes']
    return {
        'map_name': _map_server_name_to_canonical_name(attributes['mapName']),
        'created_at': _server_timestring_to_datetime(attributes['createdAt']),
        'game_mode': attributes['gameMode'],
        'duration': attributes['duration']
    }


def _server_timestring_to_datetime(pubg_server_time_string):
    pubg_server_time_string = pubg_server_time_string[:-1]  # remove Z that python datetime can't handle
    dt = datetime.strptime(pubg_server_time_string, pubg_server_timestring_format)
    return dt


def _map_server_name_to_canonical_name(name):

    with open('/app/assets/mapNames.json') as f:
        server_name_to_canonical_name = json.loads(f.read())

    canonical_name = server_name_to_canonical_name.get(name, None)
    if not canonical_name:
        raise ValueError('Map name not found')
    else:
        return canonical_name


def _get_telemetry(match_json):
    assets_urls = [d['attributes']['URL'] for d in match_json['included']
                   if d['type'] == 'asset']
    if len(assets_urls) != 1:
        raise ValueError('Unexpected number of assets')

    return Telemetry(assets_urls[0])
