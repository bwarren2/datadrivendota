import re
from datetime import timedelta

import responses

from django.test import TestCase, Client
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.core import mail
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator

from model_mommy import mommy

from .models import (
    MatchRequest,
    get_active_users,
    get_inactive_users,
)
from .management.tasks import KickoffMatchRequests, CreateMatchParse
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


class TestKickoffRequestTask(TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestKickoffRequestTask, cls).setUpClass()
        mommy.make(
            'accounts.MatchRequest',
            status=MatchRequest.SUBMITTED,
            _quantity=2
        )
        mommy.make(
            'accounts.MatchRequest',
            status=MatchRequest.FINDING_MATCH,
        )
        mommy.make(
            'accounts.MatchRequest',
            status=MatchRequest.MATCH_FOUND,
        )
        mommy.make(
            'accounts.MatchRequest',
            status=MatchRequest.MATCH_FOUND,
        )
        mommy.make(
            'accounts.MatchRequest',
            status=MatchRequest.COMPLETE,
        )

    def test_get_requests(self):

        # Test only pushing submitted requests
        self.assertQuerysetEqual(
            MatchRequest.objects.filter(
                status=MatchRequest.SUBMITTED
            ).order_by('id'),
            map(repr, KickoffMatchRequests().get_requests(True).order_by('id'))
        )

        # Test when we want to force along everything, not just submitted
        self.assertQuerysetEqual(
            MatchRequest.objects.filter(
                Q(status=MatchRequest.SUBMITTED) |
                Q(status=MatchRequest.FINDING_MATCH) |
                Q(status=MatchRequest.MATCH_FOUND)
            ).order_by('id'),
            map(repr, KickoffMatchRequests().get_requests(
                False
            ).order_by('id'))
        )

    def test_marked(self):
        requests = KickoffMatchRequests().get_requests(True)
        for request in requests:
            KickoffMatchRequests().mark_finding(request)
            self.assertEqual(request.status, MatchRequest.FINDING_MATCH)


class TestParserTask(TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestParserTask, cls).setUpClass()
        cls.match_id = 1615448703
        cls.match = mommy.make(
            'matches.Match',
            steam_id=cls.match_id
        )
        cls.match_request = mommy.make(
            'accounts.MatchRequest',
            match_id=cls.match_id,
            status=MatchRequest.FINDING_MATCH
        )

    def test_match_check(self):
        task = CreateMatchParse()
        self.assertEqual(
            task.have_match(self.match.steam_id),
            self.match_request
        )

    @method_decorator(responses.activate)
    def test_get_url(self):
        responses.add(
            responses.GET,
            'https://replayurls.herokuapp.com/tools/matchurls?match_id=1615448703',
             body='{"replay_url": "http://replay121.valve.net/570/1615448703_975041684.dem.bz2"}',
            status=200,
            content_type='application/json',
            match_querystring=True,
        )

        task = CreateMatchParse()
        match_req = task.have_match(self.match.steam_id)
        task.get_replay_url(self.match.steam_id, match_req)
        mr = MatchRequest.objects.get(match_id=self.match_id)
        self.assertNotEqual(mr.valve_replay_url, None)


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
