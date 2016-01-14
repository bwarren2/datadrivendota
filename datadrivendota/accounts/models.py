from uuid import uuid4
from datetime import timedelta

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


def get_active_users():
    two_weeks_ago = timezone.now() - timedelta(days=14)
    return User.objects.filter(
        last_login__gte=two_weeks_ago
    ).exclude(
        last_login__isnull=True
    )


def get_inactive_users():
    two_weeks_ago = timezone.now() - timedelta(days=14)
    return User.objects.exclude(
        last_login__gt=two_weeks_ago
    ).exclude(
        last_login__isnull=True
    )


def get_code():
    """ Get a uuid code. """
    return str(uuid4())


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    player = models.OneToOneField('players.Player')
    following = models.ManyToManyField('players.Player', related_name='quarry')
    tracking = models.ManyToManyField('players.Player', related_name='feed')
    track_limit = models.IntegerField(default=7)
    requested = models.ManyToManyField(
        'parserpipe.MatchRequest',
        related_name='requesters'
    )
    request_limit = models.IntegerField(default=10)

    def add_tracking(self, player):
        if self.tracking.count() >= int(self.track_limit):
            return False
        else:
            self.tracking.add(player)
            self.save()
            return True

    def __unicode__(self):
        return "User:{0}, Player{1}".format(
            unicode(self.user),
            unicode(self.player)
        )


class PingRequest(models.Model):

    email = models.EmailField()
    recurring = models.BooleanField()
    created = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __unicode__(self):
        if self.recurring:
            return "{0} at {1}, recurring".format(
                unicode(self.email),
                unicode(self.created)
            )
        else:
            return "{0} at {1}".format(
                unicode(self.email),
                unicode(self.created)
            )
