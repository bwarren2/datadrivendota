from uuid import uuid4
from django.db import models
from django.contrib.auth.models import User
from utils.exceptions import DataCapReached, ValidationException


def get_code():
    """ Get a uuid code. """
    return str(uuid4())


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    player = models.OneToOneField('players.Player')
    following = models.ManyToManyField('players.Player', related_name='quarry')
    tracking = models.ManyToManyField('players.Player', related_name='feed')
    track_limit = models.IntegerField(default=7)
    requested = models.ManyToManyField('MatchRequest')
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


class MatchRequest(models.Model):
    match_id = models.IntegerField(unique=True)

    @staticmethod
    def create_for_user(user, match_id):
        try:
            profile = UserProfile.objects.get(user=user)

            # Is the user allowed to do this?
            if profile.requested is None \
                    or profile.request_limit > profile.requested.count():
                if MatchRequest.objects.filter(
                    match_id=match_id
                ).count() == 0:
                    obj = MatchRequest.objects.create(match_id=match_id)
                    profile.requested.add(obj)
                    return obj
                else:
                    msg = "We already have that, no request needed."
                    raise ValidationException(msg)
            else:
                raise DataCapReached
        except UserProfile.DoesNotExist:
            msg = "You don't seem to be logged in, which is required."
            raise ValidationException(msg)
