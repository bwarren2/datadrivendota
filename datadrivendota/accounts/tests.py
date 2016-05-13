from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model

from model_mommy import mommy

from .models import (
    get_active_users,
    get_inactive_users,
)
User = get_user_model()


class TestActiveAccounts(TestCase):
    def test_active_and_inactive(self):
        now = timezone.now()
        then = now - timedelta(days=15)
        inactive_user = mommy.make(
            User,
            last_login=then,
            username="inactive",
        )
        active_user = mommy.make(
            User,
            last_login=now,
            username="active",
        )
        mommy.make(
            User,
            last_login=None,
            username="null",
        )
        self.assertEqual(
            [inactive_user],
            list(get_inactive_users())
        )
        self.assertEqual(
            [active_user],
            list(get_active_users())
        )
