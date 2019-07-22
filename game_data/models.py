from django.db import models
from game_data.services import pubg_crypto


class UserLeague(models.Model):
    class Meta:
        db_table = 'pubg_user_league'
        indexes = [
            models.Index(fields=['pubg_league_name'], name='pubg_league_name_uix')
        ]

    pubg_league_name = models.CharField(max_length=255)
    pubg_api_key = models.TextField(max_length=255)

    def get_pubg_api_key(self):
        return pubg_crypto.decrypt(self.pubg_api_key)

    def set_pubg_api_key(self, unenc_key, save=False):
        self.pubg_api_key = pubg_crypto.encrypt(unenc_key)
        if save:
            self.save()


class User(models.Model):

    class Meta:
        db_table = 'pubg_user'
        indexes = [
            models.Index(fields=['platform_user_name'], name='platform_user_name_uix'),
            models.Index(fields=['pubg_user_league'], name='pubg_user_league_ix')
        ]

    pubg_user_league = models.ForeignKey(UserLeague, null=True, on_delete=models.SET_NULL)
    pubg_player_id = models.CharField(max_length=200, primary_key=True)
    platform_user_name = models.CharField(max_length=100, unique=True)
    first_name = models.CharField(max_length=32, null=True)
    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_updated = models.DateTimeField(auto_now=True)
    datetime_pubg_server_updated = models.DateTimeField(null=True)


class Match(models.Model):

    class Meta:
        db_table = 'pubg_matches'
        indexes = [
            models.Index(fields=['pubg_server_timestamp'], name='pubg_server_timestamp_idx'),
        ]

    pubg_match_id = models.CharField(max_length=64, primary_key=True)
    map_name = models.CharField(max_length=64, null=True)
    duration = models.IntegerField(null=True)
    pubg_server_timestamp = models.DateTimeField(null=True)
    game_mode = models.CharField(max_length=64, null=True)


class PlayerStats(models.Model):

    class Meta:
        abstract = True

    pubg_match = models.ForeignKey(Match, on_delete=models.DO_NOTHING)
    knock_downs = models.IntegerField(null=True)
    assists = models.IntegerField(null=True)
    boosts = models.IntegerField(null=True)
    death_type = models.CharField(max_length=64)
    damage_dealt = models.DecimalField(null=True, max_digits=10, decimal_places=2)
    headshot_kills = models.IntegerField(null=True)
    heals = models.IntegerField(null=True)
    kill_place = models.IntegerField(null=True)
    kills = models.IntegerField(null=True)
    longest_kill = models.DecimalField(null=True, max_digits=10, decimal_places=2)
    road_kills = models.IntegerField(null=True)
    revives = models.IntegerField(null=True)
    team_kills = models.IntegerField(null=True)
    time_survived = models.DecimalField(null=True, max_digits=10, decimal_places=2)
    walk_distance = models.DecimalField(null=True, max_digits=10, decimal_places=2)
    weapons_acquired = models.IntegerField(null=True)
    win_place = models.IntegerField(null=True)
    roster_id = models.CharField(max_length=36, null=True)
    team_rank = models.IntegerField(null=True)
    won = models.NullBooleanField(null=True)

    def get_identifier(self):
        raise NotImplementedError


class UserStats(PlayerStats):

    CREATED = 'created'
    POPULATED = 'populated'
    SENT = 'sent'
    SKIPPED = 'skipped'

    class Meta:
        db_table = 'user_match_data'
        unique_together = (('pubg_player', 'pubg_match'),)
        indexes = [
            models.Index(fields=['pubg_match'], name='pubg_match_idx'),
            models.Index(fields=['status'], name='status_idx')
        ]

    pubg_player = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    status = models.CharField(max_length=64, default=CREATED)

    def get_identifier(self):
        return self.pubg_player_id


class ExtraPlayerStats(PlayerStats):

    class Meta:
        db_table = 'extra_player_match_data'
        unique_together = (('player_name', 'pubg_match'),)
        indexes = [
            models.Index(fields=['pubg_match'], name='pubg_match_ep_idx'),
        ]

    player_name = models.CharField(max_length=64)

    def get_identifier(self):
        return self.player_name


class UserKills(models.Model):

    class Meta:
        db_table = 'user_kill_data'

    pubg_match = models.ForeignKey(Match, on_delete=models.DO_NOTHING)
    killer_id = models.CharField(max_length=64, db_index=True)
    killer_name = models.CharField(max_length=100)
    victim_id = models.CharField(max_length=200)
    victim_name = models.CharField(max_length=100)
    weapon = models.CharField(max_length=100)
    distance = models.DecimalField(null=True, max_digits=10, decimal_places=2)
    kill_timestamp = models.DateTimeField()
