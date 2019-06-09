import logging
from game_data.models import User


logger = logging.getLogger(__name__)


def get_users():
    return list(User.objects.all())


def get_player_ids():
    return list(User.objects.all().values_list('pubg_player_id', flat=True))


def add_new_user(gamertag, account_id, name):
    User.objects.create(
        pubg_player_id=account_id,
        platform_user_name=gamertag,
        first_name=name
    )


def get_user_by_name(username_or_name):
    pass
