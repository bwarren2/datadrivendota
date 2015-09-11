from django.test import TestCase
from model_mommy import mommy
from django.utils import timezone
from datetime import timedelta


class TestLiveMatch(TestCase):

    def test_live_match_ready(self):
        lm = mommy.make('leagues.livematch', )
        lm.created_at = timezone.now() - timedelta(days=1000)
        self.assertEqual(lm.ready, True)

        lm = mommy.make('leagues.livematch', )
        lm.created_at = timezone.now()
        self.assertEqual(lm.ready, False)
