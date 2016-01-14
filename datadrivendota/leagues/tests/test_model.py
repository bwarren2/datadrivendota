from datetime import timedelta

from django.templatetags.static import static
from django.test import TestCase
from django.utils import timezone

from model_mommy import mommy
from utils.file_management import fake_image


class TestModelMethods(TestCase):

    def setUp(self):
        self.league = mommy.make_recipe('leagues.league')

    def test_update_save(self):
        self.league.save()
        self.assertLess(
            timezone.now() - self.league.update_time,
            timedelta(seconds=.1)
        )

    def test_outdated(self):
        self.league.update_time = timezone.now() - timedelta(weeks=10)
        self.league.stored_image = None
        self.assertEqual(self.league.is_outdated, True)

        self.league = fake_image(self.league)
        self.league.update_time = timezone.now() - timedelta(weeks=10)
        self.assertEqual(self.league.is_outdated, False)

        self.league.update_time = timezone.now()
        self.league.stored_image = None
        self.assertEqual(self.league.is_outdated, False)

        self.league.update_time = timezone.now()
        self.league = fake_image(self.league)
        self.assertEqual(self.league.is_outdated, False)

    def test_image(self):

        l = mommy.make('leagues.league', stored_image=None)
        self.assertEqual(l.image, static('blanks/blank_league.png'))
        l.delete()

        l = mommy.make('leagues.league')
        l = fake_image(l)
        self.assertNotEqual(l.image, static('blanks/blank_league.png'))
        l.delete()

        l = mommy.make('leagues.league', stored_image=None, image_failed=True)
        l = fake_image(l)
        self.assertEqual(l.image, static('blanks/blank_league.png'))
        l.delete()
