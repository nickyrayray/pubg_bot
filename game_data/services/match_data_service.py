from decimal import Decimal
from game_data.models import UserStats, ExtraPlayerStats, Match


def add_new_player_matches(player_match_dict):
    for player_id, matches in player_match_dict.items():
        _add_new_matches(matches)
        matches_to_add_for_player = _get_new_matches_for_user(player_id, matches)
        user_stats_to_create = [UserStats(pubg_player_id=player_id, pubg_match_id=match_id)
                                for match_id in matches_to_add_for_player]
        UserStats.objects.bulk_create(user_stats_to_create)


def _add_new_matches(matches):
    existing_matches = set(Match.objects.filter(
        pubg_match_id__in=matches,
    ).values_list('pubg_match_id', flat=True))

    new_matches = set(matches) - existing_matches

    matches_to_add = [Match(pubg_match_id=match) for match in new_matches]

    Match.objects.bulk_create(matches_to_add)


def _get_new_matches_for_user(player_id, matches):
    existing_matches_with_user_stats = set(UserStats.objects.filter(
        pubg_player_id=player_id,
        pubg_match_id__in=matches
    ).values_list('pubg_match_id', flat=True))

    new_matches = set(matches) - existing_matches_with_user_stats

    return new_matches


def get_matches_to_populate():
    user_matches = UserStats.objects.filter(
        status=UserStats.CREATED
    ).select_related('pubg_player')
    match_dict = {}
    for user_match in user_matches:
        match_id = user_match.pubg_match_id
        if match_id in match_dict:
            match_dict[match_id].append(user_match.pubg_player.platform_user_name)
        else:
            match_dict[match_id] = [user_match.pubg_player.platform_user_name]
    return match_dict


def get_matches_to_post():
    user_matches = UserStats.objects.filter(
        status=UserStats.POPULATED
    ).values_list('pubg_match_id', flat=True)
    return set(user_matches)


def enrich_user_matches(match_id, match_data, rosters, player_dict):
    user_matches = []
    extra_player_matches = []
    populate_match_with_match_data(match_id, match_data)
    for roster_id, roster in rosters.items():
        for player_id in roster['players']:
            player_json = player_dict[player_id]
            print(player_json)
            user_match = _enrich_user_match(
                match_id=match_id,
                roster_id=roster_id,
                roster_info=roster,
                player_json=player_json
            )
            user_matches.append(user_match)
        for extra_player_id in roster['extra_players']:
            player_json = player_dict[extra_player_id]
            extra_player_match = _create_extra_player_match(
                match_id=match_id,
                roster_id=roster_id,
                roster_info=roster,
                player_json=player_json
            )
            extra_player_matches.append(extra_player_match)

    return user_matches, extra_player_matches


def _enrich_user_match(match_id, roster_id, roster_info, player_json):
    player_id = player_json['playerId']
    user_match = UserStats.objects.get(
        pubg_match_id=match_id,
        pubg_player_id=player_id
    )
    _update_match_with_roster_info(user_match, roster_id, roster_info)
    _update_match_with_player_data(user_match, player_json)
    user_match.status = UserStats.POPULATED
    user_match.save()
    return user_match


def _create_extra_player_match(match_id, roster_id, roster_info, player_json):
    player_name = player_json['name']
    extra_player_match = ExtraPlayerStats.objects.create(
        pubg_match_id=match_id,
        player_name=player_name
    )
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
    user_match.road_kills = int(player_json['roadKills'])
    user_match.revives = int(player_json['revives'])
    user_match.team_kills = int(player_json['teamKills'])
    user_match.time_survived = Decimal(player_json['timeSurvived'])
    user_match.walk_distance = Decimal(player_json['walkDistance'])
    user_match.weapons_acquired = int(player_json['weaponsAcquired'])
    user_match.win_place = int(player_json['winPlace'])


def _update_match_with_roster_info(user_match, roster_id, roster_info):
    user_match.roster_id = roster_id
    user_match.team_rank = roster_info['team_rank']
    user_match.won = roster_info['won']


def populate_match_with_match_data(match_id, match_data):
    print(match_data)
    Match.objects.filter(
        pubg_match_id=match_id
    ).update(
        pubg_server_timestamp=match_data['created_at'],
        game_mode=match_data['game_mode'],
        duration=match_data['duration'],
        map_name=match_data['map_name'],
    )


def set_matches_to_completed(match_id):
    UserStats.objects.filter(
        pubg_match_id=match_id
    ).update(status=UserStats.SENT)


def get_match(match_id):
    return Match.objects.get(pubg_match_id=match_id)


def get_player_stats_for_match(match_id):
    return list(UserStats.objects.filter(pubg_match_id=match_id))


def get_extra_player_stats_for_match(match_id):
    return list(ExtraPlayerStats.objects.filter(
        pubg_match_id=match_id
    ))
