from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.contrib.auth.models import User, Group
from .validators import validate_32bit
from settings.base import ADDER_32_BIT, ANONYMOUS_ID
import datetime
from django.conf import settings
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from uuid import uuid4
from utils.exceptions import DataCapReached, ValidationException

from .managers import TI4Manager


def get_code():
    return str(uuid4())


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
            return self.pro_name
        else:
            return self.persona_name

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


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    player = models.OneToOneField('Player')
    following = models.ManyToManyField('Player', related_name='quarry')
    tracking = models.ManyToManyField('Player', related_name='feed')
    track_limit = models.IntegerField(default=7)
    requested = models.ManyToManyField('MatchRequest', null=True)
    request_limit = models.IntegerField(default=10)

    def add_tracking(self, player):
        if self.tracking.count() >= int(self.track_limit):
            return False
        else:
            self.tracking.add(player)
            self.track_limit += 1
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

    def save(self, *args, **kwargs):
        # That magic number is the valve 32bit -64bit adder.
        # Steam ids are 32 bit by convention.
        self.steam_id = self.steam_id % ADDER_32_BIT
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
