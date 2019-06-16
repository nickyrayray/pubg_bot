import logging
import json
import requests
from datetime import datetime

pubg_server_timestring_format = '%Y-%m-%dT%H:%M:%S.%f'

logger = logging.getLogger(__name__)


class Telemetry(object):

    def __init__(self, url):
        self.url = url
        self.kill_events = []
        self.dbno_events = []
        self.ASSETS = {}

    def get_kills_for(self, name_or_id):
        self._load_events()
        kill_events = [k for k in self.kill_events if k['killer'] and
                       (k['killer']['accountId'] == name_or_id or k['killer']['name'] == name_or_id)]
        return [{
            'killer_id': k['killer']['accountId'],
            'killer_name': k['killer']['name'],
            'victim_id': k['victim']['accountId'],
            'victim_name': k['victim']['name'],
            'weapon': self.get_weapon_name(k),
            'kill_timestamp': self._server_timestring_to_datetime(k['_D']),
            'distance': k['distance']
        } for k in kill_events]

    def get_weapon_name(self, k):
        self._load_assets()
        dbno = self._check_for_associated_dbno(k['attackId'])
        weapon_code = k['damageCauserName']
        if dbno:
            weapon_code = self._get_real_weapon_code_and_check_event_consistency(k, dbno)
        try:
            return self.ASSETS[weapon_code]
        except KeyError:
            return weapon_code

    @staticmethod
    def _get_real_weapon_code_and_check_event_consistency(k, dbno):
        kill_weapon_code = k['damageCauserName']
        dbno_weapon_code = dbno['damageCauserName']
        killer_name = k['killer']['name']
        attacker_name = dbno['attacker']['name']
        if killer_name != attacker_name:
            logger.info('NAME MISMATCH: killer name %s, attacker name %s', killer_name, attacker_name)
        if kill_weapon_code != dbno_weapon_code:
            logger.info('WEAPON MISMATCH: killer weapon %s, attacker weapon %s', kill_weapon_code, dbno_weapon_code)
        return dbno_weapon_code

    def _check_for_associated_dbno(self, attack_id):
        dbnos = [dbno for dbno in self.dbno_events if dbno['attackId'] == attack_id]
        if len(dbnos) == 1:
            return dbnos[0]
        else:
            logger.info('No associated DBNO for kill. Defaulting to kill event for weapon.')
            return None

    def _load_assets(self):
        if not self.ASSETS:
            with open('/app/assets/damageCauserName.json') as f:
                self.ASSETS = json.loads(f.read())

    @staticmethod
    def _server_timestring_to_datetime(pubg_server_time_string):
        pubg_server_time_string = pubg_server_time_string[:-1]  # remove Z that python datetime can't handle
        dt = datetime.strptime(pubg_server_time_string, pubg_server_timestring_format)
        return dt

    def _load_events(self):
        if not self.kill_events:
            resp = requests.get(self.url).json()
            self.kill_events = [e for e in resp if e['_T'] == 'LogPlayerKill']
            self.dbno_events = [e for e in resp if e['_T'] == 'LogPlayerMakeGroggy']