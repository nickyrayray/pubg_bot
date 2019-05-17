from django.test import TestCase
from game_data.models import Match, UserStats, User
from game_data.services import match_data_service


class TestAddPlayerMatches(TestCase):

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

# from unittest import TestCase
#
# class TestPyTest(TestCase):
#
#     def test_test(self):
#         self.assertTrue(True)