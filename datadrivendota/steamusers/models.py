from django.db import models


# Create your models here.
class SteamUser(models.Model):
    steam_id = models.BigIntegerField(help_text="Valve's internal map", unique=True)

    def is_masked(self):
        return self.steamid == 4294967295

    def __unicode__(self):
        return unicode(self.steam_id)
