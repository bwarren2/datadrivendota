import re
from datetime import timedelta

from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.core import mail
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


class TestAuth(TestCase):

    def test_login_200(self):
        c = Client()
        resp = c.get('/accounts/login/')
        self.assertEqual(resp.status_code, 200)

    def test_login_flow(self):

        email = "baz@gmail"
        username = email
        password = "bar"

        c = Client()
        login_url = reverse("social:complete", args={"email"})

        # Post to the "log me in plz" address
        resp = c.post(login_url, {'email': email, 'password': password})
        self.assertEqual(resp.status_code, 302)

        # Social auth should try to send an email
        psa_email = mail.outbox[0]

        regex = re.compile(r'http://.*')
        verification_url = regex.search(psa_email.body).group()

        # Hit the verification address
        resp = c.get(verification_url, follow=True)

        # Expect to be logged in
        self.assertEqual(
            resp.context['request'].user.username,
            username
        )

        resp = c.get(reverse('logout'), follow=True)

        # Expect to be logged out
        self.assertEqual(
            resp.context['request'].user.is_anonymous(),
            True
        )

        # Try to log back in
        resp = c.post(
            login_url,
            {'email': email, 'password': password},
            follow=True
        )

        # Expect to log in without needing to reconfirm
        self.assertEqual(
            resp.context['request'].user.username,
            username
        )

        # Logout to set up next step.
        resp = c.get(reverse('logout'), follow=True)

        # Someone else tries to log into that account
        resp = c.post(
            login_url,
            {'email': email, 'password': 'wrongpassword'},
            follow=True
        )

        # Expect to fail b/c password.
        # Should probably test for the "Wrong pass" msg.
        self.assertEqual(
            resp.context['request'].user.is_anonymous(),
            True
        )
        self.assertEqual(
            resp.request['PATH_INFO'],
            '/login/'
        )


