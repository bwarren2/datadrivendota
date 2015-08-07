from django.test import TestCase, Client
from model_mommy import mommy
from django.core.urlresolvers import reverse


class TestUrlconf(TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestUrlconf, cls).setUpClass()
        cls.match = mommy.make_recipe('matches.match')

    def test_url_ok(self):
        c = Client()

        resp = c.get(reverse('matches:index'))
        self.assertEqual(resp.status_code, 200)

        resp = c.get(
            reverse(
                'matches:detail',
                kwargs={'match_id': self.match.steam_id}
            )
        )
        self.assertEqual(resp.status_code, 200)

        resp = c.get(
            reverse(
                'matches:detail',
                kwargs={'match_id': -1}
            )
        )
        self.assertEqual(resp.status_code, 404)
