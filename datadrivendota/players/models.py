from django.db import models
from .validators import validate_32bit
from settings.base import ADDER_32_BIT, ANONYMOUS_ID
from uuid import uuid4
from django.utils.encoding import smart_str

from .managers import TI4Manager


class Player(models.Model):
    steam_id = models.BigIntegerField(
        help_text="Valve's internal map",
        unique=True,
        validators=[validate_32bit],
        db_index=True
    )
    persona_name = models.TextField(help_text='Your name on steam')
    profile_url = models.TextField(help_text='Steam profile URL')
    avatar = models.TextField(help_text='Tiny avatar image url')
    avatar_medium = models.TextField(help_text='Medium avatar image url')
    avatar_full = models.TextField(help_text="Big avatar image url")
    pro_name = models.TextField(
        help_text='If this is a pro, what are they known as?',
        null=True
    )
    updated = models.BooleanField(
        help_text='Do we update this person and scrape them?',
        default=False)
    last_scrape_time = models.IntegerField(
        help_text='Unix time of last match scrape start',
        default=0
    )

    objects = models.Manager()
    TI4 = TI4Manager()

    @property
    def display_name(self):

        if self.pro_name is not None:
            return smart_str(self.pro_name)
        else:
            return smart_str(self.persona_name)

    def save(self, *args, **kwargs):
        # That magic number is the valve 32bit -64bit adder.
        # Steam ids are 32 bit by convention.
        self.steam_id = self.steam_id % ADDER_32_BIT
        super(Player, self).save(*args, **kwargs)

    def is_masked(self):
        #That's the magic number for anonymous data
        return self.steam_id == ANONYMOUS_ID

    def get_64_bit_id(self):
        return self.steam_id + ADDER_32_BIT

    def get_32_bit_id(self):
        return self.steam_id % ADDER_32_BIT

    def __unicode__(self):
        return unicode(self.steam_id)
