from django.db import models
from .managers import SortedTeamManager, TI4TeamManager, TI4DossManager


class Team(models.Model):
    """Pro team data"""
    steam_id = models.IntegerField(unique=True)
    objects = models.Manager()
    sorted = SortedTeamManager()
    TI4 = TI4TeamManager()


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

    objects = models.Manager()
    TI4 = TI4DossManager()


def assemble_pros(teams):
    lst = []
    subset = teams.exclude(player_0=None).values('player_0__steam_id')
    addition = [t['player_0__steam_id'] for t in subset]
    lst.extend(addition)

    subset = teams.exclude(player_1=None).values('player_1__steam_id')
    addition = [t['player_1__steam_id'] for t in subset]
    lst.extend(addition)

    subset = teams.exclude(player_2=None).values('player_2__steam_id')
    addition = [t['player_2__steam_id'] for t in subset]
    lst.extend(addition)

    subset = teams.exclude(player_3=None).values('player_3__steam_id')
    addition = [t['player_3__steam_id'] for t in subset]
    lst.extend(addition)

    subset = teams.exclude(player_4=None).values('player_4__steam_id')
    addition = [t['player_4__steam_id'] for t in subset]
    lst.extend(addition)

    subset = teams.exclude(admin=None).values('admin__steam_id')
    addition = [t['admin__steam_id'] for t in subset]
    lst.extend(addition)
    return lst
