from django.db import models

# Create your models here.
class Guild(models.Model):
    steam_id = models.IntegerField()
    name = models.CharField(max_length=50)
    logo = models.BigIntegerField()
