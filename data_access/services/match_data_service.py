from decimal import Decimal
from data_access.models import UserMatch, ExtraPlayerMatch


def get_matches_to_populate():
    user_matches = UserMatch.objects.filter(
        status=UserMatch.CREATED
    ).select_related('pubg_player')
    match_dict = {}
    for user_match in user_matches:
        match_id = user_match.pubg_match_id
        if match_id in match_dict:
            match_dict[match_id].append(user_match.pubg_player.platform_user_name)
        else:
            match_dict[match_id] = [user_match.pubg_player.platform_user_name]
    return match_dict


def enrich_user_matches(match_id, match_data, rosters, player_dict):
    user_matches = []
    extra_player_matches = []
    for roster_id, roster in rosters.items():
        for player_id in roster['players']:
            player_json = player_dict[player_id]
            print(player_json)
            user_match = _enrich_user_match(
                match_id=match_id,
                match_data=match_data,
                roster_id=roster_id,
                roster_info=roster,
                player_json=player_json
            )
            user_matches.append(user_match)
        for extra_player_id in roster['extra_players']:
            player_json = player_dict[extra_player_id]
            print(player_json)
            extra_player_match = _create_extra_player_match(
                match_id=match_id,
                match_data=match_data,
                roster_id=roster_id,
                roster_info=roster,
                player_json=player_json
            )
            extra_player_matches.append(extra_player_match)

    return user_matches, extra_player_matches


def _enrich_user_match(match_id, match_data, roster_id, roster_info, player_json):
    player_id = player_json['playerId']
    user_match = UserMatch.objects.get(
        pubg_match_id=match_id,
        pubg_player_id=player_id
    )
    _update_match_with_match_data(user_match, match_data)
    _update_match_with_roster_info(user_match, roster_id, roster_info)
    _update_match_with_player_data(user_match, player_json)
    user_match.status = UserMatch.POPULATED
    user_match.save()
    return user_match


def _create_extra_player_match(match_id, match_data, roster_id, roster_info, player_json):
    player_name = player_json['name']
    extra_player_match = ExtraPlayerMatch.objects.create(
        pubg_match_id=match_id,
        player_name=player_name
    )
    _update_match_with_match_data(extra_player_match, match_data)
    _update_match_with_roster_info(extra_player_match, roster_id, roster_info)
    _update_match_with_player_data(extra_player_match, player_json)
    extra_player_match.save()
    return extra_player_match


def _update_match_with_player_data(user_match, player_json):
    user_match.knock_downs = int(player_json['DBNOs'])
    user_match.assists = int(player_json['assists'])
    user_match.boosts = int(player_json['boosts'])
    user_match.death_type = player_json['deathType']
    user_match.headshot_kills = int(player_json['headshotKills'])
    user_match.heals = int(player_json['heals'])
    user_match.kill_place = int(player_json['killPlace'])
    user_match.kills = int(player_json['kills'])
    user_match.longest_kill = Decimal(player_json['longestKill'])
    user_match.revives = int(player_json['revives'])
    user_match.team_kills = int(player_json['teamKills'])
    user_match.time_survived = Decimal(player_json['timeSurvived'])
    user_match.weapons_acquired = int(player_json['weaponsAcquired'])
    user_match.win_place = int(player_json['winPlace'])


def _update_match_with_roster_info(user_match, roster_id, roster_info):
    user_match.roster_id = roster_id
    user_match.team_rank = roster_info['team_rank']
    user_match.won = roster_info['won']


def _update_match_with_match_data(user_match, match_data):
    user_match.pubg_server_timestamp = match_data['created_at']
    user_match.game_mode = match_data['game_mode']
    user_match.duration = match_data['duration']
    user_match.map_name = match_data['map_name']

