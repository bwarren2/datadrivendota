from uuid import uuid4
from datetime import timedelta

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.functional import cached_property
from django.conf import settings

from players.validators import validate_32bit

from djstripe.models import Customer
from djstripe.utils import subscriber_has_active_subscription


def get_active_users(since=timedelta(days=14)):
    then = timezone.now() - since
    return User.objects.filter(
        last_login__gte=then,
    ).exclude(
        last_login__isnull=True,
    )


def get_inactive_users(since=timedelta(days=14)):
    then = timezone.now() - since
    return User.objects.exclude(
        last_login__gt=then,
    ).exclude(
        last_login__isnull=True,
    )


def get_customer_player_ids():
    customers = Customer.objects.active()
    ids = list(
        UserProfile.objects.filter(
            user__customer__in=customers
        ).exclude(steam_id=None).values_list('steam_id', flat=True)
    )
    ids.extend(settings.TESTERS)
    # Tech debt: hardcode our testers as though they are subscribers.
    return ids


def get_active_user_player_ids(since=timedelta(days=14)):
    steam_ids = []
    for user in get_active_users():
        try:
            id = user.userprofile.steam_id
            if id is not None:
                steam_ids.append(id)
        except AttributeError:
                pass
    return steam_ids


def get_relevant_player_ids():
    lst = get_active_user_player_ids()
    lst.extend(get_customer_player_ids())
    return lst


def get_code():
    """ Get a uuid code. """
    return str(uuid4())


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    steam_id = models.BigIntegerField(
        help_text="The steam id to pull for this user.  Like for players.",
        validators=[validate_32bit],
        null=True
    )
    requested = models.ManyToManyField(
        'parserpipe.MatchRequest',
        related_name='requesters'
    )
    request_limit = models.IntegerField(default=10)
    public = models.BooleanField(default=True)

    @property
    def big_steam_id(self):
        return self.steam_id + settings.ADDER_32_BIT

    def __unicode__(self):
        return "User:{0}, Player id: {1}".format(
            unicode(self.user),
            unicode(self.steam_id)
        )

    def save(self, *args, **kwargs):
        if self.steam_id is not None:
            self.steam_id = self.steam_id % settings.ADDER_32_BIT
        super(UserProfile, self).save(*args, **kwargs)

    @cached_property
    def has_active_subscription(self):
        return subscriber_has_active_subscription(self.user)

    def monthly_requests(self, year=None, month=None):
        if year is None or month is None:
            now = timezone.now()
            year = now.year
            month = now.month
        return self.requested.filter(
            creation__year=year,
            creation__month=month,
        )

    @cached_property
    def requests_remaining(self):
        start_of_this_calendar_month = timezone.now().replace(
            day=1,
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )

        return self.request_limit - self.requested.filter(
            creation__gte=start_of_this_calendar_month
        ).count()

    @property
    def allowed_to_request(self):
        return self.requests_remaining > 0 or self.has_active_subscription


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
