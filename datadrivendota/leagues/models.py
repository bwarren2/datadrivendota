from django.db import models

# Create your models here.


class League(models.Model):
    """Analogous to a tournament, these are game series to which you can buy a ticket in the game client"""
    steam_id = models.IntegerField()


class LeagueDossier(models.Model):
    league = models.OneToOneField('League')
    name = models.CharField(max_length=200)  # Made up constant
    description = models.CharField(max_length=300)  # Made up constant
    tournament_url = models.CharField(max_length=300)
    item_def = models.IntegerField()

    def __unicode__(self):
        return self.name
