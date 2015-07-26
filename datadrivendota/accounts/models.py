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

    SUBMITTED = 0
    REPLAY_AVAILABLE = 1
    REPLAY_NOT_AVAILABLE = 2
    PARSED = 3
    COMPLETE = 4
    MATCH_NOT_FOUND = 5
    FINDING_MATCH = 6
    MATCH_FOUND = 7

    STATUS_CHOICES = (
        (SUBMITTED, 'Submitted'),
        (FINDING_MATCH, 'Finding Match'),
        (MATCH_NOT_FOUND, 'Match Not Found'),
        (MATCH_FOUND, 'Match Found'),
        (REPLAY_AVAILABLE, 'Replay Available'),
        (REPLAY_NOT_AVAILABLE, 'Replay Not Available'),
        (PARSED, 'Parsed'),
        (COMPLETE, 'Complete'),
    )

    # The core components we care about
    status = models.PositiveIntegerField(
        choices=STATUS_CHOICES, default=SUBMITTED
    )
    match_id = models.PositiveIntegerField(unique=True)
    requester = models.ForeignKey(User)

    # Intermediate step fields if we want em.
    valve_replay_url = models.URLField(blank=True, null=True)
    raw_parse_url = models.URLField(blank=True, null=True)
    replay_file_url = models.URLField(blank=True, null=True)

    # Tracking fields, doing their own thing
    creation = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        super(MatchRequest, self).save(*args, **kwargs)

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

    def __unicode__(self):
        choices = self.STATUS_CHOICES
        return "Match Request: match#: {0}, status: {1}".format(
            self.match_id, dict(choices).get(self.status)
        )

    @property
    def file_url(self):
        return (
            "https://s3.amazonaws.com/datadrivendota/"
            "raw_replay_parse/{0}"
        ).format(self.raw_parse_url)
