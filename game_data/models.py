from django.db import models


class User(models.Model):

    class Meta:
        db_table = 'pubg_user'
        indexes = [
            models.Index(fields=['platform_user_name'], name='platform_user_name_uix')
        ]

    pubg_player_id = models.CharField(max_length=200, primary_key=True)
    platform_user_name = models.CharField(max_length=100, unique=True)
    first_name = models.CharField(max_length=32, null=True)
    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_updated = models.DateTimeField(auto_now=True)
    datetime_pubg_server_updated = models.DateTimeField(null=True)


class Match(models.Model):

    pubg_match_id = models.CharField(max_length=36, primary_key=True)
    map_name = models.CharField(max_length=36, null=True)
    duration = models.IntegerField(null=True)
    pubg_server_timestamp = models.DateTimeField(null=True)
    game_mode = models.CharField(max_length=10, null=True)


class PlayerStats(models.Model):

    class Meta:
        abstract = True

    pubg_match = models.ForeignKey(Match)
    knock_downs = models.IntegerField(null=True)
    assists = models.IntegerField(null=True)
    boosts = models.IntegerField(null=True)
    death_type = models.CharField(max_length=10)
    headshot_kills = models.IntegerField(null=True)
    heals = models.IntegerField(null=True)
    kill_place = models.IntegerField(null=True)
    kills = models.IntegerField(null=True)
    longest_kill = models.DecimalField(null=True, max_digits=10, decimal_places=2)
    revives = models.IntegerField(null=True)
    team_kills = models.IntegerField(null=True)
    time_survived = models.DecimalField(null=True, max_digits=10, decimal_places=2)
    weapons_acquired = models.IntegerField(null=True)
    win_place = models.IntegerField(null=True)
    roster_id = models.CharField(max_length=36, null=True)
    team_rank = models.IntegerField(null=True)
    won = models.NullBooleanField(null=True)


class UserStats(PlayerStats):

    CREATED = 'created'
    POPULATED = 'populated'
    SENT = 'sent'

    class Meta:
        db_table = 'user_pubg_matches'
        unique_together = (('pubg_player', 'pubg_match'),)
        indexes = [
            models.Index(fields=['pubg_match'], name='pubg_match_idx'),
            models.Index(fields=['status'], name='status_idx')
        ]

    pubg_player = models.ForeignKey(User)
    status = models.CharField(max_length=10, default=CREATED)


class ExtraPlayerStats(PlayerStats):

    class Meta:
        db_table = 'extra_player_pubg_matches'
        unique_together = (('player_name', 'pubg_match'),)
        indexes = [
            models.Index(fields=['pubg_match'], name='pubg_match_ep_idx'),
        ]

    player_name = models.CharField(max_length=64)
