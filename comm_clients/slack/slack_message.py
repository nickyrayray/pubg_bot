import calendar
from decimal import Decimal
from game_data.services import match_data_service, telemetry_data_service


class SlackMessage(object):

    PREVIEW_TEXT = 'Pubg match completed'
    MATCH_TEXT_TEMPLATE = "*{game_mode}* match completed on *{map_name}* on `{pubg_timestamp}`"
    INDIVIDUAL_TEXT_TEMPLATE = "*{name}* ranked {win_place}, got {kills} kills, {knocks} knocks, {assists} assists, " \
                               "revived {revives} teammates, did {damage} points of damage, " \
                               "used {boosts} stims, and used {heals} healing items. "
    KILL_DETAIL_TEMPLATE = 'They got {h_kills} headshot kills. Their longest kill was {kill_meters} meters ' \
                           'away. They killed {team_kills} teammates. Their kill place was {kill_place}. '
    SURVIVE_TEMPLATE = 'They survived {time_survived}, or {survival_percentage:.2f}% of the match.'
    WIN_PHRASE = '*WINNER WINNER CHICKEN DINNER!!*'
    TOP_TEN_PHRASE = 'Made the top 10!'
    LOST_PHRASE = 'You bad!'
    TEAM_TEMPLATE = 'Team of {names} ranked {team_rank}! {phrase}'
    SLACK_TIMESTAMP_TEMPLATE = '<!date^{timestamp}^{date} at {time_secs}|{unformatted} UTC>'
    KILL_ENUM_TEMPLATE = 'Killed `{name}` with a *{weapon}* from `{distance:.2f}` meters away.'

    def __init__(self, match_id):
        self.match = match_data_service.get_match(match_id)
        user_stats = match_data_service.get_player_stats_for_match(match_id)
        extra_player_stats = match_data_service.get_extra_player_stats_for_match(match_id)
        self.rosters = {}
        for stats in user_stats + extra_player_stats:
            if stats.roster_id in self.rosters:
                self.rosters[stats.roster_id].append(stats)
            else:
                self.rosters[stats.roster_id] = [stats]

    def to_message_json(self):
        blocks = []
        match_block = self._build_match_block()
        blocks.append(match_block)
        blocks += self._build_team_blocks()
        blocks.append(self._build_match_id_context_block())
        blocks.append(self._divider())
        return {
            'text': self.PREVIEW_TEXT,
            'blocks': blocks
        }

    def _build_match_block(self):
        match_text = self._get_match_text()
        return {
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': match_text
            }
        }

    def _get_match_text(self):
        text = self.MATCH_TEXT_TEMPLATE.format(
            game_mode=self.match.game_mode.capitalize(),
            map_name=self.match.map_name,
            pubg_timestamp=self._datetime_to_slack_formatting(self.match.pubg_server_timestamp)
        )
        return text

    def _build_team_blocks(self):
        blocks = []
        for roster_id, user_matches in self.rosters.items():
            blocks.append(self._build_team_stats_block(user_matches))
            for user_match in user_matches:
                blocks.append(self._build_individual_stats_block(user_match))
        return blocks

    def _build_team_stats_block(self, user_matches):
        team_names = [self._get_name_from_match_data(user_match) for user_match in user_matches]
        team_rank = user_matches[0].team_rank
        if team_rank == 1:
            phrase = self.WIN_PHRASE
        elif team_rank <= 10:
            phrase = self.TOP_TEN_PHRASE
        else:
            phrase = self.LOST_PHRASE
        text = self.TEAM_TEMPLATE.format(
            names=', '.join(['`{}`'.format(name) for name in team_names]),
            team_rank=team_rank,
            phrase=phrase
        )
        return {
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': text
            }
        }

    def _build_individual_stats_block(self, user_data):
        stats_text = self._build_individual_stats_text(user_data)
        return {
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': stats_text
            }
        }

    def _build_individual_stats_text(self, user_data):
        time_survived_string = self._stringify_time_survived(user_data.time_survived)
        percent_time_survived = self._get_percentage_of_time_survived(user_data.time_survived)
        kill_text = None
        text = self.INDIVIDUAL_TEXT_TEMPLATE.format(
            name=self._get_name_from_match_data(user_data),
            win_place=user_data.win_place,
            kills=user_data.kills + user_data.team_kills,
            knocks=user_data.knock_downs,
            assists=user_data.assists,
            revives=user_data.revives,
            heals=user_data.heals,
            boosts=user_data.boosts,
            damage=user_data.damage_dealt,
        )
        if user_data.kills + user_data.team_kills > 0:
            text += self.KILL_DETAIL_TEMPLATE.format(
                h_kills=user_data.headshot_kills,
                kill_meters=user_data.longest_kill,
                team_kills=user_data.team_kills,
                kill_place=user_data.kill_place
            )
            kill_details = telemetry_data_service.get_user_kills(user_data.pubg_match_id, user_data.get_identifier())
            kill_text = '\n'.join([self.KILL_ENUM_TEMPLATE.format(
                name=kill.victim_name,
                distance=kill.distance / Decimal(100.0),
                weapon=kill.weapon,
            ) for kill in kill_details])
        text += self.SURVIVE_TEMPLATE.format(
            time_survived=time_survived_string,
            survival_percentage=percent_time_survived
        )
        if kill_text:
            text += '\n' + kill_text
        return text

    def _build_match_id_context_block(self):
        return {
            'type': 'context',
            'elements': [
                {
                    "type": "mrkdwn",
                    "text": "Match Id: {}".format(self.match.pubg_match_id)
                }
            ]
        }

    @staticmethod
    def _divider():
        return {
            'type': 'divider'
        }

    @staticmethod
    def _get_name_from_match_data(user_data):
        return user_data.pubg_player.platform_user_name if hasattr(user_data, 'pubg_player') else user_data.player_name

    @staticmethod
    def _stringify_time_survived(time_survived):
        minutes = int(time_survived / 60)
        seconds = time_survived % 60
        return "{minutes} minutes, {seconds} seconds".format(
            minutes=minutes,
            seconds=seconds
        )

    def _get_percentage_of_time_survived(self, time_survived):
        match_time = self.match.duration
        return (time_survived/Decimal(match_time)) * 100

    def _datetime_to_slack_formatting(self, dt):
        unix_timestamp = calendar.timegm(dt.timetuple())
        return self.SLACK_TIMESTAMP_TEMPLATE.format(
            timestamp=int(unix_timestamp),
            date='{date}',
            time_secs='{time_secs}',
            unformatted=dt.strftime('%m-%d-%Y %H:%M:%S')
        )
