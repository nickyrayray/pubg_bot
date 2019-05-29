from django.test import TestCase
from game_data.models import Match, UserStats, User
from game_data.services import match_data_service


class TestAddPlayerMatchesMatchData(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            pubg_player_id='test_account_1',
            platform_user_name='test_account',
            first_name='Test'
        )

    def test_add_player_matches_creates_matches(self):
        payload = {
            self.user.pubg_player_id: ['match_1', 'match_2']
        }

        match_data_service.add_new_player_matches(payload)

        matches = Match.objects.all()
        self.assertEquals(matches.count(), 2)

    def test_add_player_matches_ignores_repeat_matches(self):
        payload = {
            self.user.pubg_player_id: ['match_1', 'match_2']
        }
        match_data_service.add_new_player_matches(payload)
        payload[self.user.pubg_player_id].append('match_3')
        match_data_service.add_new_player_matches(payload)

        match_ids = Match.objects.all().values_list('pubg_match_id', flat=True)
        self.assertEquals(match_ids.count(), 3)
        self.assertEquals(set(payload[self.user.pubg_player_id]), set(match_ids))

    def test_add_player_matches_ignores_repeat_matches_from_other_players(self):
        other_user = User.objects.create(
            pubg_player_id='test_account_2',
            platform_user_name='other_test_account',
            first_name='Test2'
        )
        payload = {
            self.user.pubg_player_id: ['match_1', 'match_2', 'match_3'],
            other_user.pubg_player_id: ['match_1', 'match_3', 'match_4'],
        }

        match_data_service.add_new_player_matches(payload)

        match_ids = Match.objects.all().values_list('pubg_match_id', flat=True)
        self.assertEquals(match_ids.count(), 4)
        self.assertEquals({'match_1', 'match_2', 'match_3', 'match_4'}, set(match_ids))

    def test_add_player_matches_creates_user_stats(self):
        payload = {
            self.user.pubg_player_id: ['match_1', 'match_2']
        }

        match_data_service.add_new_player_matches(payload)

        user_stats = UserStats.objects.all()
        self.assertEquals(user_stats.count(), 2)

    def test_add_player_matches_creates_user_stats_ignoring_repeats(self):
        payload = {
            self.user.pubg_player_id: ['match_1', 'match_2']
        }
        match_data_service.add_new_player_matches(payload)
        payload[self.user.pubg_player_id].append('match_3')
        match_data_service.add_new_player_matches(payload)

        user_stats_match_ids = UserStats.objects.all().values_list('pubg_match_id', flat=True)
        self.assertEquals(user_stats_match_ids.count(), 3)
        self.assertEquals(set(payload[self.user.pubg_player_id]), set(user_stats_match_ids))

    def test_add_player_matches_creates_user_stats_ignoring_repeats(self):
        payload = {
            self.user.pubg_player_id: ['match_1', 'match_2']
        }
        match_data_service.add_new_player_matches(payload)
        payload[self.user.pubg_player_id].append('match_3')
        match_data_service.add_new_player_matches(payload)

        user_stats_match_ids = UserStats.objects.all().values_list('pubg_match_id', flat=True)
        self.assertEquals(user_stats_match_ids.count(), 3)
        self.assertEquals(set(payload[self.user.pubg_player_id]), set(user_stats_match_ids))

    def test_empty_payload_is_a_noop(self):
        payload = {}

        match_data_service.add_new_player_matches(payload)

        self.assertEquals(Match.objects.all().count(), 0)
        self.assertEquals(UserStats.objects.all().count(), 0)

