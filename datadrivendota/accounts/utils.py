from datetime import timedelta

from django.utils import timezone
from django.contrib.auth.models import User


def get_active_users(since=timedelta(days=30)):
    return User.objects.filter(
        last_login__gte=timezone.now() - since,
    )
