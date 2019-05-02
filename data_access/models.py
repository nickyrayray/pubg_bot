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

    class Meta:
        abstract = True

    pubg_match_id = models.CharField(max_length=36)
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
    map_name = models.CharField(max_length=36, null=True)
    duration = models.IntegerField(null=True)
    pubg_server_timestamp = models.DateTimeField(null=True)
    game_mode = models.CharField(max_length=10, null=True)
    team_rank = models.IntegerField(null=True)
    won = models.NullBooleanField(null=True)


class UserMatch(Match):

    CREATED = 'created'
    POPULATED = 'populated'
    SENT = 'sent'

    class Meta:
        db_table = 'user_pubg_matches'
        unique_together = (('pubg_player', 'pubg_match_id'),)
        indexes = [
            models.Index(fields=['pubg_match_id'], name='pubg_match_id_idx'),
            models.Index(fields=['status'], name='status_idx')
        ]
        index_together = [
            ["pubg_server_timestamp", "status"],
        ]

    pubg_player = models.ForeignKey(User)
    status = models.CharField(max_length=10, default=CREATED)


class ExtraPlayerMatch(Match):

    class Meta:
        db_table = 'extra_player_pubg_matches'
        unique_together = (('player_name', 'pubg_match_id'),)
        indexes = [
            models.Index(fields=['pubg_match_id'], name='pubg_match_id_idx_ep'),
        ]

    player_name = models.CharField(max_length=10)
