import logging
from game_data.models import User, Match, UserStats


logger = logging.getLogger(__name__)


def get_users():
    return list(User.objects.all())


def get_player_ids():
    return list(User.objects.all().values_list('pubg_player_id', flat=True))


def add_new_player_matches(player_id, matches):
    _add_new_matches(matches)
    matches_to_add_for_player = _get_new_matches_for_user(player_id, matches)
    user_stats_to_create = [UserStats(pubg_player_id=player_id, pubg_match_id=match_id)
                            for match_id in matches_to_add_for_player]
    UserStats.objects.bulk_create(user_stats_to_create)


def add_new_user(gamertag, account_id, name):
    User.objects.create(
        pubg_player_id=account_id,
        platform_user_name=gamertag,
        first_name=name
    )


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
