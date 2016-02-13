from django.db import models


class Guild(models.Model):
    steam_id = models.BigIntegerField(unique=True)
    name = models.CharField(max_length=50)
    logo = models.BigIntegerField()
