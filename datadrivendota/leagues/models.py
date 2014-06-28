from django.db import models
from .managers import SortedLeagueManager


class League(models.Model):
    """Analogous to a tournament, these are game series to which you can buy a ticket in the game client"""
    steam_id = models.IntegerField(unique=True)

    objects = models.Manager()
    recency = SortedLeagueManager()


class LeagueDossier(models.Model):
    league = models.OneToOneField('League')
    name = models.CharField(max_length=200)  # Made up constant
    description = models.CharField(max_length=300)  # Made up constant
    tournament_url = models.CharField(max_length=300)
    item_def = models.IntegerField()
    logo_image = models.ImageField(upload_to='leagues/img/', null=True)

    @property
    def display_name(self):
        str = self.name.replace('#DOTA_Item_League_', '')
        str = str.replace('#DOTA_Item_', '').replace('_', ' ')
        return str

    @property
    def display_description(self):
        str = self.description.replace('#DOTA_Item_League_', '')
        str = str.replace('#DOTA_Item_Desc_', '').replace('_', ' ')
        str = str.replace('#DOTA_Item_', '').replace('_', ' ')
        return str

    def __unicode__(self):
        return self.name
