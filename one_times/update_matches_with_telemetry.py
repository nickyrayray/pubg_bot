import argparse
import logging
from pubg_api_client.pubg_client import PubgClient
from pubg_api_client.responses import match_response_service
from game_data.models import *
from game_data.services import telemetry_data_service

logger = logging.getLogger(__name__)


def main(noop=False):
    all_match_ids = get_all_match_ids()
    logger.info('Stored results from %s matches', len(all_match_ids))
    match_ids_with_kill_data = get_match_ids_with_kill_data()
    logger.info('%s match ids have kill data', len(match_ids_with_kill_data))
    match_ids_to_search = all_match_ids - match_ids_with_kill_data
    for match_id in match_ids_to_search:
        populate_user_kills_for_match(match_id, noop)


def populate_user_kills_for_match(match_id, noop=False):
    match_json = get_match_data_if_exists(match_id)
    if not match_json:
        logger.info('Could not find match json for match %s. Skipping...', match_id)
        return
    telemetry = match_response_service._get_telemetry(match_json)
    user_matches = get_user_matches(match_id)
    ep_matches = get_ep_matches(match_id)
    if noop:
        logger.info('For match %s there are %s user matches and %s ep matches with kill data',
                    match_id,
                    user_matches.filter(kills__gt=0).count(),
                    ep_matches.filter(kills__gt=0).count())
        logger.info('For match %s, %s rows will be created.',
                    match_id,
                    sum(user_match.kills for user_match in user_matches) + sum(ep_match.kills for ep_match in ep_matches))
    else:
        telemetry_data_service.add_user_kills(user_matches, telemetry)
        telemetry_data_service.add_user_kills(ep_matches, telemetry)


def get_all_match_ids():
    match_ids = Match.objects.all().values_list('pubg_match_id', flat=True)
    return set(match_ids)


def get_match_ids_with_kill_data():
    match_ids = UserKills.objects.all().values_list('pubg_match_id', flat=True)
    return set(match_ids)


def get_match_data_if_exists(match_id):
    client = PubgClient()
    try:
        return client.get_match_details(match_id)
    except:
        logger.exception('Failed to get match data')
        return None


def get_user_matches(match_id):
    return UserStats.objects.filter(
        pubg_match_id=match_id,
    )


def get_ep_matches(match_id):
    return ExtraPlayerStats.objects.filter(
        pubg_match_id=match_id,
    )


def setup_logger():
    root = logging.getLogger()
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(logging.BASIC_FORMAT))
    root.addHandler(handler)


if __name__ == '__main__':
    setup_logger()
    parser = argparse.ArgumentParser(description='Backfill script to populate match kill data for existing matches')
    parser.add_argument('--noop', help='if true, print stats rather than perform actual updates', action='store_true')
    args = parser.parse_args()
    main(args.noop)
