import os
import requests
import json
from pubg_api_client.constants import *


class PubgClient(object):

    def __init__(self, platform='xbox', api_key=None):
        self.api_key = api_key
        self.base_url = PUBG_DOMAIN.format(platform=platform)
        self.headers = {
            "Authorization": "Bearer {}".format(self._get_api_key()),
            "Accept": "application/vnd.api+json"
        }

    def get_lifetime_stats(self, account_id):
        rel_path = LIFETIME_STATS_ENDPOINT.format(account_id=account_id)
        resp = self._make_request(rel_path)
        lifetime_stats = json.loads(resp.content)
        return lifetime_stats

    def get_match_details(self, match_id):
        rel_path = MATCHES_ENDPOINT.format(match_id=match_id)
        resp = self._make_request(rel_path)
        match_details = json.loads(resp.content)
        return match_details

    def get_players_info(self, players, search_criteria='playerIds'):
        rel_path = PLAYER_ENDPOINT
        params = {
            'filter[{}]'.format(search_criteria): ','.join(players)
        }
        resp = self._make_request(rel_path, params=params)
        player_details = json.loads(resp.content)
        return player_details['data']

    def _make_request(self, rel_path, params=None):
        url = self.base_url + rel_path
        return requests.get(
            url,
            headers=self.headers,
            params=params
        )

    def _get_api_key(self):
        if not self.api_key:
            environ_key = os.environ.get('PUBG_API_KEY')
            if environ_key:
                return environ_key
            with open('credentials/api_key', 'r') as f:
                return f.read()
        return self.api_key