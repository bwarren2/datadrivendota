from django.db import models


class Team(models.Model):
    """Pro team data"""
    steam_id = models.IntegerField()


class TeamDossier(models.Model):
    team = models.OneToOneField('Team')
    name = models.CharField(max_length=200, null=True)
    tag = models.CharField(max_length=200, null=True)
    created = models.IntegerField(null=True)
    rating = models.CharField(max_length=50, null=True)
    logo = models.BigIntegerField(null=True)
    logo_sponsor = models.BigIntegerField(null=True)
    country_code = models.CharField(max_length=10, null=True)
    url = models.CharField(max_length=200, null=True)
    games_played_with_current_roster = models.IntegerField()
    player_0 = models.ForeignKey(
        'players.Player', related_name='player_0', null=True
        )
    player_1 = models.ForeignKey(
        'players.Player', related_name='player_1', null=True
        )
    player_2 = models.ForeignKey(
        'players.Player', related_name='player_2', null=True
        )
    player_3 = models.ForeignKey(
        'players.Player', related_name='player_3', null=True
        )
    player_4 = models.ForeignKey(
        'players.Player', related_name='player_4', null=True
        )
    admin = models.ForeignKey(
        'players.Player', related_name='team_admin', null=True
        )
    leagues = models.ManyToManyField('leagues.League')
    logo_image = models.ImageField(null=True, upload_to='teams/img/')
    logo_sponsor_image = models.ImageField(null=True, upload_to='teams/img/')
