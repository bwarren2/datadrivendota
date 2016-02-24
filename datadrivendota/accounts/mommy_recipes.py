from model_mommy.recipe import Recipe, seq
from .models import UserProfile
from model_mommy import mommy
from django.contrib.auth.models import User
from djstripe.models import CurrentSubscription
from django.utils import timezone
from datetime import timedelta


userprofile = Recipe(
    UserProfile,
    steam_id=seq(1),
)


def make_user(username, email, steam_id=None, active=True):
    # We need to use an actual user instance for model_mommy
    if active:
        last_login = timezone.now()
    else:
        last_login = timezone.now() - timedelta(weeks=4)

    user = User.objects.create(
        username=username, email=email, last_login=last_login
    )
    mommy.make_recipe(
        'accounts.userprofile', user=user, steam_id=steam_id
    )
    return user


def make_customer(user):
    # We need to use an actual user instance for model_mommy
    customer = mommy.make(
        'djstripe.customer',
        subscriber=user,
    )
    mommy.make(
        'djstripe.CurrentSubscription',
        status=CurrentSubscription.STATUS_ACTIVE,
        customer=customer
    )
    return customer


def make_full_customer(username, email, steam_id):
    # Initializing a real customer in one place, isolating this hacky stuff
    user = make_user('steve', 'steve@gmail.com', steam_id)
    make_customer(user)
    return user
