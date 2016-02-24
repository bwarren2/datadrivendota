from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from accounts.exceptions import DataCapReached, ValidationException
from accounts.models import UserProfile
# Create your models here.


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
    match_id = models.BigIntegerField(unique=True)
    requester = models.ForeignKey(User, null=True)

    # Intermediate step fields if we want em.
    valve_replay_url = models.URLField(blank=True, null=True)
    raw_parse_url = models.TextField(blank=True, null=True)

    # Tracking fields, doing their own thing
    creation = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    @staticmethod
    def create_for_user(user, match_id):
        try:
            profile = UserProfile.objects.get(user=user)

            # Is the user allowed to do this?
            start_of_this_calendar_month = timezone.now().replace(
                day=1,
                hour=0,
                minute=0,
                second=0,
                microsecond=0,
            )
            allowed_to_request = (
                profile.requested is not None and
                profile.request_limit > profile.requested.filter(
                    created__gte=start_of_this_calendar_month,
                ).count()
            )
            if allowed_to_request:
                if not MatchRequest.objects.filter(match_id=match_id).exists():
                    obj = MatchRequest.objects.create(match_id=match_id)
                    profile.requested.add(obj)
                    return obj
                else:
                    raise ValidationException(
                        "We already have that, no request needed.",
                    )
            else:
                raise DataCapReached
        except UserProfile.DoesNotExist:
            raise ValidationException(
                "You don't seem to be logged in, which is required.",
            )

    def __unicode__(self):
        choices = self.STATUS_CHOICES
        return "Match#: {0}, status: {1}".format(
            self.match_id, dict(choices).get(self.status)
        )

    @property
    def file_url(self):
        return (
            "https://s3.amazonaws.com/datadrivendota/"
            "raw_replay_parse/{0}"
        ).format(self.raw_parse_url)
