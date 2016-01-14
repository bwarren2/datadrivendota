from django.templatetags.static import static
from django.db import models


class Item(models.Model):
    steam_id = models.IntegerField(
        help_text="Valve's normalization id",
        unique=True
    )
    thumbshot = models.ImageField(upload_to='items/img/')
    mugshot = models.ImageField(upload_to='items/img/')
    name = models.CharField(
        max_length=100,
        help_text='The name for people'
    )
    internal_name = models.CharField(
        max_length=100,
        help_text='The underscore name'
    )
    slug_name = models.CharField(max_length=100)
    quality = models.CharField(
        max_length=100,
        help_text='Internal shop category name'
    )
    cost = models.IntegerField(default=0, null=True)
    description = models.TextField(null=True)
    notes = models.TextField(null=True)
    mana_cost = models.IntegerField(null=True)
    cooldown = models.IntegerField(null=True)
    lore = models.TextField(null=True)
    created = models.NullBooleanField()

    @property
    def thumbshot_url(self):
        try:
            return self.thumbshot.url
        except ValueError:
            return static('blanks/blank_item_small.png')

    @property
    def mugshot_url(self):
        try:
            return self.mugshot.url
        except ValueError:
            return static('blanks/blank_item.png')

    def __unicode__(self):
        return self.internal_name


class ItemAttributes(models.Model):
    item = models.ForeignKey('Item')
    attribute = models.CharField(max_length=100)


class ItemComponents(models.Model):
    product = models.ForeignKey('Item', related_name='product')
    ingredient = models.ForeignKey('Item', related_name='ingredients')
