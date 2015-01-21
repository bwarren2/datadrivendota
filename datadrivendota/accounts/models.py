from uuid import uuid4
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User, Group
import datetime
from django.conf import settings
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from utils.exceptions import DataCapReached, ValidationException


def get_code():
    return str(uuid4())


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    player = models.OneToOneField('players.Player')
    following = models.ManyToManyField('players.Player', related_name='quarry')
    tracking = models.ManyToManyField('players.Player', related_name='feed')
    track_limit = models.IntegerField(default=7)
    requested = models.ManyToManyField('MatchRequest', null=True)
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

            #Is the user allowed to do this?
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


class Applicant(models.Model):
    steam_id = models.BigIntegerField(
        # help_text="Valve's internal map",
    )
    email = models.EmailField()
    interested_in_premium = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # That magic number is the valve 32bit -64bit adder.
        # Steam ids are 32 bit by convention.
        self.steam_id = self.steam_id % settings.ADDER_32_BIT
        super(Applicant, self).save(*args, **kwargs)

    def __unicode__(self):
        return "{0}, {1}".format(self.steam_id, self.email)


class PermissionCode(models.Model):

    LOOK = 1
    TOUCH = 2
    CHOICES = (
        (LOOK, 'User can see public parts of the site'),
        (TOUCH, 'User can use the private parts of the site'),
    )

    date_created = models.DateTimeField(default=datetime.datetime.now)
    key = models.CharField(max_length=40, default=get_code)
    registrant = models.ForeignKey(User, null=True)
    upgrade_type = models.IntegerField(choices=CHOICES)

    class Meta:
        permissions = (
            ("can_look", "Can see/use public things"),
            ("can_touch", "Can use private tools"),
        )

    def is_valid(self):
        date_rightness = (
            datetime.datetime.now()
            < (
                self.date_created.replace(tzinfo=None)
                + datetime.timedelta(days=settings.VALID_KEY_DAYS)
            )
        )
        return date_rightness and self.registrant is None

    def send_to(self, to_address):
        subject = 'Datadrivendota upgrade code'
        # @todo: Should really use a template.
        # --kit 2014-02-16
        message = """
        You are invited to the private beta at DataDrivenDota!

        You can redeem the key (below) at {url} after signing into your steam
        account.

        {key}

        """.format(
            key=self.key,
            url="http://{site}.com{path}".format(
                site=settings.SITE_NAME,
                path=reverse('upgrade')
            )
        )

        from_address = 'ben@datadrivendota.com'
        return send_mail(
            subject,
            message,
            from_address,
            [to_address],
            fail_silently=False
        )

    def associate(self, user_id):
        if self.is_valid():
            if self.needs_upgrade(user_id):
                user = User.objects.get(id=user_id)

                if self.upgrade_type == self.LOOK:
                    g = Group.objects.get_or_create(name='look')[0]
                    g.user_set.add(user)

                elif self.upgrade_type == self.TOUCH:
                    g = Group.objects.get_or_create(name='touch')[0]
                    g.user_set.add(user)
                    g = Group.objects.get_or_create(name='look')[0]
                    g.user_set.add(user)
                else:
                    raise Exception(
                        "What is this upgrade type? {up} ".format(
                            up=self.upgrade_type
                        )
                    )

                self.registrant = user
                self.save()
                return True
            else:
                return False
        else:
            return False

    def needs_upgrade(self, user_id):
        user = User.objects.get(id=user_id)
        if user.has_perm('players.can_touch'):
            return False
        if (
                user.has_perm('players.can_look')
                and self.upgrade_type == self.LOOK
                ):
            return False
        return True


class PollResponse(models.Model):
    steam_id = models.BigIntegerField(
        # help_text="Valve's internal map",
    )
    interested_in_premium = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # That magic number is the valve 32bit -64bit adder.
        # Steam ids are 32 bit by convention.
        self.steam_id = self.steam_id % settings.ADDER_32_BIT
        super(PollResponse, self).save(*args, **kwargs)

    def __unicode__(self):
        return "{0}, {1}".format(self.steam_id, self.interested_in_premium)


def request_to_player(request):
    return request.user.userprofile.player


def get_tracks(users):
    tracked = []
    for user in users:
        try:
            track_list = user.userprofile.tracking.all()
            for track in track_list:
                tracked.append(track)
        except ObjectDoesNotExist:
            pass
    return tracked
