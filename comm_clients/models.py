from django.db import models


class CommChannels(models.Model):

    class Meta:
        db_table = 'comm_channels'

    comm_type = models.CharField(max_length=64)
    address_info = models.CharField(max_length=255, unique=True)


class UserCommPrefs(models.Model):

    class Meta:
        db_table = 'user_comm_prefs'

    pubg_user = models.ForeignKey('game_data.User')
    comm_channel = models.ForeignKey(CommChannels)
