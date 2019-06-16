import logging
from game_data.models import UserKills

logger = logging.getLogger(__name__)


def add_user_kills(user_matches, telemetry):
    for user_match in user_matches:
        if user_match.kills > 0:
            add_kill_events(telemetry, user_match)
        else:
            logger.info('%s had no kills this match. No need to log telemetry.', user_match.get_identifier())


def add_kill_events(telemetry, user_match):
    logger.info('%s had %s kills. Logging kill events', user_match.get_identifier(), user_match.kills)
    kills = telemetry.get_kills_for(user_match.get_identifier())
    for kill in kills:
        UserKills.objects.create(
            pubg_match_id=user_match.pubg_match_id,
            killer_id=kill['killer_id'],
            killer_name=kill['killer_name'],
            victim_id=kill['victim_id'],
            victim_name=kill['victim_name'],
            weapon=kill['weapon'],
            kill_timestamp=kill['kill_timestamp'],
            distance=kill['distance'],
        )


def get_user_kills(match_id, name_or_id):
    kills = UserKills.objects.filter(
        pubg_match_id=match_id,
        killer_id=name_or_id
    )
    if not kills.exists():
        kills = UserKills.objects.filter(
            pubg_match_id=match_id,
            killer_name=name_or_id
        )
    return kills
