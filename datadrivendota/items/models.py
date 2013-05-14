from django.db import models


# Create your models here.
class Item(models.Model):
    steam_id = models.IntegerField(help_text="Valve's normalization id", unique=True)
    internal_name = models.CharField(max_length=100,
                                     help_text='The underscore name')
    image = models.ImageField(upload_to='items/img/')
    description = models.TextField()
    lore = models.TextField()
    external_name = models.CharField(max_length=50)
    slug_name = models.CharField(max_length=100)

    def __unicode__(self):
        return self.internal_name
