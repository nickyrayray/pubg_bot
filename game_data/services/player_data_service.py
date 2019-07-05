import logging
from game_data.models import User, UserLeague


logger = logging.getLogger(__name__)


def get_user_leagues():
    return list(UserLeague.objects.all())


def get_users():
    return list(User.objects.all())


def get_player_ids_for_league(league_id):
    return list(User.objects.filter(pubg_user_league_id=league_id).values_list('pubg_player_id', flat=True))


def add_new_user(gamertag, account_id, name):
    User.objects.create(
        pubg_player_id=account_id,
        platform_user_name=gamertag,
        first_name=name
    )
