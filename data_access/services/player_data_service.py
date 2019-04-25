import logging
from data_access.models import User, UserMatch, ExtraPlayerMatch


logger = logging.getLogger(__name__)


def get_users():
    return list(User.objects.all())


def get_player_ids():
    return list(User.objects.all().values_list('pubg_player_id', flat=True))


def add_new_player_matches(player_id, matches):
    new_matches = _get_new_matches(player_id, matches)
    new_player_match_objects = []
    for match in new_matches:
        user_match = UserMatch(pubg_match_id=match, pubg_player_id=player_id)
        new_player_match_objects.append(user_match)

    UserMatch.objects.bulk_create(new_player_match_objects)


def add_new_user(gamertag, account_id, name):
    User.objects.create(
        pubg_player_id=account_id,
        platform_user_name=gamertag,
        first_name=name
    )


def _get_new_matches(player_id, matches):
    existing_matches = set(UserMatch.objects.filter(
        pubg_match_id__in=matches,
        pubg_player_id=player_id
    ).values_list('pubg_match_id', flat=True))

    new_matches = set(matches) - existing_matches

    logger.info('For player %s, found %s new matches', len(new_matches))

    return new_matches
